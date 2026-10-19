from pathlib import Path
from collections import Counter
import csv
import xml.etree.ElementTree as ET


# ============================================================
# PATHS
# ============================================================

XML_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\pepper\pepper\Labels"
)

OUTPUT_FILE = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\dataset_class_summary.csv"
)


# ============================================================
# FUNCTIONS
# ============================================================

def clean_class_name(name):
    return (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def get_condition(class_name):
    """
    Examples:

    healthy_leaf -> healthy
    n_leaf       -> n
    p_leaf       -> p
    k_leaf       -> k
    mg_leaf      -> mg
    zn_leaf      -> zn
    fe_leaf      -> fe
    """

    class_name = clean_class_name(
        class_name
    )

    if "_" in class_name:
        return class_name.split("_")[0]

    return class_name


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("PEPPER DATASET - FULL CLASS CHECK")
    print("=" * 70)

    if not XML_DIR.exists():

        print("ERROR: XML folder not found:")
        print(XML_DIR)

        return

    xml_files = sorted(
        XML_DIR.rglob("*.xml")
    )

    class_counts = Counter()
    condition_counts = Counter()

    total_objects = 0
    malformed_xml = 0
    empty_xml = 0

    # ========================================================
    # READ ALL XML FILES
    # ========================================================

    for index, xml_path in enumerate(
        xml_files,
        start=1
    ):

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

        objects = root.findall(
            "object"
        )

        if not objects:

            empty_xml += 1

            continue

        for obj in objects:

            class_name = (
                obj.findtext("name")
                or "unknown"
            )

            class_name = clean_class_name(
                class_name
            )

            condition = get_condition(
                class_name
            )

            class_counts[
                class_name
            ] += 1

            condition_counts[
                condition
            ] += 1

            total_objects += 1

        if index % 100 == 0:

            print(
                f"Processed "
                f"{index} / "
                f"{len(xml_files)}"
            )

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print()
    print("=" * 70)
    print("NUTRIENT CONDITIONS FOUND")
    print("=" * 70)

    for condition, count in (
        condition_counts.most_common()
    ):

        print(
            f"{condition:<15} "
            f"{count}"
        )

    print()
    print("=" * 70)
    print("ALL XML CLASSES FOUND")
    print("=" * 70)

    for class_name, count in (
        class_counts.most_common()
    ):

        print(
            f"{class_name:<30} "
            f"{count}"
        )

    # ========================================================
    # SAVE ONLY ONE FILE
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "TYPE",
                "NAME",
                "COUNT"
            ]
        )

        # ----------------------------------------------------
        # Dataset summary
        # ----------------------------------------------------

        writer.writerow(
            [
                "SUMMARY",
                "Total XML files",
                len(xml_files)
            ]
        )

        writer.writerow(
            [
                "SUMMARY",
                "Total annotated objects",
                total_objects
            ]
        )

        writer.writerow(
            [
                "SUMMARY",
                "Unique nutrient conditions",
                len(condition_counts)
            ]
        )

        writer.writerow(
            [
                "SUMMARY",
                "Unique XML classes",
                len(class_counts)
            ]
        )

        writer.writerow(
            [
                "SUMMARY",
                "Malformed XML files",
                malformed_xml
            ]
        )

        writer.writerow(
            [
                "SUMMARY",
                "Empty XML files",
                empty_xml
            ]
        )

        # ----------------------------------------------------
        # Nutrient groups
        # ----------------------------------------------------

        for condition, count in (
            condition_counts.most_common()
        ):

            writer.writerow(
                [
                    "NUTRIENT_CONDITION",
                    condition,
                    count
                ]
            )

        # ----------------------------------------------------
        # Detailed classes
        # ----------------------------------------------------

        for class_name, count in (
            class_counts.most_common()
        ):

            writer.writerow(
                [
                    "XML_CLASS",
                    class_name,
                    count
                ]
            )

    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("=" * 70)
    print("CHECK COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Total XML files: "
        f"{len(xml_files)}"
    )

    print(
        f"Total objects: "
        f"{total_objects}"
    )

    print(
        f"Conditions: "
        f"{len(condition_counts)}"
    )

    print(
        f"Classes: "
        f"{len(class_counts)}"
    )

    print(
        f"Bad XML files: "
        f"{malformed_xml}"
    )

    print()
    print("ONE FILE SAVED:")
    print(OUTPUT_FILE)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()