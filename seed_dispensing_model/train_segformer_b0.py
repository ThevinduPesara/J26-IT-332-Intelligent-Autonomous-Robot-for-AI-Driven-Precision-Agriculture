from pathlib import Path
from collections import defaultdict
import csv
import json
import random
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
from pycocotools import mask as mask_utils
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from transformers import SegformerForSemanticSegmentation


# ============================================================
# Configuration
# ============================================================

PROJECT_DIR = Path(
    r"C:\Users\LENOVO\Downloads\yasiru_Ai_part"
)

DATASET_DIR = (
    PROJECT_DIR
    / "paddy field.v1i.coco-segmentation"
)

TRAIN_DIR = (
    DATASET_DIR
    / "train_augmented_3000"
)

VALID_DIR = (
    DATASET_DIR
    / "valid"
)

TEST_DIR = (
    DATASET_DIR
    / "test"
)

TRAIN_JSON = (
    TRAIN_DIR
    / "_annotations.coco.json"
)

VALID_JSON = (
    VALID_DIR
    / "_annotations.coco.json"
)

TEST_JSON = (
    TEST_DIR
    / "_annotations.coco.json"
)

OUTPUT_DIR = (
    PROJECT_DIR
    / "SegFormer_B0_results"
)

BEST_MODEL_PATH = (
    OUTPUT_DIR
    / "best_segformer_b0.pt"
)

HISTORY_CSV = (
    OUTPUT_DIR
    / "training_history.csv"
)

METRICS_JSON = (
    OUTPUT_DIR
    / "test_metrics.json"
)

CURVES_FILE = (
    OUTPUT_DIR
    / "training_curves.png"
)

CONFUSION_FILE = (
    OUTPUT_DIR
    / "test_confusion_matrix.png"
)

PREDICTION_DIR = (
    OUTPUT_DIR
    / "sample_predictions"
)


MODEL_NAME = "nvidia/mit-b0"

CLASSES = {
    0: "Existing plants",
    1: "Soil",
    2: "Weeds",
}

NUM_CLASSES = 3

IMAGE_SIZE = 512

BATCH_SIZE = 4

EPOCHS = 100

LEARNING_RATE = 6e-5

WEIGHT_DECAY = 1e-4

EARLY_STOPPING_PATIENCE = 12

NUM_WORKERS = 2

IGNORE_INDEX = 255

SEED = 42


# SegFormer / ImageNet normalization
MEAN = np.array(
    [0.485, 0.456, 0.406],
    dtype=np.float32,
)

STD = np.array(
    [0.229, 0.224, 0.225],
    dtype=np.float32,
)


# ============================================================
# Reproducibility
# ============================================================

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ============================================================
# JSON utilities
# ============================================================

def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ============================================================
# COCO mask decoding
# ============================================================

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

    elif isinstance(segmentation, dict):

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

        elif isinstance(
            rle.get("counts"),
            str,
        ):
            rle["counts"] = (
                rle["counts"].encode(
                    "ascii"
                )
            )

    else:
        return None

    mask = mask_utils.decode(rle)

    if mask.ndim == 3:
        mask = np.any(
            mask,
            axis=2,
        ).astype(np.uint8)

    return (
        mask > 0
    ).astype(np.uint8)


# ============================================================
# Dataset
# ============================================================

class PaddySegmentationDataset(Dataset):

    def __init__(
        self,
        image_dir,
        annotation_file,
    ):
        self.image_dir = Path(
            image_dir
        )

        coco = load_json(
            annotation_file
        )

        self.images = coco.get(
            "images",
            [],
        )

        categories = {
            item["id"]: item["name"]
            for item in coco.get(
                "categories",
                []
            )
        }

        expected = CLASSES

        if categories != expected:
            print(
                "\nClasses found:"
            )

            for class_id, name in (
                categories.items()
            ):
                print(
                    class_id,
                    name,
                )

            raise ValueError(
                "\nDataset class IDs do not "
                "match expected classes.\n"
                "Expected:\n"
                "0 = Existing plants\n"
                "1 = Soil\n"
                "2 = Weeds"
            )

        self.annotations_by_image = (
            defaultdict(list)
        )

        for annotation in coco.get(
            "annotations",
            [],
        ):
            self.annotations_by_image[
                annotation["image_id"]
            ].append(
                annotation
            )

    def __len__(self):
        return len(self.images)

    def build_semantic_mask(
        self,
        image_info,
        height,
        width,
    ):
        # User-defined default class:
        # all unlabelled pixels = Existing plants = 0
        semantic_mask = np.zeros(
            (height, width),
            dtype=np.uint8,
        )

        annotations = (
            self.annotations_by_image.get(
                image_info["id"],
                [],
            )
        )

        class_masks = {
            0: np.zeros(
                (height, width),
                dtype=np.uint8,
            ),
            1: np.zeros(
                (height, width),
                dtype=np.uint8,
            ),
            2: np.zeros(
                (height, width),
                dtype=np.uint8,
            ),
        }

        for annotation in annotations:

            class_id = int(
                annotation[
                    "category_id"
                ]
            )

            segmentation = annotation.get(
                "segmentation"
            )

            if not segmentation:
                continue

            mask = decode_segmentation(
                segmentation,
                height,
                width,
            )

            if mask is None:
                continue

            class_masks[
                class_id
            ] = np.maximum(
                class_masks[class_id],
                mask,
            )

        # Count annotations from different
        # classes occupying the same pixel.
        annotation_count = (
            class_masks[0]
            + class_masks[1]
            + class_masks[2]
        )

        # Unique Soil pixels
        semantic_mask[
            (class_masks[1] == 1)
            & (annotation_count == 1)
        ] = 1

        # Unique Weed pixels
        semantic_mask[
            (class_masks[2] == 1)
            & (annotation_count == 1)
        ] = 2

        # Explicit Existing plant pixels
        semantic_mask[
            (class_masks[0] == 1)
            & (annotation_count == 1)
        ] = 0

        # Do not guess when annotations overlap.
        semantic_mask[
            annotation_count > 1
        ] = IGNORE_INDEX

        return semantic_mask

    def __getitem__(self, index):

        image_info = self.images[index]

        image_path = (
            self.image_dir
            / image_info["file_name"]
        )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            raise FileNotFoundError(
                f"Cannot read image:\n"
                f"{image_path}"
            )

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        height, width = (
            image.shape[:2]
        )

        mask = self.build_semantic_mask(
            image_info,
            height,
            width,
        )

        image = cv2.resize(
            image,
            (
                IMAGE_SIZE,
                IMAGE_SIZE,
            ),
            interpolation=cv2.INTER_LINEAR,
        )

        mask = cv2.resize(
            mask,
            (
                IMAGE_SIZE,
                IMAGE_SIZE,
            ),
            interpolation=cv2.INTER_NEAREST,
        )

        image = (
            image.astype(
                np.float32
            )
            / 255.0
        )

        image = (
            image - MEAN
        ) / STD

        image = np.transpose(
            image,
            (2, 0, 1),
        )

        image = torch.from_numpy(
            image
        ).float()

        mask = torch.from_numpy(
            mask.astype(
                np.int64
            )
        ).long()

        return (
            image,
            mask,
            image_info["file_name"],
        )


# ============================================================
# Dice loss
# ============================================================

class MulticlassDiceLoss(nn.Module):

    def __init__(
        self,
        num_classes,
        ignore_index=255,
        smooth=1.0,
    ):
        super().__init__()

        self.num_classes = (
            num_classes
        )

        self.ignore_index = (
            ignore_index
        )

        self.smooth = smooth

    def forward(
        self,
        logits,
        targets,
    ):
        probabilities = torch.softmax(
            logits,
            dim=1,
        )

        valid = (
            targets
            != self.ignore_index
        )

        safe_targets = (
            targets.clone()
        )

        safe_targets[
            ~valid
        ] = 0

        one_hot = F.one_hot(
            safe_targets,
            num_classes=self.num_classes,
        )

        one_hot = one_hot.permute(
            0,
            3,
            1,
            2,
        ).float()

        valid_mask = (
            valid.unsqueeze(1)
            .float()
        )

        probabilities = (
            probabilities
            * valid_mask
        )

        one_hot = (
            one_hot
            * valid_mask
        )

        dimensions = (
            0,
            2,
            3,
        )

        intersection = torch.sum(
            probabilities
            * one_hot,
            dimensions,
        )

        denominator = (
            torch.sum(
                probabilities,
                dimensions,
            )
            + torch.sum(
                one_hot,
                dimensions,
            )
        )

        dice = (
            (
                2.0 * intersection
                + self.smooth
            )
            /
            (
                denominator
                + self.smooth
            )
        )

        return (
            1.0
            - dice.mean()
        )


# ============================================================
# Combined loss
# ============================================================

class CombinedLoss(nn.Module):

    def __init__(self):
        super().__init__()

        self.cross_entropy = (
            nn.CrossEntropyLoss(
                ignore_index=IGNORE_INDEX
            )
        )

        self.dice = (
            MulticlassDiceLoss(
                NUM_CLASSES,
                IGNORE_INDEX,
            )
        )

    def forward(
        self,
        logits,
        targets,
    ):
        ce_loss = (
            self.cross_entropy(
                logits,
                targets,
            )
        )

        dice_loss = (
            self.dice(
                logits,
                targets,
            )
        )

        return (
            ce_loss
            + dice_loss
        )


# ============================================================
# Confusion matrix
# ============================================================

def update_confusion_matrix(
    matrix,
    prediction,
    target,
):
    prediction = (
        prediction
        .detach()
        .cpu()
        .numpy()
        .reshape(-1)
    )

    target = (
        target
        .detach()
        .cpu()
        .numpy()
        .reshape(-1)
    )

    valid = (
        target
        != IGNORE_INDEX
    )

    prediction = (
        prediction[valid]
    )

    target = (
        target[valid]
    )

    valid_classes = (
        (target >= 0)
        & (target < NUM_CLASSES)
        & (prediction >= 0)
        & (prediction < NUM_CLASSES)
    )

    target = target[
        valid_classes
    ]

    prediction = prediction[
        valid_classes
    ]

    indices = (
        NUM_CLASSES * target
        + prediction
    )

    counts = np.bincount(
        indices,
        minlength=(
            NUM_CLASSES
            * NUM_CLASSES
        ),
    )

    matrix += counts.reshape(
        NUM_CLASSES,
        NUM_CLASSES,
    )


# ============================================================
# Metrics
# ============================================================

def calculate_metrics(
    confusion_matrix,
):
    metrics = {}

    intersection = np.diag(
        confusion_matrix
    ).astype(np.float64)

    ground_truth = (
        confusion_matrix.sum(
            axis=1
        ).astype(
            np.float64
        )
    )

    predicted = (
        confusion_matrix.sum(
            axis=0
        ).astype(
            np.float64
        )
    )

    union = (
        ground_truth
        + predicted
        - intersection
    )

    iou = np.divide(
        intersection,
        union,
        out=np.zeros_like(
            intersection
        ),
        where=union > 0,
    )

    dice_denominator = (
        ground_truth
        + predicted
    )

    dice = np.divide(
        2.0 * intersection,
        dice_denominator,
        out=np.zeros_like(
            intersection
        ),
        where=(
            dice_denominator > 0
        ),
    )

    precision = np.divide(
        intersection,
        predicted,
        out=np.zeros_like(
            intersection
        ),
        where=predicted > 0,
    )

    recall = np.divide(
        intersection,
        ground_truth,
        out=np.zeros_like(
            intersection
        ),
        where=ground_truth > 0,
    )

    total = (
        confusion_matrix.sum()
    )

    accuracy = (
        intersection.sum()
        / total
        if total > 0
        else 0.0
    )

    metrics[
        "pixel_accuracy"
    ] = float(
        accuracy
    )

    metrics[
        "mean_iou"
    ] = float(
        np.mean(iou)
    )

    metrics[
        "mean_dice"
    ] = float(
        np.mean(dice)
    )

    for class_id, class_name in (
        CLASSES.items()
    ):
        safe_name = (
            class_name
            .lower()
            .replace(" ", "_")
        )

        metrics[
            f"{safe_name}_iou"
        ] = float(
            iou[class_id]
        )

        metrics[
            f"{safe_name}_dice"
        ] = float(
            dice[class_id]
        )

        metrics[
            f"{safe_name}_precision"
        ] = float(
            precision[class_id]
        )

        metrics[
            f"{safe_name}_recall"
        ] = float(
            recall[class_id]
        )

    return metrics


# ============================================================
# Train one epoch
# ============================================================

def train_one_epoch(
    model,
    loader,
    optimizer,
    criterion,
    scaler,
    device,
):
    model.train()

    total_loss = 0.0

    progress = tqdm(
        loader,
        desc="Training",
        leave=False,
    )

    for (
        images,
        masks,
        _,
    ) in progress:

        images = images.to(
            device,
            non_blocking=True,
        )

        masks = masks.to(
            device,
            non_blocking=True,
        )

        optimizer.zero_grad(
            set_to_none=True
        )

        with torch.autocast(
            device_type="cuda",
            dtype=torch.float16,
            enabled=(
                device.type == "cuda"
            ),
        ):
            outputs = model(
                pixel_values=images
            )

            logits = (
                outputs.logits
            )

            logits = F.interpolate(
                logits,
                size=masks.shape[-2:],
                mode="bilinear",
                align_corners=False,
            )

            loss = criterion(
                logits,
                masks,
            )

        scaler.scale(
            loss
        ).backward()

        scaler.step(
            optimizer
        )

        scaler.update()

        total_loss += (
            loss.item()
        )

        progress.set_postfix(
            loss=f"{loss.item():.4f}"
        )

    return (
        total_loss
        / len(loader)
    )


# ============================================================
# Validation / test
# ============================================================

@torch.no_grad()
def evaluate(
    model,
    loader,
    criterion,
    device,
    description,
):
    model.eval()

    total_loss = 0.0

    confusion_matrix = np.zeros(
        (
            NUM_CLASSES,
            NUM_CLASSES,
        ),
        dtype=np.int64,
    )

    progress = tqdm(
        loader,
        desc=description,
        leave=False,
    )

    for (
        images,
        masks,
        _,
    ) in progress:

        images = images.to(
            device,
            non_blocking=True,
        )

        masks = masks.to(
            device,
            non_blocking=True,
        )

        with torch.autocast(
            device_type="cuda",
            dtype=torch.float16,
            enabled=(
                device.type == "cuda"
            ),
        ):
            outputs = model(
                pixel_values=images
            )

            logits = (
                outputs.logits
            )

            logits = F.interpolate(
                logits,
                size=masks.shape[-2:],
                mode="bilinear",
                align_corners=False,
            )

            loss = criterion(
                logits,
                masks,
            )

        predictions = torch.argmax(
            logits,
            dim=1,
        )

        update_confusion_matrix(
            confusion_matrix,
            predictions,
            masks,
        )

        total_loss += (
            loss.item()
        )

    metrics = calculate_metrics(
        confusion_matrix
    )

    average_loss = (
        total_loss
        / len(loader)
    )

    return (
        average_loss,
        metrics,
        confusion_matrix,
    )


# ============================================================
# Training curves
# ============================================================

def save_training_curves(
    history,
):
    epochs = [
        item["epoch"]
        for item in history
    ]

    train_loss = [
        item["train_loss"]
        for item in history
    ]

    val_loss = [
        item["val_loss"]
        for item in history
    ]

    val_iou = [
        item["val_mean_iou"]
        for item in history
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        epochs,
        train_loss,
        label="Train loss",
    )

    plt.plot(
        epochs,
        val_loss,
        label="Validation loss",
    )

    plt.xlabel(
        "Epoch"
    )

    plt.ylabel(
        "Loss"
    )

    plt.title(
        "SegFormer-B0 Training Loss"
    )

    plt.legend()

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        CURVES_FILE,
        dpi=180,
    )

    plt.close()


    miou_file = (
        OUTPUT_DIR
        / "validation_miou.png"
    )

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        epochs,
        val_iou,
    )

    plt.xlabel(
        "Epoch"
    )

    plt.ylabel(
        "Mean IoU"
    )

    plt.title(
        "Validation Mean IoU"
    )

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        miou_file,
        dpi=180,
    )

    plt.close()


# ============================================================
# Confusion matrix
# ============================================================

def save_confusion_matrix(
    matrix,
):
    normalized = (
        matrix.astype(
            np.float64
        )
    )

    row_sum = (
        normalized.sum(
            axis=1,
            keepdims=True,
        )
    )

    normalized = np.divide(
        normalized,
        row_sum,
        out=np.zeros_like(
            normalized
        ),
        where=row_sum != 0,
    )

    plt.figure(
        figsize=(8, 7)
    )

    plt.imshow(
        normalized,
        interpolation="nearest",
    )

    plt.colorbar()

    labels = [
        CLASSES[i]
        for i in range(
            NUM_CLASSES
        )
    ]

    plt.xticks(
        range(NUM_CLASSES),
        labels,
        rotation=30,
        ha="right",
    )

    plt.yticks(
        range(NUM_CLASSES),
        labels,
    )

    plt.xlabel(
        "Predicted class"
    )

    plt.ylabel(
        "True class"
    )

    plt.title(
        "Test Confusion Matrix"
    )

    for i in range(
        NUM_CLASSES
    ):
        for j in range(
            NUM_CLASSES
        ):
            plt.text(
                j,
                i,
                f"{normalized[i, j]:.2f}",
                ha="center",
                va="center",
            )

    plt.tight_layout()

    plt.savefig(
        CONFUSION_FILE,
        dpi=180,
    )

    plt.close()


# ============================================================
# Save sample predictions
# ============================================================

@torch.no_grad()
def save_sample_predictions(
    model,
    dataset,
    device,
    count=12,
):
    PREDICTION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    indices = np.linspace(
        0,
        len(dataset) - 1,
        min(
            count,
            len(dataset),
        ),
        dtype=int,
    )

    colors = np.array(
        [
            [0, 200, 0],
            [190, 130, 60],
            [190, 60, 180],
        ],
        dtype=np.uint8,
    )

    model.eval()

    for number, index in enumerate(
        indices,
        start=1,
    ):
        image_tensor, mask, name = (
            dataset[index]
        )

        input_tensor = (
            image_tensor
            .unsqueeze(0)
            .to(device)
        )

        outputs = model(
            pixel_values=input_tensor
        )

        logits = F.interpolate(
            outputs.logits,
            size=mask.shape[-2:],
            mode="bilinear",
            align_corners=False,
        )

        prediction = (
            torch.argmax(
                logits,
                dim=1,
            )[0]
            .cpu()
            .numpy()
        )

        image = (
            image_tensor
            .numpy()
            .transpose(
                1,
                2,
                0,
            )
        )

        image = (
            image * STD
            + MEAN
        )

        image = np.clip(
            image,
            0,
            1,
        )

        prediction_rgb = (
            colors[prediction]
            / 255.0
        )

        overlay = (
            0.65 * image
            + 0.35 * prediction_rgb
        )

        plt.figure(
            figsize=(12, 5)
        )

        plt.subplot(
            1,
            2,
            1,
        )

        plt.imshow(
            image
        )

        plt.title(
            "Input"
        )

        plt.axis(
            "off"
        )

        plt.subplot(
            1,
            2,
            2,
        )

        plt.imshow(
            overlay
        )

        plt.title(
            "SegFormer-B0 Prediction"
        )

        plt.axis(
            "off"
        )

        plt.tight_layout()

        output_name = (
            PREDICTION_DIR
            / f"{number:02d}_{Path(name).stem}.png"
        )

        plt.savefig(
            output_name,
            dpi=160,
        )

        plt.close()


# ============================================================
# Main
# ============================================================

def main():

    set_seed(
        SEED
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "=" * 72
    )

    print(
        "SEGFORMER-B0 PADDY FIELD SEMANTIC SEGMENTATION"
    )

    print(
        "=" * 72
    )

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"\nDevice: {device}"
    )

    if device.type == "cuda":
        print(
            "GPU:",
            torch.cuda.get_device_name(
                0
            ),
        )

    print(
        "\nClasses:"
    )

    for class_id, class_name in (
        CLASSES.items()
    ):
        print(
            f"{class_id} = "
            f"{class_name}"
        )

    print(
        "\nLoading datasets..."
    )

    train_dataset = (
        PaddySegmentationDataset(
            TRAIN_DIR,
            TRAIN_JSON,
        )
    )

    valid_dataset = (
        PaddySegmentationDataset(
            VALID_DIR,
            VALID_JSON,
        )
    )

    test_dataset = (
        PaddySegmentationDataset(
            TEST_DIR,
            TEST_JSON,
        )
    )

    print(
        f"\nTrain images: "
        f"{len(train_dataset)}"
    )

    print(
        f"Valid images: "
        f"{len(valid_dataset)}"
    )

    print(
        f"Test images : "
        f"{len(test_dataset)}"
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=True,
        persistent_workers=(
            NUM_WORKERS > 0
        ),
    )

    valid_loader = DataLoader(
        valid_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=True,
        persistent_workers=(
            NUM_WORKERS > 0
        ),
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=True,
        persistent_workers=(
            NUM_WORKERS > 0
        ),
    )

    id2label = CLASSES

    label2id = {
        name: class_id
        for class_id, name
        in CLASSES.items()
    }

    print(
        "\nLoading pretrained "
        "SegFormer-B0..."
    )

    model = (
        SegformerForSemanticSegmentation
        .from_pretrained(
            MODEL_NAME,
            num_labels=NUM_CLASSES,
            id2label=id2label,
            label2id=label2id,
            ignore_mismatched_sizes=True,
        )
    )

    model = model.to(
        device
    )

    criterion = (
        CombinedLoss()
    )

    optimizer = (
        torch.optim.AdamW(
            model.parameters(),
            lr=LEARNING_RATE,
            weight_decay=WEIGHT_DECAY,
        )
    )

    scheduler = (
        torch.optim.lr_scheduler
        .CosineAnnealingLR(
            optimizer,
            T_max=EPOCHS,
            eta_min=1e-7,
        )
    )

    scaler = (
        torch.amp.GradScaler(
            "cuda",
            enabled=(
                device.type == "cuda"
            ),
        )
    )

    history = []

    best_miou = -1.0

    epochs_without_improvement = 0

    start_time = time.time()

    print(
        "\nStarting training...\n"
    )

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        print(
            "=" * 72
        )

        print(
            f"EPOCH "
            f"{epoch}/{EPOCHS}"
        )

        print(
            "=" * 72
        )

        train_loss = (
            train_one_epoch(
                model,
                train_loader,
                optimizer,
                criterion,
                scaler,
                device,
            )
        )

        (
            val_loss,
            val_metrics,
            _,
        ) = evaluate(
            model,
            valid_loader,
            criterion,
            device,
            "Validation",
        )

        scheduler.step()

        current_lr = (
            optimizer
            .param_groups[0]["lr"]
        )

        val_miou = (
            val_metrics[
                "mean_iou"
            ]
        )

        val_dice = (
            val_metrics[
                "mean_dice"
            ]
        )

        val_accuracy = (
            val_metrics[
                "pixel_accuracy"
            ]
        )

        print(
            f"\nTrain loss : "
            f"{train_loss:.4f}"
        )

        print(
            f"Val loss   : "
            f"{val_loss:.4f}"
        )

        print(
            f"Val mIoU   : "
            f"{val_miou:.4f}"
        )

        print(
            f"Val Dice   : "
            f"{val_dice:.4f}"
        )

        print(
            f"Val Acc    : "
            f"{val_accuracy:.4f}"
        )

        print(
            f"LR         : "
            f"{current_lr:.8f}"
        )

        for class_id, class_name in (
            CLASSES.items()
        ):

            key = (
                class_name
                .lower()
                .replace(" ", "_")
            )

            print(
                f"{class_name:<18} "
                f"IoU: "
                f"{val_metrics[key + '_iou']:.4f} "
                f"Dice: "
                f"{val_metrics[key + '_dice']:.4f}"
            )

        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_mean_iou": val_miou,
            "val_mean_dice": val_dice,
            "val_pixel_accuracy": (
                val_accuracy
            ),
            "learning_rate": (
                current_lr
            ),
        }

        history.append(
            row
        )

        with open(
            HISTORY_CSV,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=row.keys(),
            )

            writer.writeheader()

            writer.writerows(
                history
            )

        if val_miou > best_miou:

            best_miou = val_miou

            epochs_without_improvement = 0

            checkpoint = {
                "epoch": epoch,
                "model_state_dict":
                    model.state_dict(),
                "optimizer_state_dict":
                    optimizer.state_dict(),
                "best_val_miou":
                    best_miou,
                "classes":
                    CLASSES,
                "image_size":
                    IMAGE_SIZE,
                "model_name":
                    MODEL_NAME,
            }

            torch.save(
                checkpoint,
                BEST_MODEL_PATH,
            )

            print(
                "\nBEST MODEL SAVED"
            )

            print(
                f"Best mIoU: "
                f"{best_miou:.4f}"
            )

        else:

            epochs_without_improvement += 1

            print(
                "\nNo improvement: "
                f"{epochs_without_improvement}/"
                f"{EARLY_STOPPING_PATIENCE}"
            )

        if (
            epochs_without_improvement
            >= EARLY_STOPPING_PATIENCE
        ):
            print(
                "\nEarly stopping."
            )

            break

    total_minutes = (
        time.time()
        - start_time
    ) / 60.0

    save_training_curves(
        history
    )

    print(
        "\n" + "=" * 72
    )

    print(
        "LOADING BEST MODEL"
    )

    print(
        "=" * 72
    )

    checkpoint = torch.load(
        BEST_MODEL_PATH,
        map_location=device,
        weights_only=False,
    )

    model.load_state_dict(
        checkpoint[
            "model_state_dict"
        ]
    )

    print(
        f"Best epoch: "
        f"{checkpoint['epoch']}"
    )

    print(
        f"Best validation mIoU: "
        f"{checkpoint['best_val_miou']:.4f}"
    )

    print(
        "\nTesting on untouched "
        "test dataset..."
    )

    (
        test_loss,
        test_metrics,
        test_confusion,
    ) = evaluate(
        model,
        test_loader,
        criterion,
        device,
        "Testing",
    )

    test_metrics[
        "test_loss"
    ] = float(
        test_loss
    )

    test_metrics[
        "best_epoch"
    ] = int(
        checkpoint["epoch"]
    )

    test_metrics[
        "best_validation_miou"
    ] = float(
        checkpoint[
            "best_val_miou"
        ]
    )

    with open(
        METRICS_JSON,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            test_metrics,
            file,
            indent=4,
        )

    save_confusion_matrix(
        test_confusion
    )

    save_sample_predictions(
        model,
        test_dataset,
        device,
    )

    print(
        "\n" + "=" * 72
    )

    print(
        "FINAL TEST RESULTS"
    )

    print(
        "=" * 72
    )

    print(
        f"\nTest loss      : "
        f"{test_loss:.4f}"
    )

    print(
        f"Pixel accuracy : "
        f"{test_metrics['pixel_accuracy']:.4f}"
    )

    print(
        f"Mean IoU       : "
        f"{test_metrics['mean_iou']:.4f}"
    )

    print(
        f"Mean Dice      : "
        f"{test_metrics['mean_dice']:.4f}"
    )

    print()

    for class_id, class_name in (
        CLASSES.items()
    ):

        key = (
            class_name
            .lower()
            .replace(" ", "_")
        )

        print(
            class_name
        )

        print(
            f"  IoU       : "
            f"{test_metrics[key + '_iou']:.4f}"
        )

        print(
            f"  Dice      : "
            f"{test_metrics[key + '_dice']:.4f}"
        )

        print(
            f"  Precision : "
            f"{test_metrics[key + '_precision']:.4f}"
        )

        print(
            f"  Recall    : "
            f"{test_metrics[key + '_recall']:.4f}"
        )

    print(
        f"\nTraining time: "
        f"{total_minutes:.1f} minutes"
    )

    print(
        f"\nBest model:\n"
        f"{BEST_MODEL_PATH}"
    )

    print(
        f"\nResults:\n"
        f"{OUTPUT_DIR}"
    )

    print(
        "\nTRAINING COMPLETE"
    )


if __name__ == "__main__":
    main()