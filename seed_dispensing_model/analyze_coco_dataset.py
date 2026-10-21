from pathlib import Path
from collections import Counter, defaultdict
import csv
import json


PROJECT_DIR = Path(r"C:\Users\LENOVO\Downloads\yasiru_Ai_part")

DATASET_DIR = (
    PROJECT_DIR
    / "paddy field.v1i.coco-segmentation"
)

SPLITS = {
    "train": DATASET_DIR / "train",
    "valid": DATASET_DIR / "valid",
    "test": DATASET_DIR / "test",
}

SUMMARY_CSV = PROJECT_DIR / "coco_dataset_summary.csv"
REPORT_FILE = PROJECT_DIR / "coco_dataset_report.txt"


def find_annotation_file(split_dir: Path):
    preferred = split_dir / "_annotations.coco.json"

    if preferred.exists():
        return preferred

    json_files = list(split_dir.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No COCO annotation file found in:\n{split_dir}"
        )

    return json_files[0]


def load_coco(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def analyse_split(split_name: str, split_dir: Path):
    annotation_file = find_annotation_file(split_dir)
    coco = load_coco(annotation_file)

    images = coco.get("images", [])
    annotations = coco.get("annotations", [])
    categories = coco.get("categories", [])

    image_ids = {
        image["id"]
        for image in images
    }

    category_names = {
        category["id"]: category["name"]
        for category in categories
    }

    annotation_count = Counter()
    image_count_by_class = defaultdict(set)
    segmentation_count = Counter()

    images_with_annotations = set()

    invalid_image_references = 0
    invalid_category_references = 0
    missing_segmentations = 0

    for annotation in annotations:
        image_id = annotation.get("image_id")
        category_id = annotation.get("category_id")

        if image_id not in image_ids:
            invalid_image_references += 1
            continue

        if category_id not in category_names:
            invalid_category_references += 1
            continue

        annotation_count[category_id] += 1
        image_count_by_class[category_id].add(image_id)
        images_with_annotations.add(image_id)

        segmentation = annotation.get("segmentation")

        if segmentation:
            segmentation_count[category_id] += 1
        else:
            missing_segmentations += 1

    empty_images = image_ids - images_with_annotations

    result = {
        "split": split_name,
        "annotation_file": annotation_file,
        "total_images": len(images),
        "total_annotations": len(annotations),
        "total_classes": len(categories),
        "empty_images": len(empty_images),
        "invalid_image_references": invalid_image_references,
        "invalid_category_references": invalid_category_references,
        "missing_segmentations": missing_segmentations,
        "classes": [],
    }

    for category in categories:
        category_id = category["id"]
        class_name = category["name"]

        class_images = len(
            image_count_by_class[category_id]
        )

        masks = segmentation_count[category_id]
        annotations_for_class = annotation_count[category_id]

        image_percentage = (
            class_images / len(images) * 100
            if images
            else 0
        )

        result["classes"].append(
            {
                "class_id": category_id,
                "class_name": class_name,
                "images": class_images,
                "image_percentage": image_percentage,
                "annotations": annotations_for_class,
                "masks": masks,
            }
        )

    return result


def print_split(result):
    print("\n" + "=" * 72)
    print(f"{result['split'].upper()} DATASET")
    print("=" * 72)

    print(f"Images             : {result['total_images']}")
    print(f"Annotations        : {result['total_annotations']}")
    print(f"Classes            : {result['total_classes']}")
    print(f"Images with no mask: {result['empty_images']}")

    print("\nClass distribution")
    print("-" * 72)

    print(
        f"{'ID':<5}"
        f"{'Class':<22}"
        f"{'Images':>10}"
        f"{'Masks':>10}"
        f"{'Image %':>12}"
    )

    print("-" * 72)

    for item in result["classes"]:
        print(
            f"{item['class_id']:<5}"
            f"{item['class_name']:<22}"
            f"{item['images']:>10}"
            f"{item['masks']:>10}"
            f"{item['image_percentage']:>11.1f}%"
        )

    print("\nAnnotation checks")
    print("-" * 72)

    print(
        f"Invalid image references   : "
        f"{result['invalid_image_references']}"
    )

    print(
        f"Invalid category references: "
        f"{result['invalid_category_references']}"
    )

    print(
        f"Annotations without masks  : "
        f"{result['missing_segmentations']}"
    )


def save_csv(results):
    rows = []

    for result in results:
        for item in result["classes"]:
            rows.append(
                {
                    "split": result["split"],
                    "total_images": result["total_images"],
                    "class_id": item["class_id"],
                    "class_name": item["class_name"],
                    "images_containing_class": item["images"],
                    "image_percentage": round(
                        item["image_percentage"], 2
                    ),
                    "annotations": item["annotations"],
                    "segmentation_masks": item["masks"],
                }
            )

    with open(
        SUMMARY_CSV,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "split",
                "total_images",
                "class_id",
                "class_name",
                "images_containing_class",
                "image_percentage",
                "annotations",
                "segmentation_masks",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)


def save_report(results):
    lines = []

    lines.append(
        "COCO SEGMENTATION DATASET ANALYSIS"
    )
    lines.append("=" * 60)

    for result in results:
        lines.append("")
        lines.append(
            f"{result['split'].upper()} DATASET"
        )
        lines.append("-" * 60)

        lines.append(
            f"Total images: {result['total_images']}"
        )

        lines.append(
            f"Total annotations: "
            f"{result['total_annotations']}"
        )

        lines.append(
            f"Images without annotations: "
            f"{result['empty_images']}"
        )

        lines.append("")

        for item in result["classes"]:
            lines.append(
                f"{item['class_name']}: "
                f"{item['images']} images, "
                f"{item['masks']} masks"
            )

        lines.append("")
        lines.append(
            f"Invalid image references: "
            f"{result['invalid_image_references']}"
        )

        lines.append(
            f"Invalid category references: "
            f"{result['invalid_category_references']}"
        )

        lines.append(
            f"Missing segmentations: "
            f"{result['missing_segmentations']}"
        )

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main():
    results = []

    print("=" * 72)
    print("PADDY FIELD COCO SEGMENTATION DATASET ANALYSIS")
    print("=" * 72)

    for split_name, split_dir in SPLITS.items():
        if not split_dir.exists():
            print(
                f"\n{split_name} folder not found:\n"
                f"{split_dir}"
            )
            continue

        result = analyse_split(
            split_name,
            split_dir,
        )

        results.append(result)

        print_split(result)

    if not results:
        raise RuntimeError(
            "No dataset splits were found."
        )

    save_csv(results)
    save_report(results)

    print("\n" + "=" * 72)
    print("ANALYSIS COMPLETE")
    print("=" * 72)

    print(
        f"\nCSV summary:\n{SUMMARY_CSV}"
    )

    print(
        f"\nText report:\n{REPORT_FILE}"
    )


if __name__ == "__main__":
    main()