from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from threading import Lock
from typing import Any
import json
import uuid

import cv2
import numpy as np
import torch
from ultralytics import YOLO

from .config import (
    CAMERA_INDEX,
    DEFAULT_CONFIDENCE,
    DISPLAY_NAMES,
    EXPECTED_CLASSES,
    IMAGE_SIZE,
    MODEL_PATH,
    OUTPUT_DIR,
)


class PestDetector:
    def __init__(self) -> None:
        self.device = 0 if torch.cuda.is_available() else "cpu"
        self.lock = Lock()
        self.model = self._load_model()
        self.class_names = self._normalise_names(self.model.names)
        self._validate_classes()
        self.validation_metrics = self._load_validation_metrics()

    @staticmethod
    def _normalise_names(names: Any) -> dict[int, str]:
        if isinstance(names, dict):
            return {int(k): str(v) for k, v in names.items()}
        return {index: str(name) for index, name in enumerate(names)}

    def _load_model(self) -> YOLO:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        return YOLO(str(MODEL_PATH))

    def _validate_classes(self) -> None:
        if self.class_names != EXPECTED_CLASSES:
            raise RuntimeError(
                "Unexpected model classes. "
                f"Expected {EXPECTED_CLASSES}, got {self.class_names}."
            )

    def _load_validation_metrics(self) -> dict[str, float]:
        metrics_path = MODEL_PATH.parent.parent / "validation_metrics.json"
        if not metrics_path.exists():
            return {}

        try:
            with metrics_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return {
                key: float(value)
                for key, value in data.items()
                if isinstance(value, (int, float))
            }
        except (OSError, ValueError, TypeError):
            return {}

    def model_info(self) -> dict[str, Any]:
        if self.device == 0:
            device_name = torch.cuda.get_device_name(0)
        else:
            device_name = "CPU"

        return {
            "model": "YOLOv8n",
            "model_path": str(MODEL_PATH),
            "image_size": IMAGE_SIZE,
            "device": self.device,
            "device_name": device_name,
            "classes": self.class_names,
            "display_names": DISPLAY_NAMES,
            "validation_metrics": self.validation_metrics,
        }

    def predict(self, image: np.ndarray, confidence: float = DEFAULT_CONFIDENCE) -> dict[str, Any]:
        if image is None or image.size == 0:
            raise ValueError("Empty or invalid image received.")

        confidence = float(np.clip(confidence, 0.05, 0.95))

        with self.lock:
            result = self.model.predict(
                source=image,
                imgsz=IMAGE_SIZE,
                conf=confidence,
                device=self.device,
                verbose=False,
            )[0]

        detections: list[dict[str, Any]] = []
        class_summary: dict[str, dict[str, Any]] = {
            name: {
                "display_name": DISPLAY_NAMES[name],
                "detections": 0,
                "average_confidence": 0.0,
                "highest_confidence": 0.0,
            }
            for name in EXPECTED_CLASSES.values()
        }

        confidence_by_class: dict[str, list[float]] = defaultdict(list)
        height, width = image.shape[:2]

        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                class_name = self.class_names[class_id]
                score = float(box.conf[0].item())
                x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].cpu().tolist()]

                center_x = (x1 + x2) / 2.0
                center_y = (y1 + y2) / 2.0

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": class_name,
                        "display_name": DISPLAY_NAMES[class_name],
                        "confidence": round(score, 4),
                        "bounding_box": {
                            "x1": round(x1, 1),
                            "y1": round(y1, 1),
                            "x2": round(x2, 1),
                            "y2": round(y2, 1),
                        },
                        "target_center": {
                            "x": round(center_x, 1),
                            "y": round(center_y, 1),
                            "x_normalized": round(center_x / width, 4),
                            "y_normalized": round(center_y / height, 4),
                        },
                    }
                )
                confidence_by_class[class_name].append(score)

        for class_name, scores in confidence_by_class.items():
            class_summary[class_name]["detections"] = len(scores)
            class_summary[class_name]["average_confidence"] = round(sum(scores) / len(scores), 4)
            class_summary[class_name]["highest_confidence"] = round(max(scores), 4)

        detections.sort(key=lambda item: item["confidence"], reverse=True)
        primary = detections[0] if detections else None

        annotated = result.plot()
        request_id = uuid.uuid4().hex[:12]
        request_dir = OUTPUT_DIR / request_id
        request_dir.mkdir(parents=True, exist_ok=True)

        original_path = request_dir / "original.jpg"
        annotated_path = request_dir / "annotated.jpg"
        result_path = request_dir / "result.json"

        cv2.imwrite(str(original_path), image)
        cv2.imwrite(str(annotated_path), annotated)

        payload = {
            "request_id": request_id,
            "pest_present": bool(detections),
            "number_of_detections": len(detections),
            "primary_detection": primary,
            "class_summary": class_summary,
            "detections": detections,
            "image": {
                "width": width,
                "height": height,
            },
            "confidence_threshold": confidence,
            "original_image_url": f"/results/{request_id}/original.jpg",
            "annotated_image_url": f"/results/{request_id}/annotated.jpg",
        }

        with result_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

        return payload

    def camera_stream(self, confidence: float = DEFAULT_CONFIDENCE):
        camera = cv2.VideoCapture(CAMERA_INDEX)
        if not camera.isOpened():
            raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}.")

        try:
            while True:
                ok, frame = camera.read()
                if not ok:
                    break

                with self.lock:
                    result = self.model.predict(
                        source=frame,
                        imgsz=IMAGE_SIZE,
                        conf=confidence,
                        device=self.device,
                        verbose=False,
                    )[0]

                annotated = result.plot()
                encoded, buffer = cv2.imencode(".jpg", annotated)
                if not encoded:
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + buffer.tobytes()
                    + b"\r\n"
                )
        finally:
            camera.release()
