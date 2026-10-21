from pathlib import Path
import json

import cv2
import numpy as np
from pycocotools import mask as mask_utils


PROJECT_DIR = Path(
    r"C:\Users\LENOVO\Downloads\yasiru_Ai_part"
)

DATASET_DIR = (
    PROJECT_DIR
    / "paddy field.v1i.coco-segmentation"
)

OUTPUT_DIR = (
    PROJECT_DIR
    / "annotation_visual_check"
)

SPLITS = ["train", "valid", "test"]

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


CLASS_COLORS = {
    "paddy-field": (80, 80, 80),
    "Empty gap": (0, 215, 255),
    "Existing plants": (0, 190, 0),
    "Soil": (80, 120, 180),
    "Stones": (180, 180, 180),
    "Weeds": (170, 60, 180),
}


def find_annotation_file(folder):
    annotation_file = folder / "_annotations.coco.json"

    if annotation_file.exists():
        return annotation_file

    json_files = list(folder.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No COCO annotation file found in:\n{folder}"
        )

    return json_files[0]


def load_coco(annotation_file):
    with open(
        annotation_file,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def segmentation_to_mask(segmentation, height, width):
    if isinstance(segmentation, list):
        rles = mask_utils.frPyObjects(
            segmentation,
            height,
            width,
        )

        rle = mask_utils.merge(rles)

    elif isinstance(segmentation, dict):
        rle = segmentation.copy()

        if isinstance(rle.get("counts"), list):
            rle = mask_utils.frPyObjects(
                rle,
                height,
                width,
            )

    else:
        return None

    mask = mask_utils.decode(rle)

    if mask.ndim == 3:
        mask = np.any(mask, axis=2).astype(np.uint8)

    return mask.astype(np.uint8)


def draw_mask(image, mask, color):
    overlay = image.copy()

    overlay[mask > 0] = (
        np.array(color, dtype=np.uint8)
    )

    cv2.addWeighted(
        overlay,
        0.38,
        image,
        0.62,
        0,
        image,
    )


def draw_mask_boundary(image, mask, color):
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    cv2.drawContours(
        image,
        contours,
        -1,
        color,
        2,
        cv2.LINE_AA,
    )

    return contours


def label_position(annotation, contours):
    bbox = annotation.get("bbox")

    if bbox and len(bbox) == 4:
        x, y, width, height = bbox

        return (
            max(0, int(x)),
            max(25, int(y)),
        )

    if contours:
        largest = max(
            contours,
            key=cv2.contourArea,
        )

        x, y, _, _ = cv2.boundingRect(
            largest
        )

        return (
            max(0, x),
            max(25, y),
        )

    return 10, 30


def draw_class_label(
    image,
    class_name,
    position,
    color,
):
    x, y = position

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.62
    thickness = 2

    (text_width, text_height), baseline = (
        cv2.getTextSize(
            class_name,
            font,
            font_scale,
            thickness,
        )
    )

    top = max(
        0,
        y - text_height - baseline - 10,
    )

    right = min(
        image.shape[1] - 1,
        x + text_width + 12,
    )

    cv2.rectangle(
        image,
        (x, top),
        (right, y + 2),
        color,
        -1,
    )

    cv2.putText(
        image,
        class_name,
        (x + 6, y - 5),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )


def process_split(split):
    split_dir = DATASET_DIR / split

    annotation_file = find_annotation_file(
        split_dir
    )

    coco = load_coco(
        annotation_file
    )

    categories = {
        category["id"]: category["name"]
        for category in coco["categories"]
    }

    images = {
        image["id"]: image
        for image in coco["images"]
    }

    annotations_by_image = {}

    for annotation in coco.get(
        "annotations",
        [],
    ):
        image_id = annotation["image_id"]

        annotations_by_image.setdefault(
            image_id,
            [],
        ).append(annotation)

    output_split = OUTPUT_DIR / split

    output_split.mkdir(
        parents=True,
        exist_ok=True,
    )

    invalid_masks = 0
    missing_images = 0
    images_without_annotations = 0

    print("\n" + "=" * 65)
    print(f"{split.upper()} ANNOTATION VISUALIZATION")
    print("=" * 65)

    for index, (image_id, image_info) in enumerate(
        images.items(),
        start=1,
    ):
        image_path = (
            split_dir
            / image_info["file_name"]
        )

        if not image_path.exists():
            print(
                f"[MISSING IMAGE] {image_info['file_name']}"
            )

            missing_images += 1
            continue

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            print(
                f"[UNREADABLE] {image_info['file_name']}"
            )

            missing_images += 1
            continue

        height, width = image.shape[:2]

        annotations = annotations_by_image.get(
            image_id,
            [],
        )

        if not annotations:
            images_without_annotations += 1

            cv2.putText(
                image,
                "NO ANNOTATIONS",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        class_names_in_image = []

        for annotation in annotations:
            category_id = annotation.get(
                "category_id"
            )

            class_name = categories.get(
                category_id,
                f"Unknown-{category_id}",
            )

            segmentation = annotation.get(
                "segmentation"
            )

            if not segmentation:
                invalid_masks += 1
                continue

            try:
                mask = segmentation_to_mask(
                    segmentation,
                    height,
                    width,
                )

            except Exception as error:
                print(
                    f"[MASK ERROR] "
                    f"{image_info['file_name']} | "
                    f"{class_name} | {error}"
                )

                invalid_masks += 1
                continue

            if mask is None or mask.sum() == 0:
                invalid_masks += 1
                continue

            color = CLASS_COLORS.get(
                class_name,
                (255, 255, 255),
            )

            draw_mask(
                image,
                mask,
                color,
            )

            contours = draw_mask_boundary(
                image,
                mask,
                color,
            )

            position = label_position(
                annotation,
                contours,
            )

            draw_class_label(
                image,
                class_name,
                position,
                color,
            )

            if class_name not in class_names_in_image:
                class_names_in_image.append(
                    class_name
                )

        output_path = (
            output_split
            / f"{index:03d}_{image_info['file_name']}"
        )

        cv2.imwrite(
            str(output_path),
            image,
        )

        classes_text = (
            ", ".join(class_names_in_image)
            if class_names_in_image
            else "None"
        )

        print(
            f"[{index:03d}/{len(images):03d}] "
            f"{image_info['file_name']} | "
            f"{len(annotations)} mask(s) | "
            f"{classes_text}"
        )

    print("\nSummary")
    print("-" * 65)

    print(
        f"Images processed          : {len(images)}"
    )

    print(
        f"Images without annotations: "
        f"{images_without_annotations}"
    )

    print(
        f"Invalid masks             : "
        f"{invalid_masks}"
    )

    print(
        f"Missing/unreadable images : "
        f"{missing_images}"
    )

    print(
        f"Saved to:\n{output_split}"
    )


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 65)
    print("PADDY FIELD COCO SEGMENTATION VISUAL CHECK")
    print("=" * 65)

    for split in SPLITS:
        split_dir = DATASET_DIR / split

        if not split_dir.exists():
            print(
                f"\nSkipping {split}: folder not found."
            )
            continue

        process_split(split)

    print("\n" + "=" * 65)
    print("VISUAL CHECK COMPLETE")
    print("=" * 65)

    print(
        f"\nAnnotated images saved in:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()