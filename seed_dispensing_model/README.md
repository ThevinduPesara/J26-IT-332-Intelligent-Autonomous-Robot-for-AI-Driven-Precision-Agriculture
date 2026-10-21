# Seed Dispensing Model

This directory contains the trained computer-vision models and the scripts used
to train, evaluate, and run inference for paddy-field segmentation.

The frontend and backend application are intentionally not included in this
model module.

## Available checkpoints

| Model | Checkpoint |
| --- | --- |
| DeepLabV3+ with EfficientNet-B4 | `DeepLabV3Plus_EfficientNetB4_results/best_deeplabv3plus_b4.pt` |
| SegFormer-B0 baseline | `SegFormer_B0_results/best_segformer_b0.pt` |
| SegFormer-B0 group split | `SegFormer_B0_GroupSplit_Fixed/best_segformer_b0.pt` |

## Installation

Create a Python environment with a compatible PyTorch installation, then run:

```bash
python -m pip install -r requirements.txt
```

## PaddyVision API

The inference API has a separate requirements file. Use Python 3.10–3.12 and
install dependencies into a dedicated environment from the Studio directory:

```powershell
Set-Location seed_dispensing_model\PaddyVision_Studio_Complete\PaddyVision_Studio
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8003
```

PaddyVision uses port 8003; port 8001 belongs to the NPK backend. If using a
CUDA-enabled PyTorch build, install the version matching your CUDA setup before
installing the remaining requirements. The repository launcher
`seed_dispensing_model\run_backend.bat` uses this environment when available.

## Repository contents

- `train_*.py`: model training pipelines
- `infer_*.py` and `test_infer_*.py`: inference and evaluation scripts
- `analyze_*.py`, `augment_*.py`, `clean_*.py`, `plot_*.py`, and
  `visualize_*.py`: dataset preparation and analysis utilities
- `*_results/`: selected checkpoints, metrics, histories, and plots

## Dataset

The dataset is not stored in this repository because of its size. Place the
dataset in a local project directory and update the `PROJECT`, `PROJECT_DIR`,
or `DATASET_DIR` constants in the relevant script before training or inference.

The expected dataset directory is:

```text
paddy field.v1i.coco-segmentation/
├── train/
├── valid/
├── test/
└── train_augmented_3000/
```

## Notes

- The scripts currently preserve the paths and experiment layout used during
  the original training runs.
- Use only trusted model checkpoints when loading PyTorch files.
- The checkpoints support the research model experiments; they are not a
  complete frontend, backend, or production deployment.
