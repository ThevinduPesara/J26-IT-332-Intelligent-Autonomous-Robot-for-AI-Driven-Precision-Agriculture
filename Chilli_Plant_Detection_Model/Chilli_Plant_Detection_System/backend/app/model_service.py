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

    def predict(
        self,
        image: np.ndarray,
        confidence: Optional[float] = None,
    ) -> Dict[str, Any]:

        threshold = (
            CONFIDENCE_THRESHOLD
            if confidence is None
            else float(confidence)
        )

        with self.model_lock:
            result = self.model.predict(
                source=image,
                imgsz=IMAGE_SIZE,
                conf=threshold,
                device=self.device,
                verbose=False,
            )[0]

        detections = []
        class_confidences = defaultdict(list)
        vote_scores = defaultdict(float)

        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                class_name = str(self.model.names[class_id])
                score = float(box.conf[0].item())
                x1, y1, x2, y2 = box.xyxy[0].detach().cpu().tolist()

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": round(score, 4),
                        "bounding_box": {
                            "x1": round(x1, 2),
                            "y1": round(y1, 2),
                            "x2": round(x2, 2),
                            "y2": round(y2, 2),
                        },
                    }
                )

                class_confidences[class_name].append(score)
                vote_scores[class_name] += score

        if vote_scores:
            overall_prediction = max(
                vote_scores,
                key=vote_scores.get,
            )
            winning = class_confidences[overall_prediction]
            overall_confidence = sum(winning) / len(winning)
        else:
            overall_prediction = "NO_DETECTION"
            overall_confidence = 0.0

        class_summary = {}
        for class_name in ("Healthy", "N_Def", "P_Def", "K_Def"):
            scores = class_confidences.get(class_name, [])

            if scores:
                class_summary[class_name] = {
                    "detections": len(scores),
                    "average_confidence": round(
                        sum(scores) / len(scores), 4
                    ),
                    "highest_confidence": round(max(scores), 4),
                    "vote_score": round(vote_scores[class_name], 4),
                }
            else:
                class_summary[class_name] = {
                    "detections": 0,
                    "average_confidence": 0.0,
                    "highest_confidence": 0.0,
                    "vote_score": 0.0,
                }

        return {
            "overall_prediction": overall_prediction,
            "overall_confidence": round(overall_confidence, 4),
            "number_of_detections": len(detections),
            "detections": detections,
            "class_summary": class_summary,
            "annotated_image": result.plot(),
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_path": str(self.model_path),
            "device": str(self.device),
            "classes": self.model.names,
            "image_size": IMAGE_SIZE,
            "default_confidence": CONFIDENCE_THRESHOLD,
        }
