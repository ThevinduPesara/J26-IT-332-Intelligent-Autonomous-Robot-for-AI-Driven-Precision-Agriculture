from pathlib import Path
import random

import cv2


# Dataset paths
IMAGE_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Thevindu_AI_Part\archive\val\images"
)

LABEL_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Thevindu_AI_Part\archive\val\labels"
)

OUTPUT_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Thevindu_AI_Part\annotation_check"
)


# Dataset class names
CLASS_NAMES = ["MP", "BT", "T", "C"]

# Bounding-box colours for each class
COLORS = {
    0: (0, 200, 0),
    1: (255, 120, 0),
    2: (180, 0, 255),
    3: (0, 140, 255),
}

NUM_IMAGES = 50
RANDOM_SEED = 42


def get_images(folder: Path):
    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    return [
        file
        for file in folder.iterdir()
        if file.suffix.lower() in extensions
    ]


def yolo_to_xyxy(
    x_center,
    y_center,
    width,
    height,
    image_width,
    image_height,
):
    box_width = width * image_width
    box_height = height * image_height

    x1 = int(x_center * image_width - box_width / 2)
    y1 = int(y_center * image_height - box_height / 2)
    x2 = int(x_center * image_width + box_width / 2)
    y2 = int(y_center * image_height + box_height / 2)

    x1 = max(0, min(x1, image_width - 1))
    y1 = max(0, min(y1, image_height - 1))
    x2 = max(0, min(x2, image_width - 1))
    y2 = max(0, min(y2, image_height - 1))

    return x1, y1, x2, y2


def draw_label(image, text, x1, y1, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2

    (text_width, text_height), baseline = cv2.getTextSize(
        text,
        font,
        font_scale,
        thickness,
    )

    label_top = max(0, y1 - text_height - baseline - 8)

    cv2.rectangle(
        image,
        (x1, label_top),
        (x1 + text_width + 10, y1),
        color,
        -1,
    )

    cv2.putText(
        image,
        text,
        (x1 + 5, y1 - 6),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )


def annotate_image(image_path: Path):
    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read image: {image_path.name}")
        return None, 0

    height, width = image.shape[:2]

    label_path = LABEL_DIR / f"{image_path.stem}.txt"

    if not label_path.exists():
        cv2.putText(
            image,
            "Label file not found",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

        return image, 0

    box_count = 0

    with open(label_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            parts = line.strip().split()

            if not parts:
                continue

            if len(parts) != 5:
                print(
                    f"Invalid annotation: "
                    f"{label_path.name}, line {line_number}"
                )
                continue

            try:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                box_width = float(parts[3])
                box_height = float(parts[4])

            except ValueError:
                print(
                    f"Invalid values: "
                    f"{label_path.name}, line {line_number}"
                )
                continue

            if class_id < 0 or class_id >= len(CLASS_NAMES):
                print(
                    f"Unknown class ID {class_id}: "
                    f"{label_path.name}"
                )
                continue

            x1, y1, x2, y2 = yolo_to_xyxy(
                x_center,
                y_center,
                box_width,
                box_height,
                width,
                height,
            )

            class_name = CLASS_NAMES[class_id]
            color = COLORS[class_id]

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                color,
                2,
            )

            draw_label(
                image,
                class_name,
                x1,
                y1,
                color,
            )

            box_count += 1

    return image, box_count


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    images = get_images(IMAGE_DIR)

    if not images:
        raise FileNotFoundError(
            f"No images found in:\n{IMAGE_DIR}"
        )

    random.seed(RANDOM_SEED)

    sample_size = min(
        NUM_IMAGES,
        len(images),
    )

    selected_images = random.sample(
        images,
        sample_size,
    )

    print(f"Available images : {len(images)}")
    print(f"Checking images  : {sample_size}")
    print(f"Output folder    : {OUTPUT_DIR}\n")

    total_boxes = 0

    for index, image_path in enumerate(
        selected_images,
        start=1,
    ):
        annotated_image, box_count = annotate_image(
            image_path
        )

        if annotated_image is None:
            continue

        output_path = (
            OUTPUT_DIR
            / f"{index:02d}_{image_path.name}"
        )

        cv2.imwrite(
            str(output_path),
            annotated_image,
        )

        total_boxes += box_count

        print(
            f"[{index:02d}/{sample_size}] "
            f"{image_path.name} -> "
            f"{box_count} annotation(s)"
        )

    print("\nAnnotation check completed.")
    print(f"Images checked : {sample_size}")
    print(f"Total boxes    : {total_boxes}")
    print(f"Results saved  : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()