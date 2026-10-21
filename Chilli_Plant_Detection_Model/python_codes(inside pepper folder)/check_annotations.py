from pathlib import Path
from collections import Counter
import csv
import math
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont, ImageOps


# ============================================================
# CONFIGURATION
# ============================================================

IMAGE_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\pepper\pepper\pepper_photo"
)

XML_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\pepper\pepper\Labels"
)

OUTPUT_DIR = Path(
    r"C:\Users\LENOVO\Downloads\Lithira_Ai_part\check_annotation"
)

# Number of matched image/XML pairs to check
MAX_IMAGES = 100

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
}


# ============================================================
# FONT
# ============================================================

def load_font(size=18):

    font_paths = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\calibri.ttf"),
        Path(r"C:\Windows\Fonts\times.ttf"),
    ]

    for font_path in font_paths:

        if font_path.exists():

            try:
                return ImageFont.truetype(
                    str(font_path),
                    size=size
                )

            except Exception:
                pass

    return ImageFont.load_default()


FONT = load_font(18)
SMALL_FONT = load_font(13)


# ============================================================
# BUILD IMAGE INDEX
# ============================================================

def build_image_index():

    filename_index = {}
    stem_index = {}

    for image_path in IMAGE_DIR.rglob("*"):

        if not image_path.is_file():
            continue

        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        filename_index[
            image_path.name.lower()
        ] = image_path

        stem_index.setdefault(
            image_path.stem.lower(),
            []
        ).append(image_path)

    return filename_index, stem_index


# ============================================================
# READ PASCAL VOC XML
# ============================================================

def read_pascal_voc_xml(xml_path):

    tree = ET.parse(xml_path)
    root = tree.getroot()

    filename = (
        root.findtext("filename")
        or ""
    ).strip()

    xml_width = None
    xml_height = None

    size = root.find("size")

    if size is not None:

        try:

            xml_width = int(
                float(
                    size.findtext(
                        "width",
                        "0"
                    )
                )
            )

            xml_height = int(
                float(
                    size.findtext(
                        "height",
                        "0"
                    )
                )
            )

        except Exception:
            pass

    objects = []

    for obj in root.findall("object"):

        class_name = (
            obj.findtext("name")
            or "UNKNOWN"
        ).strip()

        bbox = obj.find("bndbox")

        if bbox is None:

            objects.append(
                {
                    "class_name": class_name,
                    "xmin": None,
                    "ymin": None,
                    "xmax": None,
                    "ymax": None,
                }
            )

            continue

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

            xmin = None
            ymin = None
            xmax = None
            ymax = None

        objects.append(
            {
                "class_name": class_name,
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
            }
        )

    return {
        "filename": filename,
        "xml_width": xml_width,
        "xml_height": xml_height,
        "objects": objects,
    }


# ============================================================
# FIND MATCHING IMAGE
# ============================================================

def find_matching_image(
    xml_path,
    xml_data,
    filename_index,
    stem_index
):

    # --------------------------------------------------------
    # METHOD 1
    # Use <filename> inside XML
    # --------------------------------------------------------

    xml_filename = xml_data["filename"]

    if xml_filename:

        filename_key = Path(
            xml_filename
        ).name.lower()

        if filename_key in filename_index:

            return filename_index[
                filename_key
            ]

    # --------------------------------------------------------
    # METHOD 2
    # Use XML filename stem
    # --------------------------------------------------------

    stem = xml_path.stem.lower()

    matches = stem_index.get(
        stem,
        []
    )

    if len(matches) == 1:

        return matches[0]

    if len(matches) > 1:

        # Prefer JPG first
        priority = {
            ".jpg": 1,
            ".jpeg": 2,
            ".png": 3,
            ".bmp": 4,
            ".tif": 5,
            ".tiff": 6,
        }

        matches = sorted(
            matches,
            key=lambda p: priority.get(
                p.suffix.lower(),
                99
            )
        )

        return matches[0]

    return None


# ============================================================
# CLASS COLOR
# ============================================================

def get_class_color(class_name):

    value = sum(
        ord(character)
        for character in class_name
    )

    red = 70 + (
        value * 47
    ) % 170

    green = 70 + (
        value * 83
    ) % 170

    blue = 70 + (
        value * 131
    ) % 170

    return (
        red,
        green,
        blue
    )


# ============================================================
# DRAW LABEL
# ============================================================

def draw_class_label(
    draw,
    x,
    y,
    text,
    color
):

    text_bbox = draw.textbbox(
        (x, y),
        text,
        font=FONT
    )

    text_width = (
        text_bbox[2]
        - text_bbox[0]
    )

    text_height = (
        text_bbox[3]
        - text_bbox[1]
    )

    padding = 5

    label_top = max(
        0,
        y
        - text_height
        - padding * 2
    )

    draw.rectangle(
        (
            x,
            label_top,
            x
            + text_width
            + padding * 2,
            y
        ),
        fill=color
    )

    draw.text(
        (
            x + padding,
            label_top + padding
        ),
        text,
        fill=(0, 0, 0),
        font=FONT
    )


# ============================================================
# SCALE XML BOUNDING BOX
# ============================================================

def scale_bbox(
    obj,
    xml_width,
    xml_height,
    real_width,
    real_height
):

    xmin = obj["xmin"]
    ymin = obj["ymin"]
    xmax = obj["xmax"]
    ymax = obj["ymax"]

    if None in (
        xmin,
        ymin,
        xmax,
        ymax
    ):

        return None, "Missing bounding-box coordinate"

    # --------------------------------------------------------
    # IMPORTANT FIX
    #
    # If the XML was created using a different resolution
    # than the downloaded image, scale coordinates properly.
    #
    # Example:
    # XML image = 6000 x 4000
    # JPG image = 3000 x 2000
    #
    # scale_x = 0.5
    # scale_y = 0.5
    # --------------------------------------------------------

    scale_x = 1.0
    scale_y = 1.0

    if (
        xml_width
        and xml_height
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

    xmin = int(
        round(
            xmin * scale_x
        )
    )

    xmax = int(
        round(
            xmax * scale_x
        )
    )

    ymin = int(
        round(
            ymin * scale_y
        )
    )

    ymax = int(
        round(
            ymax * scale_y
        )
    )

    # --------------------------------------------------------
    # Clip coordinates only AFTER scaling
    # --------------------------------------------------------

    xmin = max(
        0,
        min(
            xmin,
            real_width - 1
        )
    )

    ymin = max(
        0,
        min(
            ymin,
            real_height - 1
        )
    )

    xmax = max(
        1,
        min(
            xmax,
            real_width
        )
    )

    ymax = max(
        1,
        min(
            ymax,
            real_height
        )
    )

    # --------------------------------------------------------
    # Validate box
    # --------------------------------------------------------

    if xmin >= xmax:

        return (
            None,
            "Invalid box after scaling: xmin >= xmax"
        )

    if ymin >= ymax:

        return (
            None,
            "Invalid box after scaling: ymin >= ymax"
        )

    return (
        (
            xmin,
            ymin,
            xmax,
            ymax
        ),
        ""
    )


# ============================================================
# ANNOTATE ONE IMAGE
# ============================================================

def annotate_image(
    image_path,
    xml_data
):

    image = Image.open(
        image_path
    ).convert("RGB")

    real_width, real_height = (
        image.size
    )

    xml_width = xml_data[
        "xml_width"
    ]

    xml_height = xml_data[
        "xml_height"
    ]

    draw = ImageDraw.Draw(
        image
    )

    object_rows = []

    error_rows = []

    class_counter = Counter()

    # --------------------------------------------------------
    # Calculate scale information
    # --------------------------------------------------------

    if (
        xml_width
        and xml_height
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

    else:

        scale_x = 1.0
        scale_y = 1.0

    # --------------------------------------------------------
    # Draw every annotation
    # --------------------------------------------------------

    for object_number, obj in enumerate(
        xml_data["objects"],
        start=1
    ):

        class_name = (
            obj["class_name"]
            or "UNKNOWN"
        )

        class_counter[
            class_name
        ] += 1

        scaled_box, error = scale_bbox(
            obj,
            xml_width,
            xml_height,
            real_width,
            real_height
        )

        if scaled_box is None:

            error_rows.append(
                {
                    "image": image_path.name,
                    "object_number": object_number,
                    "class_name": class_name,
                    "problem": error,
                }
            )

            continue

        (
            xmin,
            ymin,
            xmax,
            ymax
        ) = scaled_box

        color = get_class_color(
            class_name
        )

        # ----------------------------------------------------
        # Rectangle thickness
        # ----------------------------------------------------

        line_width = max(
            3,
            int(
                min(
                    real_width,
                    real_height
                ) / 300
            )
        )

        draw.rectangle(
            (
                xmin,
                ymin,
                xmax,
                ymax
            ),
            outline=color,
            width=line_width
        )

        # ----------------------------------------------------
        # Class text
        # ----------------------------------------------------

        draw_class_label(
            draw,
            xmin,
            max(
                ymin,
                28
            ),
            class_name,
            color
        )

        object_rows.append(
            {
                "image": image_path.name,
                "class_name": class_name,

                "original_xmin": obj["xmin"],
                "original_ymin": obj["ymin"],
                "original_xmax": obj["xmax"],
                "original_ymax": obj["ymax"],

                "scaled_xmin": xmin,
                "scaled_ymin": ymin,
                "scaled_xmax": xmax,
                "scaled_ymax": ymax,

                "bbox_width": (
                    xmax - xmin
                ),

                "bbox_height": (
                    ymax - ymin
                ),

                "scale_x": round(
                    scale_x,
                    6
                ),

                "scale_y": round(
                    scale_y,
                    6
                ),
            }
        )

    # ========================================================
    # IMAGE INFORMATION BOX
    # ========================================================

    size_status = "SAME SIZE"

    if (
        xml_width
        and xml_height
        and (
            xml_width != real_width
            or xml_height != real_height
        )
    ):

        size_status = "SCALED"

    information_lines = [

        f"Image: {image_path.name}",

        (
            f"Objects: "
            f"{len(object_rows)}"
        ),

        (
            f"Real image: "
            f"{real_width} x "
            f"{real_height}"
        ),

        (
            f"XML image: "
            f"{xml_width} x "
            f"{xml_height}"
        ),

        (
            f"Scale: "
            f"{scale_x:.4f}, "
            f"{scale_y:.4f}"
        ),

        (
            f"Status: "
            f"{size_status}"
        ),
    ]

    y_position = 10

    for information in information_lines:

        text_bbox = draw.textbbox(
            (
                10,
                y_position
            ),
            information,
            font=FONT
        )

        draw.rectangle(
            (
                5,
                y_position - 3,
                text_bbox[2] + 10,
                text_bbox[3] + 5
            ),
            fill=(255, 255, 255)
        )

        draw.text(
            (
                10,
                y_position
            ),
            information,
            fill=(0, 0, 0),
            font=FONT
        )

        y_position += 28

    return (
        image,
        object_rows,
        error_rows,
        class_counter,
        {
            "real_width": real_width,
            "real_height": real_height,
            "xml_width": xml_width,
            "xml_height": xml_height,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "size_status": size_status,
        }
    )


# ============================================================
# CREATE CONTACT SHEET
# ============================================================

def create_contact_sheet(
    image_paths
):

    if not image_paths:
        return None

    columns = 4

    thumbnail_width = 320
    thumbnail_height = 220

    label_height = 30

    rows = math.ceil(
        len(image_paths)
        / columns
    )

    sheet_width = (
        columns
        * thumbnail_width
    )

    sheet_height = (
        rows
        * (
            thumbnail_height
            + label_height
        )
    )

    contact_sheet = Image.new(
        "RGB",
        (
            sheet_width,
            sheet_height
        ),
        "white"
    )

    draw = ImageDraw.Draw(
        contact_sheet
    )

    for index, image_path in enumerate(
        image_paths
    ):

        row = (
            index
            // columns
        )

        column = (
            index
            % columns
        )

        with Image.open(
            image_path
        ) as image:

            image = image.convert(
                "RGB"
            )

            preview = ImageOps.contain(
                image,
                (
                    thumbnail_width - 10,
                    thumbnail_height - 10
                )
            )

        x = (
            column
            * thumbnail_width
            + (
                thumbnail_width
                - preview.width
            ) // 2
        )

        y = (
            row
            * (
                thumbnail_height
                + label_height
            )
            + 5
        )

        contact_sheet.paste(
            preview,
            (
                x,
                y
            )
        )

        filename = (
            image_path.name
        )

        if len(filename) > 40:

            filename = (
                filename[:37]
                + "..."
            )

        draw.text(
            (
                column
                * thumbnail_width
                + 5,

                row
                * (
                    thumbnail_height
                    + label_height
                )
                + thumbnail_height
                + 5
            ),
            filename,
            fill=(0, 0, 0),
            font=SMALL_FONT
        )

    contact_sheet_path = (
        OUTPUT_DIR
        / "contact_sheet_first_100.jpg"
    )

    contact_sheet.save(
        contact_sheet_path,
        quality=90
    )

    return contact_sheet_path


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print(
        "CHILLI PEPPER DATASET "
        "ANNOTATION CHECKER"
    )
    print("=" * 75)

    # ========================================================
    # CHECK INPUT FOLDERS
    # ========================================================

    if not IMAGE_DIR.exists():

        print()
        print(
            "ERROR: Image folder "
            "does not exist:"
        )

        print(
            IMAGE_DIR
        )

        return

    if not XML_DIR.exists():

        print()
        print(
            "ERROR: XML folder "
            "does not exist:"
        )

        print(
            XML_DIR
        )

        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # INDEX IMAGES
    # ========================================================

    (
        filename_index,
        stem_index
    ) = build_image_index()

    total_images = sum(
        len(paths)
        for paths in stem_index.values()
    )

    xml_files = sorted(
        XML_DIR.rglob("*.xml"),
        key=lambda p: p.name.lower()
    )

    print()
    print(
        f"Images found     : "
        f"{total_images}"
    )

    print(
        f"XML files found  : "
        f"{len(xml_files)}"
    )

    # ========================================================
    # MATCH XML + IMAGE
    # ========================================================

    matched_pairs = []

    error_rows = []

    malformed_xml_count = 0

    for xml_path in xml_files:

        try:

            xml_data = (
                read_pascal_voc_xml(
                    xml_path
                )
            )

        except ET.ParseError as error:

            malformed_xml_count += 1

            error_rows.append(
                {
                    "xml_file": xml_path.name,
                    "image": "",
                    "problem": (
                        "Malformed XML: "
                        f"{error}"
                    ),
                }
            )

            print(
                f"[BAD XML] "
                f"{xml_path.name}: "
                f"{error}"
            )

            continue

        except Exception as error:

            error_rows.append(
                {
                    "xml_file": xml_path.name,
                    "image": "",
                    "problem": (
                        "XML read error: "
                        f"{error}"
                    ),
                }
            )

            continue

        image_path = find_matching_image(
            xml_path,
            xml_data,
            filename_index,
            stem_index
        )

        if image_path is None:

            error_rows.append(
                {
                    "xml_file": xml_path.name,
                    "image": "",
                    "problem": (
                        "Matching image "
                        "not found"
                    ),
                }
            )

            continue

        matched_pairs.append(
            (
                xml_path,
                image_path,
                xml_data
            )
        )

    print()
    print(
        f"Matched pairs    : "
        f"{len(matched_pairs)}"
    )

    print(
        f"Malformed XML    : "
        f"{malformed_xml_count}"
    )

    if not matched_pairs:

        print()
        print(
            "No valid matched pairs "
            "were found."
        )

        return

    # ========================================================
    # SELECT FIRST 100
    # ========================================================

    selected_pairs = (
        matched_pairs[:MAX_IMAGES]
    )

    print(
        f"Images to check  : "
        f"{len(selected_pairs)}"
    )

    print()
    print("-" * 75)

    # ========================================================
    # PROCESS ANNOTATIONS
    # ========================================================

    saved_images = []

    summary_rows = []

    object_rows = []

    total_class_counts = Counter()

    scaled_image_count = 0

    same_size_count = 0

    for index, (
        xml_path,
        image_path,
        xml_data
    ) in enumerate(
        selected_pairs,
        start=1
    ):

        try:

            (
                annotated_image,
                local_object_rows,
                local_errors,
                class_counts,
                size_info
            ) = annotate_image(
                image_path,
                xml_data
            )

            # ------------------------------------------------
            # Count resolution mismatches
            # ------------------------------------------------

            if (
                size_info[
                    "size_status"
                ]
                == "SCALED"
            ):

                scaled_image_count += 1

            else:

                same_size_count += 1

            # ------------------------------------------------
            # Save checked image
            # ------------------------------------------------

            output_filename = (
                f"{index:03d}_"
                f"{image_path.stem}"
                f"_checked.jpg"
            )

            output_path = (
                OUTPUT_DIR
                / output_filename
            )

            annotated_image.save(
                output_path,
                quality=95
            )

            saved_images.append(
                output_path
            )

            # ------------------------------------------------
            # Collect object information
            # ------------------------------------------------

            object_rows.extend(
                local_object_rows
            )

            total_class_counts.update(
                class_counts
            )

            for local_error in local_errors:

                local_error[
                    "xml_file"
                ] = xml_path.name

                error_rows.append(
                    local_error
                )

            classes_text = ", ".join(
                sorted(
                    class_counts.keys()
                )
            )

            summary_rows.append(
                {
                    "number": index,

                    "image_file": (
                        image_path.name
                    ),

                    "xml_file": (
                        xml_path.name
                    ),

                    "output_file": (
                        output_filename
                    ),

                    "object_count": (
                        len(
                            local_object_rows
                        )
                    ),

                    "classes": (
                        classes_text
                    ),

                    "real_width": (
                        size_info[
                            "real_width"
                        ]
                    ),

                    "real_height": (
                        size_info[
                            "real_height"
                        ]
                    ),

                    "xml_width": (
                        size_info[
                            "xml_width"
                        ]
                    ),

                    "xml_height": (
                        size_info[
                            "xml_height"
                        ]
                    ),

                    "scale_x": round(
                        size_info[
                            "scale_x"
                        ],
                        6
                    ),

                    "scale_y": round(
                        size_info[
                            "scale_y"
                        ],
                        6
                    ),

                    "size_status": (
                        size_info[
                            "size_status"
                        ]
                    ),
                }
            )

            print(
                f"[{index:03d}/"
                f"{len(selected_pairs):03d}] "
                f"{image_path.name}"
            )

            print(
                f"      Objects : "
                f"{len(local_object_rows)}"
            )

            print(
                f"      Classes : "
                f"{classes_text}"
            )

            print(
                f"      Image   : "
                f"{size_info['real_width']} x "
                f"{size_info['real_height']}"
            )

            print(
                f"      XML     : "
                f"{size_info['xml_width']} x "
                f"{size_info['xml_height']}"
            )

            print(
                f"      Scale   : "
                f"{size_info['scale_x']:.4f}, "
                f"{size_info['scale_y']:.4f}"
            )

            print()

        except Exception as error:

            print(
                f"[ERROR] "
                f"{image_path.name}"
            )

            print(
                f"        {error}"
            )

            print()

            error_rows.append(
                {
                    "xml_file": (
                        xml_path.name
                    ),

                    "image": (
                        image_path.name
                    ),

                    "problem": str(
                        error
                    ),
                }
            )

    # ========================================================
    # SAVE SUMMARY CSV
    # ========================================================

    summary_csv = (
        OUTPUT_DIR
        / "annotation_summary.csv"
    )

    summary_fields = [
        "number",
        "image_file",
        "xml_file",
        "output_file",
        "object_count",
        "classes",
        "real_width",
        "real_height",
        "xml_width",
        "xml_height",
        "scale_x",
        "scale_y",
        "size_status",
    ]

    with open(
        summary_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=summary_fields
        )

        writer.writeheader()

        writer.writerows(
            summary_rows
        )

    # ========================================================
    # SAVE OBJECT DETAILS CSV
    # ========================================================

    object_csv = (
        OUTPUT_DIR
        / "object_details.csv"
    )

    object_fields = [
        "image",
        "class_name",

        "original_xmin",
        "original_ymin",
        "original_xmax",
        "original_ymax",

        "scaled_xmin",
        "scaled_ymin",
        "scaled_xmax",
        "scaled_ymax",

        "bbox_width",
        "bbox_height",

        "scale_x",
        "scale_y",
    ]

    with open(
        object_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=object_fields
        )

        writer.writeheader()

        writer.writerows(
            object_rows
        )

    # ========================================================
    # CLASS COUNTS CSV
    # ========================================================

    class_csv = (
        OUTPUT_DIR
        / "class_counts.csv"
    )

    with open(
        class_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "class_name",
                "object_count"
            ]
        )

        for (
            class_name,
            count
        ) in total_class_counts.most_common():

            writer.writerow(
                [
                    class_name,
                    count
                ]
            )

    # ========================================================
    # ERROR REPORT CSV
    # ========================================================

    error_csv = (
        OUTPUT_DIR
        / "annotation_errors.csv"
    )

    if error_rows:

        error_fields = sorted(
            {
                key
                for row in error_rows
                for key in row.keys()
            }
        )

        with open(
            error_csv,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=error_fields
            )

            writer.writeheader()

            writer.writerows(
                error_rows
            )

    else:

        with open(
            error_csv,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow(
                [
                    "status"
                ]
            )

            writer.writerow(
                [
                    "No errors found"
                ]
            )

    # ========================================================
    # CONTACT SHEET
    # ========================================================

    contact_sheet_path = (
        create_contact_sheet(
            saved_images
        )
    )

    # ========================================================
    # SAVE TEXT REPORT
    # ========================================================

    report_path = (
        OUTPUT_DIR
        / "annotation_check_report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "CHILLI PEPPER DATASET "
            "ANNOTATION CHECK REPORT\n"
        )

        file.write(
            "=" * 60
            + "\n\n"
        )

        file.write(
            f"Image directory:\n"
            f"{IMAGE_DIR}\n\n"
        )

        file.write(
            f"XML directory:\n"
            f"{XML_DIR}\n\n"
        )

        file.write(
            f"Images found: "
            f"{total_images}\n"
        )

        file.write(
            f"XML files found: "
            f"{len(xml_files)}\n"
        )

        file.write(
            f"Matched pairs: "
            f"{len(matched_pairs)}\n"
        )

        file.write(
            f"Images checked: "
            f"{len(saved_images)}\n"
        )

        file.write(
            f"Images requiring "
            f"coordinate scaling: "
            f"{scaled_image_count}\n"
        )

        file.write(
            f"Same-size XML/images: "
            f"{same_size_count}\n"
        )

        file.write(
            f"Malformed XML files: "
            f"{malformed_xml_count}\n"
        )

        file.write(
            f"Total annotated objects: "
            f"{sum(total_class_counts.values())}"
            f"\n"
        )

        file.write(
            f"Warnings/errors: "
            f"{len(error_rows)}\n\n"
        )

        file.write(
            "CLASSES FOUND\n"
        )

        file.write(
            "-" * 40
            + "\n"
        )

        for (
            class_name,
            count
        ) in total_class_counts.most_common():

            file.write(
                f"{class_name}: "
                f"{count}\n"
            )

        file.write(
            "\nIMPORTANT\n"
        )

        file.write(
            "-" * 40
            + "\n"
        )

        file.write(
            "Bounding boxes were scaled "
            "when the XML annotation size "
            "was different from the real "
            "downloaded image size.\n"
        )

        file.write(
            "This prevents coordinates from "
            "being incorrectly clipped to "
            "the right or bottom image edge.\n"
        )

    # ========================================================
    # FINAL TERMINAL SUMMARY
    # ========================================================

    print()
    print("=" * 75)
    print(
        "ANNOTATION CHECK COMPLETE"
    )
    print("=" * 75)

    print()

    print(
        f"Checked images              : "
        f"{len(saved_images)}"
    )

    print(
        f"Images with size scaling    : "
        f"{scaled_image_count}"
    )

    print(
        f"Images with same size       : "
        f"{same_size_count}"
    )

    print(
        f"Total annotated objects     : "
        f"{sum(total_class_counts.values())}"
    )

    print(
        f"Malformed XML files         : "
        f"{malformed_xml_count}"
    )

    print(
        f"Warnings / errors           : "
        f"{len(error_rows)}"
    )

    print()
    print(
        "CLASSES FOUND"
    )

    print("-" * 50)

    for (
        class_name,
        count
    ) in total_class_counts.most_common():

        print(
            f"{class_name:<30}"
            f"{count}"
        )

    print()
    print("=" * 75)

    print(
        "RESULTS SAVED TO:"
    )

    print(
        OUTPUT_DIR
    )

    print()
    print(
        "FIRST OPEN:"
    )

    print(
        contact_sheet_path
    )

    print()
    print(
        "THEN CHECK:"
    )

    print(
        summary_csv
    )

    print(
        error_csv
    )

    print(
        report_path
    )

    print("=" * 75)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()