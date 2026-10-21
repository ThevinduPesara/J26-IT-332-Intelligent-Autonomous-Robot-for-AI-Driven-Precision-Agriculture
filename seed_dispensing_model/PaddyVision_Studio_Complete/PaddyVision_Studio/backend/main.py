"""PaddyVision Studio FastAPI service. Run with uvicorn backend.main:app."""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .config import PACKAGE_ROOT, PROJECT_ROOT, MODEL_BY_ID, MODELS, describe, LABELS, PALETTE, MAX_UPLOAD_BYTES
from .vision import decode_image, predict_probs, available_model_ids, ensemble_probability
from .visuals import make_views

log = logging.getLogger('paddyvision')
app = FastAPI(title='PaddyVision Studio API', description='Paddy-field semantic-segmentation inference. Local trusted checkpoints only.', version='1.0.0')
default_origins = [
    'http://localhost:3000', 'http://127.0.0.1:3000',
    'http://localhost:3001', 'http://127.0.0.1:3001',
    'http://localhost:3002', 'http://127.0.0.1:3002',
    'http://localhost:8501', 'http://127.0.0.1:8501',
]
configured_origins = os.environ.get('PADDYVISION_CORS_ORIGINS', '').split(',')
allowed_origins = default_origins + [origin.strip() for origin in configured_origins if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins,
                   allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['*'])


@app.get('/health')
def health():
    try:
        import torch
        cuda = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda else 'CPU'
    except Exception:
        cuda, device_name = False, 'PyTorch unavailable'
    return {'status': 'ok', 'service': 'PaddyVision Studio', 'project_root': str(PROJECT_ROOT),
            'device': device_name, 'cuda_available': cuda, 'available_models': len(available_model_ids())}


@app.get('/models')
def models():
    return {'models': [describe(s) for s in MODELS], 'labels': LABELS,
            'palette': PALETTE, 'ensemble_ready': len(available_model_ids()) >= 2}


@app.get('/benchmarks')
def benchmarks():
    files = {
        'segformer_base': PROJECT_ROOT / 'SegFormer_B0_results' / 'test_metrics.json',
        'segformer_group': PROJECT_ROOT / 'SegFormer_B0_GroupSplit_Fixed' / 'final_test_metrics.json',
        'deeplab_b4': PROJECT_ROOT / 'DeepLabV3Plus_EfficientNetB4_results' / 'final_test_metrics.json',
    }
    response = {}
    for model_id, path in files.items():
        if path.is_file():
            try:
                raw = json.loads(path.read_text(encoding='utf-8'))
                response[model_id] = {'mean_iou': raw.get('mean_iou', raw.get('miou')),
                                      'mean_dice': raw.get('mean_dice'),
                                      'pixel_accuracy': raw.get('pixel_accuracy'),
                                      'source': str(path)}
            except (ValueError, OSError) as exc:
                response[model_id] = {'error': str(exc)}
        else:
            response[model_id] = None
    return {'benchmarks': response,
            'note': 'Historic test metrics use different split/ignored-pixel policies; do not rank checkpoints without common evaluation.'}


def _safe_exception(exc: Exception):
    if isinstance(exc, (FileNotFoundError, ValueError)):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if isinstance(exc, RuntimeError):
        log.exception('Model inference failed')
        raise HTTPException(status_code=503, detail=str(exc)[:1500]) from exc
    log.exception('Unexpected inference error')
    raise HTTPException(status_code=500, detail=f'Inference failed: {type(exc).__name__}') from exc


async def _uploaded(file: UploadFile):
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail='File exceeds 15MB.')
    try:
        return decode_image(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post('/predict')
async def predict(file: UploadFile = File(...), model_id: str = Form('segformer_base'), alpha: float = Form(0.52)):
    if model_id not in MODEL_BY_ID and model_id != 'ensemble':
        raise HTTPException(status_code=422, detail='Unknown model selection.')
    if not 0 <= alpha <= 1:
        raise HTTPException(status_code=422, detail='alpha must be from 0 to 1')
    image = await _uploaded(file)
    try:
        if model_id == 'ensemble':
            selected = available_model_ids()
            results = [predict_probs(mid, image) for mid in selected]
            probs = ensemble_probability(results)
            data = make_views(image, probs, alpha)
            data.update({'model_id': model_id, 'model_name': 'Mean-probability ensemble',
                         'contributors': selected, 'inference_seconds': round(sum(r.seconds for r in results), 3),
                         'device': ', '.join(sorted({r.device for r in results}))})
        else:
            result = predict_probs(model_id, image)
            data = make_views(image, result.probability, alpha)
            data.update({'model_id': model_id, 'model_name': MODEL_BY_ID[model_id].display_name,
                         'contributors': [model_id], 'inference_seconds': round(result.seconds, 3),
                         'checkpoint_epoch': result.epoch, 'checkpoint_val_miou': result.validation_miou,
                         'device': result.device})
        return data
    except Exception as exc:
        _safe_exception(exc)


@app.post('/compare')
async def compare(file: UploadFile = File(...), alpha: float = Form(0.52)):
    image = await _uploaded(file)
    ids = available_model_ids()
    if len(ids) < 2:
        raise HTTPException(status_code=422, detail='Comparison needs at least two trained checkpoints.')
    try:
        results = [predict_probs(mid, image) for mid in ids]
        individual = []
        for r in results:
            view = make_views(image, r.probability, alpha)
            individual.append({'model_id': r.model_id, 'model_name': MODEL_BY_ID[r.model_id].display_name,
                               'inference_seconds': round(r.seconds, 3),
                               'checkpoint_epoch': r.epoch, 'checkpoint_val_miou': r.validation_miou,
                               **view})
        combined = make_views(image, ensemble_probability(results), alpha)
        combined.update({'model_id': 'ensemble', 'model_name': 'Mean-probability ensemble',
                         'contributors': ids, 'inference_seconds': round(sum(r.seconds for r in results), 3)})
        return {'models': individual, 'ensemble': combined,
                'note': 'Ensemble is unvalidated; confidence is not calibrated, and there is no ground-truth accuracy here.'}
    except Exception as exc:
        _safe_exception(exc)
