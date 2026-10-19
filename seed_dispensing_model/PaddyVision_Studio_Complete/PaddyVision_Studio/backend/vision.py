"""Checkpoint-compatible inference adapters for three trained segmenters.

Models are sequentially moved to the requested device, avoiding three-way
GPU-residency on a 6GB laptop GPU. Ensemble averages aligned per-class softmax
probabilities; it is an optional comparative experiment, not a validated model.
"""
from __future__ import annotations

import io
import threading
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from .config import (DEVICE_PREFERENCE, LABELS, MAX_IMAGE_PIXELS,
                     MAX_UPLOAD_BYTES, MODEL_BY_ID, MODELS, MODEL_INPUT_BASELINE)

Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
_LOCK = threading.RLock()


def decode_image(data: bytes) -> Image.Image:
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ValueError('Upload an image smaller than 15 MB.')
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.load()
            if im.width * im.height > MAX_IMAGE_PIXELS:
                raise ValueError('Image exceeds 12 million pixels.')
            return ImageOps.exif_transpose(im).convert('RGB')
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError('Invalid or unsupported image file.') from exc


def _torch_device():
    import torch
    if DEVICE_PREFERENCE == 'cpu':
        return torch.device('cpu')
    if DEVICE_PREFERENCE == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('PADDYVISION_DEVICE=cuda, but CUDA is not available.')
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def _checkpoint(spec):
    import torch
    if not spec.checkpoint.is_file():
        raise FileNotFoundError(f'Checkpoint not found: {spec.checkpoint}')
    # Only open the user's own locally trained, trusted .pt checkpoints.
    try:
        ckpt = torch.load(spec.checkpoint, map_location='cpu', weights_only=False)
    except Exception as exc:
        raise RuntimeError(f'Cannot open checkpoint {spec.checkpoint.name}: {exc}') from exc
    if not isinstance(ckpt, dict):
        raise ValueError('Checkpoint must contain a state dictionary.')
    state = ckpt.get('model_state_dict', ckpt.get('state_dict'))
    if state is None and ckpt and all(isinstance(k, str) for k in ckpt):
        state = ckpt   # support raw state_dict checkpoints
    if not isinstance(state, dict):
        raise ValueError('Checkpoint missing model_state_dict.')
    if 'labels' in ckpt and tuple(ckpt['labels']) != LABELS:
        raise ValueError('Checkpoint label ordering does not match Existing plants, Soil, Weeds.')
    if 'classes' in ckpt:
        classes = ckpt['classes']
        if isinstance(classes, dict):
            ordered = tuple(classes.get(i, classes.get(str(i))) for i in range(3))
            if ordered != LABELS:
                raise ValueError(f'Unexpected SegFormer label ordering: {ordered}')
    return ckpt, state


def _build(spec, ckpt):
    if spec.family == 'segformer':
        try:
            from transformers import SegformerConfig, SegformerForSemanticSegmentation
        except Exception as exc:
            raise RuntimeError('Install compatible transformers==4.46.3 (see requirements.txt).') from exc
        # nvidia/mit-b0 was an ImageNet encoder checkpoint. Segmentation head
        # used the standard B0 configuration and three output channels.
        # Construct locally, not from_pretrained: no internet required at inference.
        config = SegformerConfig(num_labels=3,
                                 id2label={i: label for i, label in enumerate(LABELS)},
                                 label2id={label: i for i, label in enumerate(LABELS)})
        model = SegformerForSemanticSegmentation(config)
        size = int(ckpt.get('image_size', MODEL_INPUT_BASELINE))
        mean = (0.485, 0.456, 0.406)
        std = (0.229, 0.224, 0.225)
    else:
        try:
            import segmentation_models_pytorch as smp
        except Exception as exc:
            raise RuntimeError('Install segmentation-models-pytorch==0.5.0 (see requirements.txt).') from exc
        encoder = str(ckpt.get('encoder', 'efficientnet-b4'))
        if encoder != 'efficientnet-b4':
            raise ValueError(f'Expected efficientnet-b4, got {encoder}')
        model = smp.DeepLabV3Plus(
            encoder_name=encoder, encoder_weights=None, encoder_output_stride=16,
            in_channels=3, classes=3, activation=None,
        )
        size = int(ckpt.get('input_size', 320))
        preprocessing = smp.encoders.get_preprocessing_params(encoder, pretrained='imagenet')
        mean = preprocessing['mean']
        std = preprocessing['std']
    return model, size, np.asarray(mean, dtype=np.float32), np.asarray(std, dtype=np.float32)


@dataclass
class Result:
    model_id: str
    probability: np.ndarray  # class x H x W, full original resolution
    seconds: float
    epoch: Optional[int]
    validation_miou: Optional[float]
    device: str


def predict_probs(spec_id: str, image: Image.Image) -> Result:
    import torch
    import torch.nn.functional as F
    spec = MODEL_BY_ID.get(spec_id)
    if spec is None:
        raise ValueError(f'Unknown model: {spec_id}')
    with _LOCK:
        start = time.perf_counter()
        device = _torch_device()
        ckpt, state = _checkpoint(spec)
        model = None
        try:
            model, size, mean, std = _build(spec, ckpt)
            try:
                model.load_state_dict(state, strict=True)
            except RuntimeError as exc:
                raise RuntimeError(f'Checkpoint/architecture mismatch for {spec.display_name}: {exc}') from exc
            model = model.to(device).eval()
            src = np.asarray(image.resize((size, size), Image.Resampling.BILINEAR), dtype=np.float32) / 255.0
            src = (src - mean) / std
            tensor = torch.from_numpy(src.transpose(2, 0, 1).copy()).unsqueeze(0).to(device)
            with torch.inference_mode():
                if spec.family == 'segformer':
                    logits = model(pixel_values=tensor).logits
                else:
                    logits = model(tensor)
                logits = F.interpolate(logits.float(), size=(image.height, image.width),
                                       mode='bilinear', align_corners=False)
                probs = torch.softmax(logits, dim=1)[0].float().cpu().numpy()
            del tensor, logits
            return Result(spec_id, probs, time.perf_counter() - start,
                          int(ckpt['epoch']) if 'epoch' in ckpt else None,
                          float(ckpt['best_val_miou']) if 'best_val_miou' in ckpt else None,
                          str(device))
        finally:
            if model is not None:
                model.to('cpu')
                del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


def available_model_ids() -> list[str]:
    return [m.id for m in MODELS if m.checkpoint.is_file()]


def ensemble_probability(results: list[Result]) -> np.ndarray:
    if len(results) < 2:
        raise ValueError('Ensemble needs at least two available trained checkpoints.')
    shapes = {result.probability.shape for result in results}
    if len(shapes) != 1:
        raise ValueError('Model probability dimensions do not match.')
    return np.mean(np.stack([r.probability for r in results], axis=0), axis=0)
