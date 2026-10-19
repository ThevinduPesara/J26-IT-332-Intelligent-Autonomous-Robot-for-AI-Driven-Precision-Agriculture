from io import BytesIO
import cv2
import numpy as np
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

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


@app.get("/")
def root():
    return {
        "system": "Chilli Plant Detection API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
    }


@app.get("/model")
def model_information():
    return model_service.get_model_info()


async def read_uploaded_image(file: UploadFile):
    if (
        file.content_type is not None
        and not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=415,
            detail="Only image files are supported.",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Empty image file.",
        )

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Maximum upload size is {MAX_UPLOAD_MB} MB."
            ),
        )

    try:
        pil_image = Image.open(
            BytesIO(contents)
        ).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file.",
        )

    image_rgb = np.array(pil_image)
    image_bgr = cv2.cvtColor(
        image_rgb,
        cv2.COLOR_RGB2BGR,
    )

    return pil_image, image_bgr
