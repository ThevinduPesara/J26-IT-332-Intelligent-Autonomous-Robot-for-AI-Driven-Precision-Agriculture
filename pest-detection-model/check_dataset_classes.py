from pathlib import Path
from collections import Counter

DATASET = Path(r"C:\Users\LENOVO\Downloads\Thevindu_AI_Part\archive")

CLASS_NAMES = {
    0: "MP",
    1: "BT",
    2: "T",
    3: "C"
}


def check_split(split):
    image_dir = DATASET / split / "images"
    label_dir = DATASET / split / "labels"

    image_files = list(image_dir.glob("*.*"))

    images_per_class = Counter()
    boxes_per_class = Counter()

    for label_file in label_dir.glob("*.txt"):

        classes_in_image = set()

        with open(label_file, "r", encoding="utf-8") as file:

            for line in file:
                parts = line.strip().split()

                if len(parts) != 5:
                    continue

                class_id = int(parts[0])

                if class_id not in CLASS_NAMES:
                    continue

                boxes_per_class[class_id] += 1
                classes_in_image.add(class_id)

        for class_id in classes_in_image:
            images_per_class[class_id] += 1

    print(f"\n{split.upper()} DATASET")
    print("-" * 45)

    print(f"Total images : {len(image_files)}")

    print("\nImages containing each class:")

    for class_id, class_name in CLASS_NAMES.items():
        print(
            f"{class_name:<3} : "
            f"{images_per_class[class_id]} images"
        )

    print("\nTotal bounding boxes:")

    for class_id, class_name in CLASS_NAMES.items():
        print(
            f"{class_name:<3} : "
            f"{boxes_per_class[class_id]} boxes"
        )


check_split("train")
check_split("val")