from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import (
    OUTPUT_DIR,
    MAX_UPLOAD_BYTES,
    MAX_UPLOAD_MB,
    CAMERA_INDEX,
)
from app.model_service import ChilliModelService
from app.schemas import PredictionResponse


app = FastAPI(
    title="Chilli Plant Detection API",
    description=(
        "YOLO11s inference API for Healthy, Nitrogen Deficiency, "
        "Phosphorus Deficiency and Potassium Deficiency."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/results",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="results",
)

model_service = ChilliModelService()
