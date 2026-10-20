from pathlib import Path
import csv

import cv2
import torch
from ultralytics import YOLO


PROJECT_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Thevindu_AI_Part"
)

MODEL_PATH = (
    PROJECT_DIR
    / "training_results"
    / "YOLOv8n_Pest_Detection"
    / "weights"
    / "best.pt"
)

DATASET_DIR = PROJECT_DIR / "archive"

OUTPUT_DIR = (
    PROJECT_DIR
    / "inference_val_test"
)

SPLITS = [
    "val",
    "test",
]

IMAGE_SIZE = 640
CONFIDENCE_THRESHOLD = 0.25

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def get_images(folder: Path):
    return sorted(
        file
        for file in folder.iterdir()
        if file.suffix.lower() in IMAGE_EXTENSIONS
    )


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found:\n{MODEL_PATH}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if torch.cuda.is_available():
        device = 0
        print(
            f"GPU: {torch.cuda.get_device_name(0)}"
        )
    else:
        device = "cpu"
        print("GPU not detected. Using CPU.")

    model = YOLO(
        str(MODEL_PATH)
    )

    print(f"\nModel loaded: {MODEL_PATH}")
    print(f"Classes: {model.names}")

    detection_rows = []
    summary_rows = []

    total_images = 0
    total_detections = 0

    for split in SPLITS:
        image_dir = (
            DATASET_DIR
            / split
            / "images"
        )

        if not image_dir.exists():
            print(
                f"\n{split} images folder not found. "
                f"Skipping..."
            )
            continue

        images = get_images(
            image_dir
        )

        if not images:
            print(
                f"\nNo images found in {split}."
            )
            continue

        annotated_dir = (
            OUTPUT_DIR
            / split
            / "annotated"
        )

        annotated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        print("\n" + "=" * 55)
        print(f"{split.upper()} INFERENCE")
        print("=" * 55)
        print(f"Images: {len(images)}\n")

        for index, image_path in enumerate(
            images,
            start=1,
        ):
            result = model.predict(
                source=str(image_path),
                imgsz=IMAGE_SIZE,
                conf=CONFIDENCE_THRESHOLD,
                device=device,
                verbose=False,
            )[0]

            annotated_image = result.plot()

            output_image = (
                annotated_dir
                / image_path.name
            )

            cv2.imwrite(
                str(output_image),
                annotated_image,
            )

            image_detections = 0

            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(
                        box.cls[0].item()
                    )

                    confidence = float(
                        box.conf[0].item()
                    )

                    x1, y1, x2, y2 = (
                        box.xyxy[0]
                        .cpu()
                        .tolist()
                    )

                    class_name = (
                        model.names[class_id]
                    )

                    detection_rows.append(
                        {
                            "split": split,
                            "image": image_path.name,
                            "class_id": class_id,
                            "class_name": class_name,
                            "confidence": round(
                                confidence,
                                4,
                            ),
                            "x1": round(x1, 2),
                            "y1": round(y1, 2),
                            "x2": round(x2, 2),
                            "y2": round(y2, 2),
                        }
                    )

                    image_detections += 1
                    total_detections += 1

            summary_rows.append(
                {
                    "split": split,
                    "image": image_path.name,
                    "detections": image_detections,
                }
            )

            total_images += 1

            print(
                f"[{index:04d}/{len(images):04d}] "
                f"{image_path.name} -> "
                f"{image_detections} detection(s)"
            )

    detections_csv = (
        OUTPUT_DIR
        / "detections.csv"
    )

    with open(
        detections_csv,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "split",
                "image",
                "class_id",
                "class_name",
                "confidence",
                "x1",
                "y1",
                "x2",
                "y2",
            ],
        )

        writer.writeheader()
        writer.writerows(
            detection_rows
        )

    summary_csv = (
        OUTPUT_DIR
        / "image_summary.csv"
    )

    with open(
        summary_csv,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "split",
                "image",
                "detections",
            ],
        )

        writer.writeheader()
        writer.writerows(
            summary_rows
        )

    print("\n" + "=" * 55)
    print("INFERENCE COMPLETE")
    print("=" * 55)

    print(
        f"Images processed : {total_images}"
    )

    print(
        f"Total detections : {total_detections}"
    )

    print(
        f"\nResults saved to:\n{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()