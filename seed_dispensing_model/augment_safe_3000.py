from pathlib import Path
from collections import Counter, defaultdict
import json
import shutil

import albumentations as A
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

TRAIN_DIR = DATASET_DIR / "train"

ANNOTATION_FILE = (
    TRAIN_DIR
    / "_annotations.coco.json"
)

OUTPUT_DIR = (
    DATASET_DIR
    / "train_augmented_3000"
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "_annotations.coco.json"
)

PREVIEW_DIR = (
    OUTPUT_DIR
    / "_preview"
)

TARGET_IMAGES = 3000

CLASSES = {
    0: "Existing plants",
    1: "Soil",
    2: "Weeds",
}

COLORS = {
    0: (0, 200, 0),
    1: (70, 150, 220),
    2: (180, 70, 180),
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


def decode_mask(segmentation, height, width):

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

        elif isinstance(rle.get("counts"), str):

            rle["counts"] = (
                rle["counts"].encode("ascii")
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


def encode_mask(mask):

    mask = (
        mask > 0
    ).astype(np.uint8)

    rle = mask_utils.encode(
        np.asfortranarray(mask)
    )

    if isinstance(rle["counts"], bytes):

        rle["counts"] = (
            rle["counts"].decode("ascii")
        )

    return rle


def get_bbox(mask):

    y, x = np.where(mask > 0)

    if len(x) == 0:
        return None

    x1 = int(x.min())
    x2 = int(x.max())

    y1 = int(y.min())
    y2 = int(y.max())

    return [
        float(x1),
        float(y1),
        float(x2 - x1 + 1),
        float(y2 - y1 + 1),
    ]


def build_augmentation():

    return A.Compose(
        [
            A.HorizontalFlip(
                p=0.50
            ),

            A.VerticalFlip(
                p=0.30
            ),

            A.RandomRotate90(
                p=0.40
            ),

            A.Affine(
                scale=(
                    0.94,
                    1.08,
                ),
                translate_percent={
                    "x": (-0.03, 0.03),
                    "y": (-0.03, 0.03),
                },
                rotate=(-8, 8),
                shear=(-2, 2),

                interpolation=cv2.INTER_LINEAR,
                mask_interpolation=cv2.INTER_NEAREST,

                border_mode=cv2.BORDER_REFLECT_101,

                p=0.55,
            ),

            A.OneOf(
                [
                    A.RandomBrightnessContrast(
                        brightness_limit=0.15,
                        contrast_limit=0.15,
                        p=1.0,
                    ),

                    A.RandomGamma(
                        gamma_limit=(88, 112),
                        p=1.0,
                    ),

                    A.CLAHE(
                        clip_limit=(1.0, 2.0),
                        tile_grid_size=(8, 8),
                        p=1.0,
                    ),
                ],
                p=0.65,
            ),

            A.HueSaturationValue(
                hue_shift_limit=5,
                sat_shift_limit=10,
                val_shift_limit=8,
                p=0.25,
            ),

            A.OneOf(
                [
                    A.GaussianBlur(
                        blur_limit=(3, 3),
                        p=1.0,
                    ),

                    A.GaussNoise(
                        std_range=(0.01, 0.025),
                        p=1.0,
                    ),
                ],
                p=0.10,
            ),
        ]
    )


def draw_preview(
    image,
    masks,
    class_ids,
):

    preview = image.copy()

    for mask, class_id in zip(
        masks,
        class_ids,
    ):

        mask = (
            np.asarray(mask) > 0
        ).astype(np.uint8)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        color = COLORS[class_id]

        cv2.drawContours(
            preview,
            contours,
            -1,
            color,
            2,
            cv2.LINE_AA,
        )

    return preview


def main():

    if not ANNOTATION_FILE.exists():

        raise FileNotFoundError(
            f"Annotation JSON not found:\n"
            f"{ANNOTATION_FILE}"
        )

    coco = load_json(
        ANNOTATION_FILE
    )

    categories = {
        item["id"]: item["name"]
        for item in coco["categories"]
    }

    if categories != CLASSES:

        print("Found classes:")

        for class_id, name in categories.items():
            print(class_id, name)

        raise ValueError(
            "\nExpected classes:\n"
            "0 = Existing plants\n"
            "1 = Soil\n"
            "2 = Weeds"
        )

    if OUTPUT_DIR.exists():

        shutil.rmtree(
            OUTPUT_DIR
        )

    OUTPUT_DIR.mkdir(
        parents=True
    )

    PREVIEW_DIR.mkdir(
        parents=True
    )

    annotations_by_image = defaultdict(
        list
    )

    for annotation in coco["annotations"]:

        annotations_by_image[
            annotation["image_id"]
        ].append(annotation)

    source_samples = []

    print("\nLoading original dataset...")

    for image_info in coco["images"]:

        image_path = (
            TRAIN_DIR
            / image_info["file_name"]
        )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            print(
                "Skipping:",
                image_path.name
            )

            continue

        height, width = image.shape[:2]

        masks = []
        class_ids = []

        for annotation in (
            annotations_by_image[
                image_info["id"]
            ]
        ):

            mask = decode_mask(
                annotation["segmentation"],
                height,
                width,
            )

            if mask is None:
                continue

            if mask.sum() == 0:
                continue

            masks.append(mask)

            class_ids.append(
                int(
                    annotation[
                        "category_id"
                    ]
                )
            )

        if not masks:
            continue

        source_samples.append(
            {
                "file_name":
                    image_info["file_name"],

                "image":
                    image,

                "masks":
                    masks,

                "class_ids":
                    class_ids,
            }
        )

    original_count = len(
        source_samples
    )

    if original_count == 0:

        raise RuntimeError(
            "No usable training images found."
        )

    if original_count > TARGET_IMAGES:

        raise ValueError(
            "Original dataset already has more "
            "than the target number of images."
        )

    print(
        f"Usable original images : "
        f"{original_count}"
    )

    print(
        f"Target images          : "
        f"{TARGET_IMAGES}"
    )

    print(
        f"New images required    : "
        f"{TARGET_IMAGES - original_count}"
    )

    augment = build_augmentation()

    output_images = []
    output_annotations = []

    image_id = 1
    annotation_id = 1

    class_mask_counts = Counter()

    # ------------------------------------------------------------
    # Save original real images first
    # ------------------------------------------------------------

    for sample in source_samples:

        image = sample["image"]

        output_name = (
            f"original_{image_id:05d}.jpg"
        )

        cv2.imwrite(
            str(
                OUTPUT_DIR
                / output_name
            ),
            image,
        )

        height, width = image.shape[:2]

        output_images.append(
            {
                "id": image_id,
                "file_name": output_name,
                "width": width,
                "height": height,
            }
        )

        for mask, class_id in zip(
            sample["masks"],
            sample["class_ids"],
        ):

            bbox = get_bbox(mask)

            if bbox is None:
                continue

            encoded = encode_mask(
                mask
            )

            output_annotations.append(
                {
                    "id":
                        annotation_id,

                    "image_id":
                        image_id,

                    "category_id":
                        class_id,

                    "segmentation":
                        encoded,

                    "bbox":
                        bbox,

                    "area":
                        float(
                            mask.sum()
                        ),

                    "iscrowd":
                        0,
                }
            )

            class_mask_counts[
                class_id
            ] += 1

            annotation_id += 1

        image_id += 1

    # ------------------------------------------------------------
    # Generate until exactly 3000
    # ------------------------------------------------------------

    source_index = 0
    preview_count = 0

    while len(output_images) < TARGET_IMAGES:

        sample = source_samples[
            source_index
            % original_count
        ]

        transformed = augment(
            image=sample["image"],
            masks=sample["masks"],
        )

        aug_image = transformed[
            "image"
        ]

        aug_masks = transformed[
            "masks"
        ]

        class_ids = sample[
            "class_ids"
        ]

        valid_masks = []
        valid_classes = []

        for mask, class_id in zip(
            aug_masks,
            class_ids,
        ):

            mask = (
                np.asarray(mask) > 0
            ).astype(np.uint8)

            if mask.sum() == 0:
                continue

            valid_masks.append(mask)
            valid_classes.append(
                class_id
            )

        if not valid_masks:

            source_index += 1
            continue

        output_name = (
            f"aug_{image_id:05d}.jpg"
        )

        cv2.imwrite(
            str(
                OUTPUT_DIR
                / output_name
            ),
            aug_image,
        )

        height, width = (
            aug_image.shape[:2]
        )

        output_images.append(
            {
                "id":
                    image_id,

                "file_name":
                    output_name,

                "width":
                    width,

                "height":
                    height,
            }
        )

        for mask, class_id in zip(
            valid_masks,
            valid_classes,
        ):

            bbox = get_bbox(
                mask
            )

            if bbox is None:
                continue

            encoded = encode_mask(
                mask
            )

            output_annotations.append(
                {
                    "id":
                        annotation_id,

                    "image_id":
                        image_id,

                    "category_id":
                        class_id,

                    "segmentation":
                        encoded,

                    "bbox":
                        bbox,

                    "area":
                        float(
                            mask.sum()
                        ),

                    "iscrowd":
                        0,
                }
            )

            class_mask_counts[
                class_id
            ] += 1

            annotation_id += 1

        if preview_count < 50:

            preview = draw_preview(
                aug_image,
                valid_masks,
                valid_classes,
            )

            cv2.imwrite(
                str(
                    PREVIEW_DIR
                    / output_name
                ),
                preview,
            )

            preview_count += 1

        if (
            len(output_images) % 100
            == 0
        ):

            print(
                f"Created "
                f"{len(output_images)} / "
                f"{TARGET_IMAGES}"
            )

        image_id += 1
        source_index += 1

    output_coco = {
        "info": {
            "description":
                "Paddy field segmentation - "
                "annotation-safe augmented dataset"
        },

        "categories": [
            {
                "id": class_id,
                "name": class_name,
                "supercategory":
                    "paddy-field",
            }
            for class_id, class_name
            in CLASSES.items()
        ],

        "images":
            output_images,

        "annotations":
            output_annotations,
    }

    save_json(
        output_coco,
        OUTPUT_JSON,
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "AUGMENTATION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Original real images   : "
        f"{original_count}"
    )

    print(
        f"Generated images       : "
        f"{TARGET_IMAGES - original_count}"
    )

    print(
        f"Final training images  : "
        f"{len(output_images)}"
    )

    print(
        f"Final annotations      : "
        f"{len(output_annotations)}"
    )

    print(
        "\nFinal mask counts:"
    )

    for class_id, class_name in (
        CLASSES.items()
    ):

        print(
            f"{class_id} "
            f"{class_name:<18} "
            f"{class_mask_counts[class_id]}"
        )

    print(
        f"\nDataset:\n"
        f"{OUTPUT_DIR}"
    )

    print(
        f"\nCOCO annotations:\n"
        f"{OUTPUT_JSON}"
    )

    print(
        f"\nCheck 50 augmented annotations:\n"
        f"{PREVIEW_DIR}"
    )


if __name__ == "__main__":
    main()