"""FastAPI backend for Manjitha's Chilli Liquid NPK research prototype."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .science import DoseRequest, calculate, SCHEDULE, DOA_URL, demo_request

app = FastAPI(
    title="NutrientOS | Chilli Liquid NPK Research API",
    version="1.0.0",
    description="DOA field chilli baseline and explicit, unvalidated soil-coefficient research simulation. Never controls a pump.",
)
app.add_middleware(CORSMiddleware,
    allow_origins=["http://127.0.0.1:8501", "http://localhost:8501"],
    allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

@app.get("/health")
def health():
    return {"status": "ok", "app": "NutrientOS", "simulation_only": True, "version": "1.0.0"}

@app.get("/api/v1/config")
def config():
    return {"crop": "Sri Lankan field chilli", "source_url": DOA_URL,
            "schedule_kg_ha": list(SCHEDULE), "demo": demo_request().model_dump(mode="json"),
            "dose_requires_user_calibration": True, "physical_actuation": False}

@app.get("/api/v1/sensor-demo")
def sensor_demo():
    return {"n_mgkg": 80, "p_mgkg": 12, "k_mgkg": 90,
            "ph": 6.3, "origin": "SIMULATED", "not_sensor_measurements": True}

