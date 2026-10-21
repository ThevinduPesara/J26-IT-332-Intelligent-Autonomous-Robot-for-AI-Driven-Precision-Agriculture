from __future__ import annotations

from io import BytesIO
from typing import Annotated

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from .config import DEFAULT_CONFIDENCE, MAX_UPLOAD_MB, OUTPUT_DIR
from .model_service import PestDetector


app = FastAPI(
    title="ChilliGuard Vision API",
    version="1.0.0",
    description="YOLOv8n pest detection service for chilli plant images.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/results", StaticFiles(directory=str(OUTPUT_DIR)), name="results")

detector = PestDetector()


@app.get("/")
def root():
    return {
        "service": "ChilliGuard Vision API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "device": detector.model_info()["device_name"],
    }


@app.get("/model")
def model_info():
    return detector.model_info()


def decode_upload(data: bytes) -> np.ndarray:
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Image is larger than {MAX_UPLOAD_MB} MB.",
        )

    try:
        image = Image.open(BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(status_code=400, detail="Invalid image file.") from error

    rgb = np.array(image)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


@app.post("/predict/image")
async def predict_image(
    file: Annotated[UploadFile, File(...)],
    confidence: float = Query(DEFAULT_CONFIDENCE, ge=0.05, le=0.95),
):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    image = decode_upload(data)

    try:
        return detector.predict(image, confidence)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/predict/frame")
async def predict_frame(
    file: Annotated[UploadFile, File(...)],
    confidence: float = Query(DEFAULT_CONFIDENCE, ge=0.05, le=0.95),
):
    return await predict_image(file=file, confidence=confidence)


@app.get("/camera/stream")
def camera_stream(
    confidence: float = Query(DEFAULT_CONFIDENCE, ge=0.05, le=0.95),
):
    try:
        stream = detector.camera_stream(confidence)
        return StreamingResponse(
            stream,
            media_type="multipart/x-mixed-replace; boundary=frame",
        )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
