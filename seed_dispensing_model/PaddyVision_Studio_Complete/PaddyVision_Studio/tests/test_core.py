"""Run: python -m pytest -q (requires pytest, FastAPI extras and Pillow)."""
import io
import numpy as np
import pytest
from PIL import Image
from backend.config import LABELS, PALETTE, MODELS
from backend.visuals import make_views
from backend.vision import decode_image, ensemble_probability, Result


def test_three_models_registered():
    assert [m.id for m in MODELS] == ['segformer_base','segformer_group','deeplab_b4']
    assert LABELS == ('Existing plants', 'Soil', 'Weeds')


def test_image_decode_rgb_and_exif():
    b=io.BytesIO(); Image.new('RGB', (18,12), 'green').save(b, format='PNG')
    assert decode_image(b.getvalue()).size == (18,12)


def test_reject_nonimage():
    with pytest.raises(ValueError):
        decode_image(b'not really a photo')


def test_prediction_render_and_stats():
    image=Image.new('RGB',(4,2),'white')
    probs=np.zeros((3,2,4),dtype=np.float32)
    probs[0,:,:2]=1
    probs[1,:,2:3]=1
    probs[2,:,3:]=1
    view=make_views(image,probs,alpha=0.5)
    assert [s['percent'] for s in view['stats']] == [50.0,25.0,25.0]
    assert view['mean_confidence'] == 1.0
    assert set(view['images']) == {'original_png','overlay_png','mask_png','confidence_png'}


def test_ensemble_probabilities():
    p=np.zeros((3,2,2),dtype=np.float32)
    q=np.zeros_like(p)
    p[0,:,:]=1.0; q[1,:,:]=1.0
    results=[Result('a',p,0.01,None,None,'cpu'),Result('b',q,0.01,None,None,'cpu')]
    out=ensemble_probability(results)
    assert out.shape == (3,2,2)
    assert np.allclose(out[0],0.5)
    assert np.allclose(out[1],0.5)


def test_ensemble_requires_two():
    with pytest.raises(ValueError): ensemble_probability([])


def test_http_health_models(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    client=TestClient(app)
    health=client.get('/health')
    models=client.get('/models')
    assert health.status_code == 200
    assert models.status_code == 200
    assert len(models.json()['models']) == 3


def test_http_predict_with_dummy_model(monkeypatch):
    from fastapi.testclient import TestClient
    from backend import main
    def fake_predict(_model_id, image):
        px=np.zeros((3,image.height,image.width), dtype=np.float32)
        px[1]=1.0
        return Result('segformer_base',px,0.12,3,0.54,'cpu')
    monkeypatch.setattr(main,'predict_probs',fake_predict)
    b=io.BytesIO(); Image.new('RGB',(10,7),'white').save(b,format='PNG')
    response=TestClient(main.app).post('/predict',
        files={'file':('demo.png',b.getvalue(),'image/png')},
        data={'model_id':'segformer_base','alpha':'0.4'})
    assert response.status_code == 200,response.text
    payload=response.json()
    assert payload['stats'][1]['percent']==100.0
    assert payload['images']['overlay_png']
    assert payload['model_name']=='SegFormer-B0 · Baseline'


def test_http_predict_rejects_bad_image():
    from fastapi.testclient import TestClient
    from backend.main import app
    response=TestClient(app).post('/predict',
        files={'file':('invalid.png',b'garbage','image/png')},
        data={'model_id':'segformer_base'})
    assert response.status_code == 422
