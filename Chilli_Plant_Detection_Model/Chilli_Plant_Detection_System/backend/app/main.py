from io import BytesIO
from uuid import uuid4
import json
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


def save_result(
    request_id: str,
    original_image: Image.Image,
    prediction: dict,
):
    request_folder = OUTPUT_DIR / request_id
    request_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    original_path = request_folder / "original.jpg"
    annotated_path = request_folder / "annotated.jpg"
    json_path = request_folder / "result.json"

    original_image.save(
        original_path,
        "JPEG",
        quality=95,
    )

    cv2.imwrite(
        str(annotated_path),
        prediction["annotated_image"],
    )

    serializable = {
        k: v
        for k, v in prediction.items()
        if k != "annotated_image"
    }

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            serializable,
            file,
            indent=4,
        )


async def process_prediction(
    file: UploadFile,
    confidence: float,
):
    original, image_bgr = await read_uploaded_image(file)
    request_id = uuid4().hex

    try:
        prediction = model_service.predict(
            image=image_bgr,
            confidence=confidence,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Model inference failed: {error}",
        )

    save_result(
        request_id,
        original,
        prediction,
    )

    return {
        "request_id": request_id,
        "overall_prediction": prediction["overall_prediction"],
        "overall_confidence": prediction["overall_confidence"],
        "number_of_detections": prediction["number_of_detections"],
        "detections": prediction["detections"],
        "class_summary": prediction["class_summary"],
        "original_image_url": f"/results/{request_id}/original.jpg",
        "annotated_image_url": f"/results/{request_id}/annotated.jpg",
        "result_json_url": f"/results/{request_id}/result.json",
    }


@app.post(
    "/predict/image",
    response_model=PredictionResponse,
)
async def predict_image(
    file: UploadFile = File(...),
    confidence: float = Query(
        default=0.25,
        ge=0.05,
        le=1.0,
    ),
):
    return await process_prediction(
        file,
        confidence,
    )
