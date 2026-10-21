from pathlib import Path
from collections import defaultdict
import json
import random

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pycocotools import mask as mask_utils


DATASET_DIR = Path(
    r"C:\Users\LENOVO\Downloads\yasiru_Ai_part"
    r"\paddy field.v1i.coco-segmentation"
    r"\train_augmented_3000"
)

JSON_FILE = DATASET_DIR / "_annotations.coco.json"

OUTPUT_FILE = (
    DATASET_DIR
    / "augmentation_annotation_check.png"
)

NUM_IMAGES = 12
RANDOM_SEED = 42


COLORS = {
    0: (0, 200, 0),       # Existing plants
    1: (220, 150, 70),    # Soil
    2: (180, 70, 180),    # Weeds
}


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


with open(
    JSON_FILE,
    "r",
    encoding="utf-8",
) as file:
    coco = json.load(file)


categories = {
    c["id"]: c["name"]
    for c in coco["categories"]
}


annotations_by_image = defaultdict(list)

for annotation in coco["annotations"]:
    annotations_by_image[
        annotation["image_id"]
    ].append(annotation)


images = coco["images"].copy()

random.seed(RANDOM_SEED)

selected = random.sample(
    images,
    min(NUM_IMAGES, len(images)),
)


fig, axes = plt.subplots(
    3,
    4,
    figsize=(18, 14),
)

axes = axes.flatten()


for ax, image_info in zip(
    axes,
    selected,
):
    image_path = (
        DATASET_DIR
        / image_info["file_name"]
    )

    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        ax.axis("off")
        continue

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    height, width = image.shape[:2]

    display = image.copy()

    annotations = annotations_by_image.get(
        image_info["id"],
        [],
    )

    class_names = []

    for annotation in annotations:
        class_id = annotation[
            "category_id"
        ]

        class_name = categories[
            class_id
        ]

        mask = decode_mask(
            annotation["segmentation"],
            height,
            width,
        )

        if mask is None:
            continue

        if mask.sum() == 0:
            continue

        color_bgr = COLORS[
            class_id
        ]

        color = np.array(
            [
                color_bgr[2],
                color_bgr[1],
                color_bgr[0],
            ],
            dtype=np.uint8,
        )

        overlay = display.copy()

        overlay[
            mask > 0
        ] = color

        display = cv2.addWeighted(
            display,
            0.70,
            overlay,
            0.30,
            0,
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        contour_image = cv2.cvtColor(
            display,
            cv2.COLOR_RGB2BGR,
        )

        cv2.drawContours(
            contour_image,
            contours,
            -1,
            color_bgr,
            2,
        )

        display = cv2.cvtColor(
            contour_image,
            cv2.COLOR_BGR2RGB,
        )

        if class_name not in class_names:
            class_names.append(
                class_name
            )

    ax.imshow(display)

    ax.set_title(
        f"{image_info['file_name']}\n"
        f"{', '.join(class_names)}",
        fontsize=8,
    )

    ax.axis("off")


for ax in axes[len(selected):]:
    ax.axis("off")


plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=180,
    bbox_inches="tight",
)

plt.show()


print("\nSaved:")
print(OUTPUT_FILE)