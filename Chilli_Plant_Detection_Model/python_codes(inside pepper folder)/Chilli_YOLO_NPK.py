from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import random
import shutil
import xml.etree.ElementTree as ET

from PIL import Image
import torch
from ultralytics import YOLO


# ============================================================
# 1. PATHS
# ============================================================

IMAGE_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\pepper\pepper\pepper_photo"
)

XML_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\pepper\pepper\Labels"
)

OUTPUT_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\Chilli_YOLO_NPK"
)


# ============================================================
# 2. TRAINING SETTINGS
# ============================================================

MODEL_NAME = "yolo11s.pt"

EPOCHS = 100
PATIENCE = 20

IMAGE_SIZE = 640
BATCH_SIZE = 8

SEED = 42


# ============================================================
# 3. DATA SPLIT
# ============================================================

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10


# ============================================================
# 4. FINAL YOLO CLASSES
# ============================================================

CLASS_NAMES = {
    0: "Healthy",
    1: "N_Def",
    2: "P_Def",
    3: "K_Def",
}


# ============================================================
# 5. ONLY THESE ORIGINAL XML LABELS WILL BE USED
# ============================================================

LABEL_MAP = {

    # Healthy
    "healthy_leaf": 0,
    "healthy_backleaf": 0,
    "healthy_bottomleaf": 0,

    # Nitrogen deficiency
    "n_leaf": 1,
    "n_backleaf": 1,
    "n_bottomleaf": 1,

    # Phosphorus deficiency
    "p_leaf": 2,
    "p_backleaf": 2,
    "p_bottomleaf": 2,

    # Potassium deficiency
    "k_leaf": 3,
    "k_backleaf": 3,
    "k_bottomleaf": 3,
}


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
}


# ============================================================
# 6. CLEAN LABEL NAME
# ============================================================

def normalize_label(name):

    return (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


# ============================================================
# 7. BUILD IMAGE INDEX
# ============================================================

def build_image_index():

    filename_index = {}
    stem_index = defaultdict(list)

    for image_path in IMAGE_DIR.rglob("*"):

        if not image_path.is_file():
            continue

        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        filename_index[
            image_path.name.lower()
        ] = image_path

        stem_index[
            image_path.stem.lower()
        ].append(image_path)

    return filename_index, stem_index


# ============================================================
# 8. FIND IMAGE MATCHING XML
# ============================================================

def find_matching_image(
    xml_path,
    root,
    filename_index,
    stem_index
):

    xml_filename = (
        root.findtext("filename")
        or ""
    ).strip()

    # First try XML filename
    if xml_filename:

        key = Path(
            xml_filename
        ).name.lower()

        if key in filename_index:

            return filename_index[key]

    # Second try same stem
    stem = xml_path.stem.lower()

    matches = stem_index.get(
        stem,
        []
    )

    if matches:

        return matches[0]

    return None


# ============================================================
# 9. GET XML IMAGE SIZE
# ============================================================

def get_xml_size(root):

    size = root.find("size")

    if size is None:
        return None, None

    try:

        width = int(
            float(
                size.findtext(
                    "width",
                    "0"
                )
            )
        )

        height = int(
            float(
                size.findtext(
                    "height",
                    "0"
                )
            )
        )

        if width <= 0 or height <= 0:
            return None, None

        return width, height

    except Exception:

        return None, None


# ============================================================
# 10. CONVERT PASCAL VOC BOUNDING BOX TO YOLO
# ============================================================

def convert_bbox_to_yolo(
    bbox,
    xml_width,
    xml_height,
    real_width,
    real_height
):

    try:

        xmin = float(
            bbox.findtext(
                "xmin",
                "0"
            )
        )

        ymin = float(
            bbox.findtext(
                "ymin",
                "0"
            )
        )

        xmax = float(
            bbox.findtext(
                "xmax",
                "0"
            )
        )

        ymax = float(
            bbox.findtext(
                "ymax",
                "0"
            )
        )

    except Exception:

        return None

    # ========================================================
    # Correct XML/Image resolution mismatch
    # ========================================================

    if (
        xml_width is not None
        and xml_height is not None
        and xml_width > 0
        and xml_height > 0
    ):

        scale_x = (
            real_width
            / xml_width
        )

        scale_y = (
            real_height
            / xml_height
        )

        xmin *= scale_x
        xmax *= scale_x

        ymin *= scale_y
        ymax *= scale_y

    # ========================================================
    # Clip coordinates
    # ========================================================

    xmin = max(
        0,
        min(
            xmin,
            real_width
        )
    )

    xmax = max(
        0,
        min(
            xmax,
            real_width
        )
    )

    ymin = max(
        0,
        min(
            ymin,
            real_height
        )
    )

    ymax = max(
        0,
        min(
            ymax,
            real_height
        )
    )

    if xmin >= xmax:
        return None

    if ymin >= ymax:
        return None

    # ========================================================
    # Convert to YOLO normalized format
    # ========================================================

    x_center = (
        (xmin + xmax) / 2
    ) / real_width

    y_center = (
        (ymin + ymax) / 2
    ) / real_height

    box_width = (
        xmax - xmin
    ) / real_width

    box_height = (
        ymax - ymin
    ) / real_height

    if (
        box_width <= 0
        or box_height <= 0
    ):
        return None

    return (
        x_center,
        y_center,
        box_width,
        box_height
    )


# ============================================================
# 11. READ DATASET
# ============================================================

def collect_records():

    (
        filename_index,
        stem_index
    ) = build_image_index()

    xml_files = sorted(
        XML_DIR.rglob("*.xml")
    )

    records = []

    class_box_counts = Counter()

    malformed_xml = 0
    no_image = 0
    no_target_labels = 0
    invalid_boxes = 0

    print()
    print("=" * 70)

    print(
        f"Total XML files found: "
        f"{len(xml_files)}"
    )

    print("=" * 70)

    for index, xml_path in enumerate(
        xml_files,
        start=1
    ):

        # ----------------------------------------------------
        # Read XML
        # ----------------------------------------------------

        try:

            tree = ET.parse(
                xml_path
            )

            root = tree.getroot()

        except Exception as error:

            malformed_xml += 1

            print(
                f"[BAD XML] "
                f"{xml_path.name}"
            )

            continue

        # ----------------------------------------------------
        # Find image
        # ----------------------------------------------------

        image_path = find_matching_image(
            xml_path,
            root,
            filename_index,
            stem_index
        )

        if image_path is None:

            no_image += 1
            continue

        # ----------------------------------------------------
        # Actual image size
        # ----------------------------------------------------

        try:

            with Image.open(
                image_path
            ) as image:

                real_width, real_height = (
                    image.size
                )

        except Exception:

            continue

        # ----------------------------------------------------
        # XML image size
        # ----------------------------------------------------

        (
            xml_width,
            xml_height
        ) = get_xml_size(
            root
        )

        yolo_lines = []
        class_ids = []

        # ----------------------------------------------------
        # Read annotations
        # ----------------------------------------------------

        for obj in root.findall(
            "object"
        ):

            original_label = (
                obj.findtext("name")
                or ""
            )

            original_label = normalize_label(
                original_label
            )

            # =================================================
            # IMPORTANT:
            # Ignore everything except our selected 12 labels
            # =================================================

            if original_label not in LABEL_MAP:
                continue

            class_id = LABEL_MAP[
                original_label
            ]

            bbox = obj.find(
                "bndbox"
            )

            if bbox is None:
                continue

            converted = convert_bbox_to_yolo(
                bbox=bbox,
                xml_width=xml_width,
                xml_height=xml_height,
                real_width=real_width,
                real_height=real_height
            )

            if converted is None:

                invalid_boxes += 1
                continue

            (
                x_center,
                y_center,
                box_width,
                box_height
            ) = converted

            yolo_line = (
                f"{class_id} "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{box_width:.6f} "
                f"{box_height:.6f}"
            )

            yolo_lines.append(
                yolo_line
            )

            class_ids.append(
                class_id
            )

            class_box_counts[
                class_id
            ] += 1

        # ----------------------------------------------------
        # Ignore image if no selected annotations
        # ----------------------------------------------------

        if not yolo_lines:

            no_target_labels += 1
            continue

        # ----------------------------------------------------
        # Determine main class for stratified split
        # ----------------------------------------------------

        dominant_class = Counter(
            class_ids
        ).most_common(1)[0][0]

        records.append(
            {
                "image_path": image_path,
                "xml_path": xml_path,
                "labels": yolo_lines,
                "dominant_class": dominant_class,
            }
        )

        if index % 500 == 0:

            print(
                f"Processed "
                f"{index} / "
                f"{len(xml_files)} XML files"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("DATASET FILTERING COMPLETE")
    print("=" * 70)

    print(
        f"Usable images: "
        f"{len(records)}"
    )

    print(
        f"Malformed XML: "
        f"{malformed_xml}"
    )

    print(
        f"Images not found: "
        f"{no_image}"
    )

    print(
        f"Ignored non-NPK images: "
        f"{no_target_labels}"
    )

    print(
        f"Invalid boxes: "
        f"{invalid_boxes}"
    )

    print()

    print(
        "FINAL BOUNDING BOX COUNTS"
    )

    print("-" * 40)

    for class_id in range(4):

        print(
            f"{CLASS_NAMES[class_id]:<15}"
            f"{class_box_counts[class_id]}"
        )

    return records


# ============================================================
# 12. STRATIFIED TRAIN/VAL/TEST SPLIT
# ============================================================

def split_dataset(records):

    random.seed(
        SEED
    )

    grouped = defaultdict(list)

    for record in records:

        grouped[
            record["dominant_class"]
        ].append(
            record
        )

    train_records = []
    val_records = []
    test_records = []

    for class_id in range(4):

        items = grouped[
            class_id
        ]

        random.shuffle(
            items
        )

        total = len(items)

        train_count = int(
            total * TRAIN_RATIO
        )

        val_count = int(
            total * VAL_RATIO
        )

        train_items = (
            items[
                :train_count
            ]
        )

        val_items = (
            items[
                train_count:
                train_count + val_count
            ]
        )

        test_items = (
            items[
                train_count + val_count:
            ]
        )

        train_records.extend(
            train_items
        )

        val_records.extend(
            val_items
        )

        test_records.extend(
            test_items
        )

    random.shuffle(
        train_records
    )

    random.shuffle(
        val_records
    )

    random.shuffle(
        test_records
    )

    return (
        train_records,
        val_records,
        test_records
    )


# ============================================================
# 13. CREATE UNIQUE FILE NAME
# ============================================================

def create_unique_name(
    image_path
):

    unique_id = hashlib.md5(
        str(
            image_path
        ).encode(
            "utf-8"
        )
    ).hexdigest()[:8]

    return (
        f"{image_path.stem}_"
        f"{unique_id}"
    )


# ============================================================
# 14. SAVE ONE SPLIT
# ============================================================

def save_split(
    records,
    split_name
):

    image_folder = (
        OUTPUT_DIR
        / "images"
        / split_name
    )

    label_folder = (
        OUTPUT_DIR
        / "labels"
        / split_name
    )

    image_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    label_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    for index, record in enumerate(
        records,
        start=1
    ):

        source_image = record[
            "image_path"
        ]

        unique_name = create_unique_name(
            source_image
        )

        destination_image = (
            image_folder
            / (
                unique_name
                + source_image.suffix.lower()
            )
        )

        destination_label = (
            label_folder
            / (
                unique_name
                + ".txt"
            )
        )

        shutil.copy2(
            source_image,
            destination_image
        )

        with open(
            destination_label,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "\n".join(
                    record["labels"]
                )
            )

            file.write(
                "\n"
            )

        if index % 500 == 0:

            print(
                f"{split_name}: "
                f"{index} files saved"
            )


# ============================================================
# 15. CREATE data.yaml
# ============================================================

def create_yaml():

    yaml_path = (
        OUTPUT_DIR
        / "data.yaml"
    )

    dataset_path = (
        OUTPUT_DIR.resolve()
        .as_posix()
    )

    yaml_text = f"""
path: {dataset_path}

train: images/train
val: images/val
test: images/test

nc: 4

names:
  0: Healthy
  1: N_Def
  2: P_Def
  3: K_Def
"""

    with open(
        yaml_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            yaml_text.strip()
        )

    return yaml_path


# ============================================================
# 16. PRINT SPLIT SUMMARY
# ============================================================

def print_split_summary(
    name,
    records
):

    class_counts = Counter(
        record["dominant_class"]
        for record in records
    )

    print()
    print("=" * 50)

    print(
        name.upper()
    )

    print("=" * 50)

    print(
        f"Total images: "
        f"{len(records)}"
    )

    for class_id in range(4):

        print(
            f"{CLASS_NAMES[class_id]:<15}"
            f"{class_counts[class_id]}"
        )


# ============================================================
# 17. MAIN
# ============================================================

def main():

    print()
    print("=" * 70)

    print(
        "CHILLI NPK DEFICIENCY "
        "YOLO11s TRAINING"
    )

    print("=" * 70)

    # ========================================================
    # Check input folders
    # ========================================================

    if not IMAGE_DIR.exists():

        print()
        print(
            "ERROR: Image folder not found"
        )

        print(
            IMAGE_DIR
        )

        return

    if not XML_DIR.exists():

        print()
        print(
            "ERROR: XML folder not found"
        )

        print(
            XML_DIR
        )

        return

    # ========================================================
    # Remove old generated output
    # ========================================================

    if OUTPUT_DIR.exists():

        print()
        print(
            "Removing old generated "
            "Chilli YOLO folder..."
        )

        shutil.rmtree(
            OUTPUT_DIR
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # Prepare data
    # ========================================================

    records = collect_records()

    if len(records) == 0:

        print()
        print(
            "ERROR: No usable training "
            "images found."
        )

        return

    # ========================================================
    # Split dataset
    # ========================================================

    (
        train_records,
        val_records,
        test_records
    ) = split_dataset(
        records
    )

    print_split_summary(
        "Train",
        train_records
    )

    print_split_summary(
        "Validation",
        val_records
    )

    print_split_summary(
        "Test",
        test_records
    )

    # ========================================================
    # Save YOLO dataset
    # ========================================================

    print()
    print("=" * 70)

    print(
        "CREATING YOLO DATASET"
    )

    print("=" * 70)

    save_split(
        train_records,
        "train"
    )

    save_split(
        val_records,
        "val"
    )

    save_split(
        test_records,
        "test"
    )

    data_yaml = create_yaml()

    print()
    print(
        "Dataset created successfully."
    )

    print(
        data_yaml
    )

    # ========================================================
    # GPU CHECK
    # ========================================================

    print()
    print("=" * 70)

    print(
        "HARDWARE CHECK"
    )

    print("=" * 70)

    if torch.cuda.is_available():

        device = 0

        print(
            "GPU detected:"
        )

        print(
            torch.cuda.get_device_name(
                0
            )
        )

        print(
            f"CUDA version: "
            f"{torch.version.cuda}"
        )

    else:

        device = "cpu"

        print(
            "CUDA GPU not detected."
        )

        print(
            "Training will use CPU."
        )

    # ========================================================
    # LOAD YOLO11s
    # ========================================================

    print()
    print("=" * 70)

    print(
        "LOADING YOLO11s PRETRAINED MODEL"
    )

    print("=" * 70)

    model = YOLO(
        MODEL_NAME
    )

    # ========================================================
    # TRAIN
    # ========================================================

    print()
    print("=" * 70)

    print(
        "STARTING TRAINING"
    )

    print("=" * 70)

    print(
        f"Model      : {MODEL_NAME}"
    )

    print(
        f"Epochs     : {EPOCHS}"
    )

    print(
        f"Patience   : {PATIENCE}"
    )

    print(
        f"Image size : {IMAGE_SIZE}"
    )

    print(
        f"Batch size : {BATCH_SIZE}"
    )

    print()

    model.train(

        data=str(
            data_yaml
        ),

        epochs=EPOCHS,

        patience=PATIENCE,

        imgsz=IMAGE_SIZE,

        batch=BATCH_SIZE,

        device=device,

        workers=2,

        pretrained=True,

        optimizer="auto",

        seed=SEED,

        deterministic=True,

        amp=True,

        plots=True,

        save=True,

        save_period=-1,

        project=str(
            OUTPUT_DIR
            / "training_results"
        ),

        name="YOLO11s_NPK",

        exist_ok=True
    )

    # ========================================================
    # BEST MODEL PATH
    # ========================================================

    best_model_path = (
        OUTPUT_DIR
        / "training_results"
        / "YOLO11s_NPK"
        / "weights"
        / "best.pt"
    )

    if not best_model_path.exists():

        print()
        print(
            "ERROR: best.pt was not found."
        )

        return

    print()
    print("=" * 70)

    print(
        "TRAINING COMPLETE"
    )

    print("=" * 70)

    print()
    print(
        "BEST MODEL:"
    )

    print(
        best_model_path
    )

    # ========================================================
    # TEST FINAL MODEL
    # ========================================================

    print()
    print("=" * 70)

    print(
        "TESTING BEST MODEL"
    )

    print("=" * 70)

    best_model = YOLO(
        str(
            best_model_path
        )
    )

    metrics = best_model.val(

        data=str(
            data_yaml
        ),

        split="test",

        imgsz=IMAGE_SIZE,

        batch=BATCH_SIZE,

        device=device,

        plots=True,

        project=str(
            OUTPUT_DIR
            / "test_results"
        ),

        name="final_test",

        exist_ok=True
    )

    # ========================================================
    # DISPLAY METRICS
    # ========================================================

    print()
    print("=" * 70)

    print(
        "FINAL TEST RESULTS"
    )

    print("=" * 70)

    try:

        print(
            f"Precision : "
            f"{metrics.box.mp:.4f}"
        )

        print(
            f"Recall    : "
            f"{metrics.box.mr:.4f}"
        )

        print(
            f"mAP50     : "
            f"{metrics.box.map50:.4f}"
        )

        print(
            f"mAP50-95  : "
            f"{metrics.box.map:.4f}"
        )

    except Exception:

        print(
            "Metrics are available in "
            "the test_results folder."
        )

    print()
    print("=" * 70)

    print(
        "CHILLI MODEL COMPLETED"
    )

    print("=" * 70)

    print()
    print(
        "FINAL MODEL:"
    )

    print(
        best_model_path
    )

    print()

    print(
        "Classes:"
    )

    print(
        "0 = Healthy"
    )

    print(
        "1 = N_Def"
    )

    print(
        "2 = P_Def"
    )

    print(
        "3 = K_Def"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()