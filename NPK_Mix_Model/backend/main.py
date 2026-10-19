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

