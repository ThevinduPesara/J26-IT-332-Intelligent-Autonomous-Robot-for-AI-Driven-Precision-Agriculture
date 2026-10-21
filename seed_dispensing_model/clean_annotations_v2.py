from pathlib import Path
from collections import Counter, defaultdict
import json
import shutil

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
    / "annotation_check_v2"
)

SPLITS = ["train", "valid", "test"]


# Final model classes
FINAL_CLASSES = {
    "Existing plants": 0,
    "Soil": 1,
    "Weeds": 2,
}


CLASS_COLORS = {
    "Existing plants": (0, 200, 0),
    "Soil": (70, 150, 220),
    "Weeds": (180, 70, 180),
}


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def make_backup(annotation_file):
    backup_file = (
        annotation_file.parent
        / "_annotations.before_v2_cleanup.coco.json"
    )

    if not backup_file.exists():
        shutil.copy2(
            annotation_file,
            backup_file,
        )

    return backup_file


def existing_image_files(split_dir):
    return {
        file.name
        for file in split_dir.iterdir()
        if (
            file.is_file()
            and file.suffix.lower()
            in IMAGE_EXTENSIONS
        )
    }


def clean_annotations(split):
    split_dir = DATASET_DIR / split

    annotation_file = (
        split_dir
        / "_annotations.coco.json"
    )

    if not annotation_file.exists():
        raise FileNotFoundError(
            f"Annotation file not found:\n"
            f"{annotation_file}"
        )

    make_backup(annotation_file)

    coco = load_json(annotation_file)

    images = coco.get("images", [])
    annotations = coco.get(
        "annotations",
        [],
    )
    categories = coco.get(
        "categories",
        [],
    )

    category_names = {
        category["id"]: category["name"]
        for category in categories
    }

    files_on_disk = existing_image_files(
        split_dir
    )

    # Keep only images that still exist physically
    available_images = {
        image["id"]: image
        for image in images
        if image["file_name"]
        in files_on_disk
    }

    deleted_image_records = (
        len(images)
        - len(available_images)
    )

    annotations_by_image = defaultdict(
        list
    )

    removed_old_classes = Counter()

    for annotation in annotations:
        image_id = annotation.get(
            "image_id"
        )

        if image_id not in available_images:
            continue

        old_category_id = annotation.get(
            "category_id"
        )

        class_name = category_names.get(
            old_category_id
        )

        if class_name not in FINAL_CLASSES:
            removed_old_classes[
                class_name or "Unknown"
            ] += 1
            continue

        if not annotation.get(
            "segmentation"
        ):
            continue

        annotations_by_image[
            image_id
        ].append(
            annotation
        )

    # Keep only images that still contain one
    # of the final three classes
    usable_images = []

    for image_id, image in (
        available_images.items()
    ):
        if annotations_by_image.get(
            image_id
        ):
            usable_images.append(
                image
            )

    no_target_images = (
        len(available_images)
        - len(usable_images)
    )

    # Re-number image IDs
    image_id_map = {}

    clean_images = []

    for new_image_id, image in enumerate(
        usable_images,
        start=1,
    ):
        old_image_id = image["id"]

        image_id_map[
            old_image_id
        ] = new_image_id

        new_image = image.copy()
        new_image["id"] = new_image_id

        clean_images.append(
            new_image
        )

    clean_annotations = []

    annotation_id = 1
    mask_counts = Counter()
    image_counts = defaultdict(set)

    for old_image_id, ann_list in (
        annotations_by_image.items()
    ):
        if old_image_id not in image_id_map:
            continue

        new_image_id = image_id_map[
            old_image_id
        ]

        for annotation in ann_list:
            old_category_id = annotation[
                "category_id"
            ]

            class_name = category_names[
                old_category_id
            ]

            new_annotation = (
                annotation.copy()
            )

            new_annotation["id"] = (
                annotation_id
            )

            new_annotation["image_id"] = (
                new_image_id
            )

            new_annotation[
                "category_id"
            ] = FINAL_CLASSES[
                class_name
            ]

            clean_annotations.append(
                new_annotation
            )

            mask_counts[
                class_name
            ] += 1

            image_counts[
                class_name
            ].add(
                new_image_id
            )

            annotation_id += 1

    clean_categories = [
        {
            "id": class_id,
            "name": class_name,
            "supercategory": "paddy-field",
        }
        for class_name, class_id
        in FINAL_CLASSES.items()
    ]

    cleaned_coco = {
        "info": coco.get(
            "info",
            {},
        ),
        "licenses": coco.get(
            "licenses",
            [],
        ),
        "categories": clean_categories,
        "images": clean_images,
        "annotations": clean_annotations,
    }

    save_json(
        cleaned_coco,
        annotation_file,
    )

    print("\n" + "=" * 65)
    print(f"{split.upper()} CLEANING")
    print("=" * 65)

    print(
        f"Original images       : {len(images)}"
    )
    print(
        f"Deleted photos removed: "
        f"{deleted_image_records}"
    )
    print(
        f"No-target images      : "
        f"{no_target_images}"
    )
    print(
        f"Final images          : "
        f"{len(clean_images)}"
    )

    print(
        f"\nOriginal annotations  : "
        f"{len(annotations)}"
    )
    print(
        f"Final annotations     : "
        f"{len(clean_annotations)}"
    )

    print("\nFinal class distribution")

    for class_name in FINAL_CLASSES:
        print(
            f"{class_name:<18} "
            f"{len(image_counts[class_name]):>4} images | "
            f"{mask_counts[class_name]:>4} masks"
        )

    print("\nRemoved annotations")

    if removed_old_classes:
        for class_name, count in (
            removed_old_classes.items()
        ):
            print(
                f"{class_name:<18} : {count}"
            )
    else:
        print("None")

    return cleaned_coco


def decode_segmentation(
    segmentation,
    height,
    width,
):
    if isinstance(segmentation, list):
        rles = mask_utils.frPyObjects(
            segmentation,
            height,
            width,
        )

        rle = mask_utils.merge(rles)

    elif isinstance(
        segmentation,
        dict,
    ):
        rle = segmentation.copy()

        if isinstance(
            rle.get("counts"),
            list,
        ):
            rle = mask_utils.frPyObjects(
                rle,
                height,
                width,
            )

    else:
        return None

    mask = mask_utils.decode(rle)

    if mask.ndim == 3:
        mask = np.any(
            mask,
            axis=2,
        ).astype(np.uint8)

    return mask.astype(np.uint8)


def draw_label(
    image,
    text,
    x,
    y,
    color,
):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.55
    thickness = 2

    (text_width, text_height), _ = (
        cv2.getTextSize(
            text,
            font,
            scale,
            thickness,
        )
    )

    y = max(
        y,
        text_height + 10,
    )

    cv2.rectangle(
        image,
        (x, y - text_height - 9),
        (x + text_width + 10, y + 3),
        color,
        -1,
    )

    cv2.putText(
        image,
        text,
        (x + 5, y - 4),
        font,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )


def create_annotation_preview(
    split,
    coco,
):
    split_dir = DATASET_DIR / split
    output_dir = OUTPUT_DIR / split

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    category_names = {
        category["id"]: category["name"]
        for category in coco[
            "categories"
        ]
    }

    annotations_by_image = defaultdict(
        list
    )

    for annotation in coco[
        "annotations"
    ]:
        annotations_by_image[
            annotation["image_id"]
        ].append(annotation)

    print(
        f"\nCreating {split} previews..."
    )

    for index, image_info in enumerate(
        coco["images"],
        start=1,
    ):
        image_path = (
            split_dir
            / image_info["file_name"]
        )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            continue

        height, width = (
            image.shape[:2]
        )

        annotations = (
            annotations_by_image.get(
                image_info["id"],
                [],
            )
        )

        for annotation in annotations:
            class_name = (
                category_names[
                    annotation[
                        "category_id"
                    ]
                ]
            )

            color = CLASS_COLORS[
                class_name
            ]

            try:
                mask = decode_segmentation(
                    annotation[
                        "segmentation"
                    ],
                    height,
                    width,
                )
            except Exception:
                continue

            if (
                mask is None
                or mask.sum() == 0
            ):
                continue

            contours, _ = (
                cv2.findContours(
                    mask,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE,
                )
            )

            # Boundary line only
            cv2.drawContours(
                image,
                contours,
                -1,
                color,
                2,
                cv2.LINE_AA,
            )

            bbox = annotation.get(
                "bbox",
                [],
            )

            if len(bbox) == 4:
                x = max(
                    0,
                    int(bbox[0]),
                )

                y = max(
                    25,
                    int(bbox[1]),
                )
            else:
                x, y = 10, 30

            draw_label(
                image,
                class_name,
                x,
                y,
                color,
            )

        output_file = (
            output_dir
            / (
                f"{index:03d}_"
                f"{image_info['file_name']}"
            )
        )

        cv2.imwrite(
            str(output_file),
            image,
        )

    print(
        f"Saved: {output_dir}"
    )


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 65)
    print("PADDY FIELD DATASET - CLEAN ANNOTATION V2")
    print("=" * 65)

    print("\nClasses")
    print("0 = Existing plants")
    print("1 = Soil")
    print("2 = Weeds")

    for split in SPLITS:
        split_dir = DATASET_DIR / split

        if not split_dir.exists():
            print(
                f"\nSkipping {split}: "
                f"folder does not exist."
            )
            continue

        cleaned_coco = (
            clean_annotations(
                split
            )
        )

        create_annotation_preview(
            split,
            cleaned_coco,
        )

    print("\n" + "=" * 65)
    print("FINISHED")
    print("=" * 65)

    print(
        "\nUpdated COCO files are inside "
        "train / valid / test."
    )

    print(
        f"\nAnnotation previews:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()