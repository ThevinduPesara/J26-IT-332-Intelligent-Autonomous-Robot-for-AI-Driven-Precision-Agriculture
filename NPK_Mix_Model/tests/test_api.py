from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['simulation_only'] is True


def test_api_reference():
    response = client.get('/api/v1/config')
    assert response.status_code == 200
    assert response.json()['dose_requires_user_calibration'] is True


def test_api_calculation_and_guard():
    response = client.post('/api/v1/calculate', json={'calculation_mode':'experimental_soil'})
    assert response.status_code == 200
    assert response.json()['status'] == 'SOIL_CALIBRATION_REQUIRED'
    assert response.json()['modelled']['liquid_comparison'] is None


def test_bad_data_rejected():
    response = client.post('/api/v1/calculate', json={'plot': {'area': -1}})
    assert response.status_code == 422
