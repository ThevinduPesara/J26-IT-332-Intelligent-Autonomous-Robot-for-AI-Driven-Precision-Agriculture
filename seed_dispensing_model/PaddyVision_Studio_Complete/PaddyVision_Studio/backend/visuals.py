"""Pure rendering and pixel statistics from learned model probabilities."""
from __future__ import annotations
import base64
import io
from typing import Any
import numpy as np
from PIL import Image
from .config import LABELS, PALETTE

PALETTE_ARRAY = np.array(PALETTE, dtype=np.uint8)


def to_png_bytes(image: Image.Image) -> bytes:
    out = io.BytesIO()
    image.save(out, format='PNG', optimize=True)
    return out.getvalue()


def as_b64(image: Image.Image) -> str:
    return base64.b64encode(to_png_bytes(image)).decode('ascii')


def make_views(image: Image.Image, probabilities: np.ndarray, alpha: float = 0.50) -> dict[str, Any]:
    if not 0 <= alpha <= 1:
        raise ValueError('Overlay opacity must be between 0 and 1.')
    if probabilities.shape != (3, image.height, image.width):
        raise ValueError('Predictions must have shape (3, image_height, image_width).')
    if not np.isfinite(probabilities).all():
        raise ValueError('Prediction contains non-finite values.')
    prediction = probabilities.argmax(axis=0).astype(np.uint8)
    mask = Image.fromarray(PALETTE_ARRAY[prediction], mode='RGB')
    overlay = Image.blend(image, mask, alpha=alpha)
    confidence = probabilities.max(axis=0)
    # Confidence heatmap is derived from neural-network probabilities only.
    heat = np.uint8(np.clip(confidence * 255, 0, 255))
    conf_rgb = np.stack([255 - heat, heat, np.uint8(np.clip(180 - 0.5 * heat, 0, 255))], axis=-1)
    confidence_map = Image.fromarray(conf_rgb, 'RGB')
    counts = np.bincount(prediction.reshape(-1), minlength=3)
    total = int(prediction.size)
    categories = []
    for idx, label in enumerate(LABELS):
        selected = prediction == idx
        categories.append({
            'id': idx, 'name': label, 'color': '#%02x%02x%02x' % PALETTE[idx],
            'percent': round(float(100 * counts[idx] / total), 2),
            'pixels': int(counts[idx]),
            'mean_confidence': round(float(probabilities[idx][selected].mean()), 4) if np.any(selected) else None,
        })
    return {
        'width': image.width, 'height': image.height,
        'stats': categories, 'mean_confidence': round(float(confidence.mean()), 4),
        'images': {
            'original_png': as_b64(image),
            'overlay_png': as_b64(overlay),
            'mask_png': as_b64(mask),
            'confidence_png': as_b64(confidence_map),
        },
    }
