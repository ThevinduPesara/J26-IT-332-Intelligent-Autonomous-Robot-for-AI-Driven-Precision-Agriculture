from pathlib import Path
import random
import csv

from ultralytics import YOLO


# ============================================================
# MODEL
# ============================================================

MODEL_PATH = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\Chilli_YOLO_NPK\training_results\YOLO11s_NPK\weights\best.pt"
)


# ============================================================
# SOURCE IMAGE FOLDER
# ============================================================

# Recommended:
# Use the held-out TEST dataset
SOURCE_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\Chilli_YOLO_NPK\images\test"
)

# If you really want random images from the original dataset,
# replace SOURCE_DIR with:
#
# SOURCE_DIR = Path(
#     r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\pepper\pepper\pepper_photo"
# )


# ============================================================
# OUTPUT
# Saves close to best.pt
# ============================================================

OUTPUT_DIR = (
    MODEL_PATH.parent
    / "random_100_inference"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SETTINGS
# ============================================================

NUMBER_OF_IMAGES = 100

CONFIDENCE_THRESHOLD = 0.25

IMAGE_SIZE = 640

RANDOM_SEED = 42


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
}


# ============================================================
# CHECK MODEL
# ============================================================

if not MODEL_PATH.exists():

    raise FileNotFoundError(
        f"Model not found:\n{MODEL_PATH}"
    )


if not SOURCE_DIR.exists():

    raise FileNotFoundError(
        f"Image folder not found:\n{SOURCE_DIR}"
    )


# ============================================================
# LOAD MODEL
# ============================================================

model = YOLO(
    str(MODEL_PATH)
)


print()
print("=" * 70)
print("CHILLI NPK MODEL LOADED")
print("=" * 70)

print()
print("Model classes:")

print(
    model.names
)


# ============================================================
# FIND ALL IMAGES
# ============================================================

all_images = [
    image_path
    for image_path in SOURCE_DIR.rglob("*")
    if (
        image_path.is_file()
        and image_path.suffix.lower()
        in IMAGE_EXTENSIONS
    )
]


print()
print(
    f"Total images available: "
    f"{len(all_images)}"
)


if len(all_images) == 0:

    raise RuntimeError(
        "No images found."
    )


# ============================================================
# RANDOMLY SELECT 100
# ============================================================

random.seed(
    RANDOM_SEED
)


number_to_select = min(
    NUMBER_OF_IMAGES,
    len(all_images)
)


selected_images = random.sample(
    all_images,
    number_to_select
)


print(
    f"Random images selected: "
    f"{len(selected_images)}"
)


# ============================================================
# SAVE SELECTED IMAGE LIST
# ============================================================

selected_list_path = (
    OUTPUT_DIR
    / "selected_100_images.txt"
)


with open(
    selected_list_path,
    "w",
    encoding="utf-8"
) as file:

    for image_path in selected_images:

        file.write(
            str(image_path)
            + "\n"
        )


# ============================================================
# RUN INFERENCE
# ============================================================

print()
print("=" * 70)
print("STARTING RANDOM 100 IMAGE INFERENCE")
print("=" * 70)


results = model.predict(

    source=[
        str(image_path)
        for image_path
        in selected_images
    ],

    imgsz=IMAGE_SIZE,

    conf=CONFIDENCE_THRESHOLD,

    device=0,

    save=True,

    save_txt=False,

    save_conf=False,

    project=str(
        OUTPUT_DIR
    ),

    name="annotated_images",

    exist_ok=True,

    verbose=True
)


# ============================================================
# SAVE DETECTION RESULTS TO CSV
# ============================================================

CSV_PATH = (
    OUTPUT_DIR
    / "prediction_results.csv"
)


rows = []


for result in results:

    image_name = Path(
        result.path
    ).name

    boxes = result.boxes


    # --------------------------------------------------------
    # No detections
    # --------------------------------------------------------

    if boxes is None or len(boxes) == 0:

        rows.append(
            {
                "image": image_name,
                "class_id": "",
                "class_name": "NO_DETECTION",
                "confidence": "",
                "x1": "",
                "y1": "",
                "x2": "",
                "y2": "",
            }
        )

        continue


    # --------------------------------------------------------
    # Detected objects
    # --------------------------------------------------------

    for box in boxes:

        class_id = int(
            box.cls[0]
        )

        confidence = float(
            box.conf[0]
        )

        class_name = (
            model.names[
                class_id
            ]
        )


        x1, y1, x2, y2 = (
            box.xyxy[0]
            .cpu()
            .tolist()
        )


        rows.append(
            {
                "image": image_name,

                "class_id": (
                    class_id
                ),

                "class_name": (
                    class_name
                ),

                "confidence": round(
                    confidence,
                    4
                ),

                "x1": round(
                    x1,
                    2
                ),

                "y1": round(
                    y1,
                    2
                ),

                "x2": round(
                    x2,
                    2
                ),

                "y2": round(
                    y2,
                    2
                ),
            }
        )


# ============================================================
# WRITE CSV
# ============================================================

with open(
    CSV_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    fieldnames = [
        "image",
        "class_id",
        "class_name",
        "confidence",
        "x1",
        "y1",
        "x2",
        "y2",
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        rows
    )


# ============================================================
# CLASS SUMMARY
# ============================================================

summary = {
    "Healthy": 0,
    "N_Def": 0,
    "P_Def": 0,
    "K_Def": 0,
    "NO_DETECTION": 0,
}


images_seen_per_class = {
    key: set()
    for key in summary
}


for row in rows:

    class_name = row[
        "class_name"
    ]

    image_name = row[
        "image"
    ]

    if class_name in summary:

        images_seen_per_class[
            class_name
        ].add(
            image_name
        )


for class_name in summary:

    summary[
        class_name
    ] = len(
        images_seen_per_class[
            class_name
        ]
    )


SUMMARY_PATH = (
    OUTPUT_DIR
    / "prediction_summary.csv"
)


with open(
    SUMMARY_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.writer(
        file
    )

    writer.writerow(
        [
            "Class",
            "Number_of_images"
        ]
    )

    for (
        class_name,
        count
    ) in summary.items():

        writer.writerow(
            [
                class_name,
                count
            ]
        )


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("INFERENCE COMPLETE")
print("=" * 70)

print()

print(
    f"Random images tested: "
    f"{len(selected_images)}"
)

print()

print("IMAGE-LEVEL DETECTION SUMMARY")
print("-" * 40)


for class_name, count in summary.items():

    print(
        f"{class_name:<20}"
        f"{count}"
    )


print()
print("=" * 70)

print(
    "ANNOTATED IMAGES:"
)

print(
    OUTPUT_DIR
    / "annotated_images"
)

print()

print(
    "FULL PREDICTION CSV:"
)

print(
    CSV_PATH
)

print()

print(
    "SUMMARY CSV:"
)

print(
    SUMMARY_PATH
)

print()

print(
    "RANDOM IMAGE LIST:"
)

print(
    selected_list_path
)

print("=" * 70)