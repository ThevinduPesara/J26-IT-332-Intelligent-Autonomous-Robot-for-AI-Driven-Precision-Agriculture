from pathlib import Path
import json

import torch
import yaml
from ultralytics import YOLO


PROJECT_DIR = Path(r"C:\Users\LENOVO\Downloads\Thevindu_AI_Part")

DATA_YAML = PROJECT_DIR / "thevindu_pest.yaml"
RESULTS_DIR = PROJECT_DIR / "training_results"

RUN_NAME = "YOLOv8n_Pest_Detection"

MODEL_WEIGHTS = "yolov8n.pt"

IMAGE_SIZE = 640
EPOCHS = 100
BATCH_SIZE = 8
PATIENCE = 20
WORKERS = 4


def check_dataset_config():
    if not DATA_YAML.exists():
        raise FileNotFoundError(
            f"Dataset configuration file not found:\n{DATA_YAML}"
        )

    with open(DATA_YAML, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    required_keys = {"path", "train", "val", "nc", "names"}

    missing_keys = required_keys - config.keys()

    if missing_keys:
        raise ValueError(
            f"Missing fields in YAML: {sorted(missing_keys)}"
        )

    if config["nc"] != 4:
        raise ValueError(
            f"Expected 4 classes, but YAML contains {config['nc']}."
        )

    print("Dataset configuration checked successfully.")
    print(f"Classes: {config['names']}")

    return config


def get_device():
    if torch.cuda.is_available():
        print("\nGPU detected")
        print(f"Device : {torch.cuda.get_device_name(0)}")
        print(f"CUDA   : {torch.version.cuda}")
        return 0

    print("\nCUDA GPU was not detected.")
    print("Training will run on CPU.")

    return "cpu"


def train_model(device):
    print("\nLoading pretrained YOLOv8n model...")

    model = YOLO(MODEL_WEIGHTS)

    print("\nStarting training...\n")

    model.train(
        data=str(DATA_YAML),
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        patience=PATIENCE,
        device=device,
        workers=WORKERS,
        pretrained=True,
        optimizer="auto",
        seed=42,
        deterministic=True,
        plots=True,
        save=True,
        val=True,
        project=str(RESULTS_DIR),
        name=RUN_NAME,
        exist_ok=True,
    )


def get_best_model_path():
    best_model_path = (
        RESULTS_DIR
        / RUN_NAME
        / "weights"
        / "best.pt"
    )

    if not best_model_path.exists():
        raise FileNotFoundError(
            f"best.pt was not found:\n{best_model_path}"
        )

    return best_model_path


def validate_best_model(best_model_path, device):
    print("\nRunning final validation using best.pt...\n")

    model = YOLO(str(best_model_path))

    metrics = model.val(
        data=str(DATA_YAML),
        split="val",
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        device=device,
        workers=WORKERS,
        plots=True,
        project=str(RESULTS_DIR),
        name=f"{RUN_NAME}_Validation",
        exist_ok=True,
    )

    results = {
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "mAP50": float(metrics.box.map50),
        "mAP50_95": float(metrics.box.map),
    }

    return results


def save_metrics(metrics):
    output_file = (
        RESULTS_DIR
        / RUN_NAME
        / "validation_metrics.json"
    )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    return output_file


def print_results(metrics, best_model_path, metrics_file):
    print("\n" + "=" * 60)
    print("TRAINING AND VALIDATION COMPLETE")
    print("=" * 60)

    print(f"\nPrecision     : {metrics['precision']:.4f}")
    print(f"Recall        : {metrics['recall']:.4f}")
    print(f"mAP@0.50      : {metrics['mAP50']:.4f}")
    print(f"mAP@0.50:0.95 : {metrics['mAP50_95']:.4f}")

    print("\nBest trained model:")
    print(best_model_path)

    print("\nValidation metrics:")
    print(metrics_file)

    print("\nTraining graphs and validation plots are saved inside:")
    print(RESULTS_DIR / RUN_NAME)


def main():
    print("=" * 60)
    print("THEVINDU - CHILLI PEST DETECTION")
    print("YOLOv8n Training and Validation")
    print("=" * 60)

    check_dataset_config()

    device = get_device()

    train_model(device)

    best_model_path = get_best_model_path()

    metrics = validate_best_model(
        best_model_path,
        device,
    )

    metrics_file = save_metrics(
        metrics
    )

    print_results(
        metrics,
        best_model_path,
        metrics_file,
    )


if __name__ == "__main__":
    main()