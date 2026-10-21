from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REPO_PEST_DIR = Path(__file__).resolve().parents[4]
DEFAULT_MODEL_CANDIDATES = [
    REPO_PEST_DIR / "training_results" / "YOLOv8n_Pest_Detection" / "weights" / "best.pt",
    REPO_PEST_DIR / "yolov8n.pt",
    BASE_DIR / "weights" / "best.pt",
]

resolved_model_path = next((p for p in DEFAULT_MODEL_CANDIDATES if p.exists()), DEFAULT_MODEL_CANDIDATES[0])

MODEL_PATH = Path(
    os.getenv("PEST_MODEL_PATH", str(resolved_model_path))
)


IMAGE_SIZE = int(os.getenv("PEST_IMAGE_SIZE", "640"))
DEFAULT_CONFIDENCE = float(os.getenv("PEST_CONFIDENCE", "0.25"))
CAMERA_INDEX = int(os.getenv("PEST_CAMERA_INDEX", "0"))
MAX_UPLOAD_MB = int(os.getenv("PEST_MAX_UPLOAD_MB", "15"))

EXPECTED_CLASSES = {
    0: "MP",
    1: "BT",
    2: "T",
    3: "C",
}

DISPLAY_NAMES = {
    "MP": "Aphid",
    "BT": "Whitefly",
    "T": "Thrips",
    "C": "Caterpillar",
}
