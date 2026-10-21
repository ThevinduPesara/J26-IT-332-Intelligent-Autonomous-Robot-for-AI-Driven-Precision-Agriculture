from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


LOCAL_MODEL = BASE_DIR / "model" / "best.pt"
PARENT_MODEL = (
    BASE_DIR.parent.parent
    / "Chilli_YOLO_NPK"
    / "training_results"
    / "YOLO11s_NPK"
    / "weights"
    / "best.pt"
)
DEFAULT_MODEL_PATH = LOCAL_MODEL if LOCAL_MODEL.exists() else PARENT_MODEL

env_model_path = os.getenv("MODEL_PATH")
if env_model_path and Path(env_model_path).exists():
    MODEL_PATH = Path(env_model_path)
else:
    MODEL_PATH = DEFAULT_MODEL_PATH

OUTPUT_DIR = Path(
    os.getenv(
        "OUTPUT_DIR",
        str(BASE_DIR / "outputs"),
    )
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONFIDENCE_THRESHOLD = float(
    os.getenv("CONFIDENCE_THRESHOLD", "0.25")
)

IMAGE_SIZE = int(
    os.getenv("IMAGE_SIZE", "640")
)

CAMERA_INDEX = int(
    os.getenv("CAMERA_INDEX", "0")
)

MAX_UPLOAD_MB = int(
    os.getenv("MAX_UPLOAD_MB", "15")
)

MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


EXPECTED_CLASSES = {
    0: "Healthy",
    1: "N_Def",
    2: "P_Def",
    3: "K_Def",
}
