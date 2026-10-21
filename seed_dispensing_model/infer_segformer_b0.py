from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from transformers import SegformerConfig, SegformerForSemanticSegmentation


PROJECT_DIR = Path(
    r"C:\Users\LENOVO\Downloads\yasiru_Ai_part"
)

MODEL_PATH = (
    PROJECT_DIR
    / "SegFormer_B0_results"
    / "best_segformer_b0.pt"
)

TEST_DIR = (
    PROJECT_DIR
    / "paddy field.v1i.coco-segmentation"
    / "test"
)

OUTPUT_DIR = (
    PROJECT_DIR
    / "SegFormer_B0_results"
    / "inference_results"
)

IMAGE_SIZE = 512

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

MEAN = np.array(
    [0.485, 0.456, 0.406],
    dtype=np.float32,
)

STD = np.array(
    [0.229, 0.224, 0.225],
    dtype=np.float32,
)


def load_model(device):
    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
        weights_only=False,
    )

    model_name = checkpoint.get(
        "model_name",
        "nvidia/mit-b0",
    )

    config = SegformerConfig.from_pretrained(
        model_name
    )

    config.num_labels = 3

    config.id2label = CLASSES

    config.label2id = {
        name: idx
        for idx, name in CLASSES.items()
    }

    model = SegformerForSemanticSegmentation(
        config
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
    model.eval()

    print(
        f"Loaded best epoch: "
        f"{checkpoint.get('epoch')}"
    )

    print(
        f"Best validation mIoU: "
        f"{checkpoint.get('best_val_miou'):.4f}"
    )

    return model


def preprocess(image):
    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    resized = cv2.resize(
        rgb,
        (IMAGE_SIZE, IMAGE_SIZE),
        interpolation=cv2.INTER_LINEAR,
    )

    resized = (
        resized.astype(np.float32)
        / 255.0
    )

    resized = (
        resized - MEAN
    ) / STD

    resized = np.transpose(
        resized,
        (2, 0, 1),
    )

    tensor = torch.from_numpy(
        resized
    ).float()

    return tensor.unsqueeze(0)


@torch.no_grad()
def predict(model, image, device):
    original_height, original_width = (
        image.shape[:2]
    )

    input_tensor = preprocess(
        image
    ).to(device)

    outputs = model(
        pixel_values=input_tensor
    )

    logits = F.interpolate(
        outputs.logits,
        size=(
            original_height,
            original_width,
        ),
        mode="bilinear",
        align_corners=False,
    )

    probabilities = torch.softmax(
        logits,
        dim=1,
    )

    prediction = torch.argmax(
        probabilities,
        dim=1,
    )[0].cpu().numpy()

    confidence = torch.max(
        probabilities,
        dim=1,
    ).values[0].cpu().numpy()

    return prediction, confidence


def create_overlay(
    image,
    prediction,
):
    mask_rgb = np.zeros_like(
        image
    )

    for class_id, color in COLORS.items():
        mask_rgb[
            prediction == class_id
        ] = color

    overlay = cv2.addWeighted(
        image,
        0.60,
        mask_rgb,
        0.40,
        0,
    )

    return overlay, mask_rgb


def add_legend(image):
    output = image.copy()

    x = 20
    y = 30

    for class_id, class_name in (
        CLASSES.items()
    ):
        color = COLORS[class_id]

        cv2.rectangle(
            output,
            (x, y - 15),
            (x + 20, y + 5),
            color,
            -1,
        )

        cv2.putText(
            output,
            class_name,
            (x + 30, y + 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        y += 30

    return output


def process_image(
    model,
    image_path,
    device,
):
    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        print(
            f"Cannot read: {image_path}"
        )
        return

    prediction, confidence = predict(
        model,
        image,
        device,
    )

    overlay, mask_rgb = create_overlay(
        image,
        prediction,
    )

    overlay = add_legend(
        overlay
    )

    combined = np.hstack(
        [
            image,
            overlay,
            mask_rgb,
        ]
    )

    output_path = (
        OUTPUT_DIR
        / f"{image_path.stem}_prediction.jpg"
    )

    cv2.imwrite(
        str(output_path),
        combined,
    )

    total_pixels = prediction.size

    print(
        f"\n{image_path.name}"
    )

    for class_id, class_name in (
        CLASSES.items()
    ):
        pixels = np.sum(
            prediction == class_id
        )

        percentage = (
            pixels
            / total_pixels
            * 100
        )

        print(
            f"{class_name:<18}: "
            f"{percentage:6.2f}%"
        )

    print(
        f"Mean confidence      : "
        f"{confidence.mean():.4f}"
    )

    print(
        f"Saved                : "
        f"{output_path}"
    )


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"Device: {device}"
    )

    if device.type == "cuda":
        print(
            torch.cuda.get_device_name(0)
        )

    model = load_model(
        device
    )

    image_files = []

    for extension in (
        "*.jpg",
        "*.jpeg",
        "*.png",
        "*.JPG",
    ):
        image_files.extend(
            TEST_DIR.glob(extension)
        )

    image_files = [
        path
        for path in image_files
        if not path.name.startswith("_")
    ]

    if not image_files:
        raise RuntimeError(
            "No test images found."
        )

    print(
        f"\nImages found: "
        f"{len(image_files)}"
    )

    for image_path in image_files:
        process_image(
            model,
            image_path,
            device,
        )

    print(
        "\nInference complete."
    )

    print(
        f"Results:\n{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()