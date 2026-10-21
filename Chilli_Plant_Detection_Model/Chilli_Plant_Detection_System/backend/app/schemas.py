from typing import Dict, List
from pydantic import BaseModel


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bounding_box: BoundingBox


class ClassSummaryItem(BaseModel):
    detections: int
    average_confidence: float
    highest_confidence: float
    vote_score: float


class PredictionResponse(BaseModel):
    request_id: str
    overall_prediction: str
    overall_confidence: float
    number_of_detections: int
    detections: List[Detection]
    class_summary: Dict[str, ClassSummaryItem]
    original_image_url: str
    annotated_image_url: str
    result_json_url: str
