"""Application paths and operational defaults. No implicit remote model downloads."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(os.environ.get('PADDYVISION_PROJECT_ROOT', str(Path.home() / 'Downloads' / 'yasiru_Ai_part'))).expanduser().resolve()
DEVICE_PREFERENCE = os.environ.get('PADDYVISION_DEVICE', 'auto').lower()
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_IMAGE_PIXELS = 12_000_000
LABELS = ('Existing plants', 'Soil', 'Weeds')
PALETTE = ((41, 210, 138), (231, 167, 102), (180, 108, 245))  # RGB
MODEL_INPUT_BASELINE = 512

@dataclass(frozen=True)
class ModelSpec:
    id: str
    display_name: str
    family: str
    checkpoint: Path
    note: str
    badge: str

MODELS = (
    ModelSpec('segformer_base', 'SegFormer-B0 · Baseline', 'segformer',
              PROJECT_ROOT / 'SegFormer_B0_results' / 'best_segformer_b0.pt',
              'Original SegFormer-B0 training checkpoint', 'TRANSFORMER'),
    ModelSpec('segformer_group', 'SegFormer-B0 · Group Split', 'segformer',
              PROJECT_ROOT / 'SegFormer_B0_GroupSplit_Fixed' / 'best_segformer_b0.pt',
              'Group-safe split checkpoint (if training completed)', 'TRANSFORMER'),
    ModelSpec('deeplab_b4', 'DeepLabV3+ · EfficientNet-B4', 'deeplab',
              PROJECT_ROOT / 'DeepLabV3Plus_EfficientNetB4_results' / 'best_deeplabv3plus_b4.pt',
              'Pretrained EfficientNet encoder + DeepLabV3+ decoder', 'CNN + ASPP'),
)
MODEL_BY_ID = {m.id: m for m in MODELS}


def describe(spec: ModelSpec) -> dict:
    return {
        'id': spec.id, 'name': spec.display_name, 'family': spec.family,
        'badge': spec.badge, 'note': spec.note,
        'checkpoint': str(spec.checkpoint),
        'available': spec.checkpoint.is_file(),
        'size_mb': round(spec.checkpoint.stat().st_size / 1048576, 1) if spec.checkpoint.is_file() else None,
    }
