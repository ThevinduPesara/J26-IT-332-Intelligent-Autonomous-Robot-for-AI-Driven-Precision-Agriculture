from collections import defaultdict
from threading import Lock
from typing import Any, Dict, Optional

import numpy as np
import torch
from ultralytics import YOLO

from app.config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    IMAGE_SIZE,
    EXPECTED_CLASSES,
)


class ChilliModelService:
    """Thread-safe YOLO inference service for Chilli Plant Detection model."""

    def __init__(self) -> None:
        self.model_path = MODEL_PATH
        self.device = "cpu"
        self.model = None
        self.model_lock = Lock()
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                "\nTRAINED MODEL NOT FOUND\n"
                f"Expected path:\n{self.model_path}\n\n"
                "Edit backend/.env and set MODEL_PATH to the trained best.pt."
            )

        if torch.cuda.is_available():
            self.device = 0
            print("=" * 72)
            print("GPU detected :", torch.cuda.get_device_name(0))
            print("CUDA version :", torch.version.cuda)
        else:
            self.device = "cpu"
            print("=" * 72)
            print("CUDA GPU not detected. Using CPU.")

        self.model = YOLO(str(self.model_path))
        self._validate_classes()

        print("Chilli Plant Detection model loaded successfully")
        print("Model path   :", self.model_path)
        print("Model classes:", self.model.names)
        print("=" * 72)

    def _validate_classes(self) -> None:
        loaded = {
            int(k): str(v)
            for k, v in self.model.names.items()
        }

        if loaded != EXPECTED_CLASSES:
            raise RuntimeError(
                "\nWRONG MODEL FILE LOADED\n"
                f"Expected: {EXPECTED_CLASSES}\n"
                f"Loaded:   {loaded}\n\n"
                "Use the trained best.pt, not the original yolo11s.pt."
            )
