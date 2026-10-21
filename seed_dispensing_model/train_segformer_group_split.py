from pathlib import Path
from collections import defaultdict
import csv
import json
import random
import re
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
from pycocotools import mask as mask_utils
from tqdm import tqdm

import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import SegformerForSemanticSegmentation


PROJECT_DIR = Path(r"C:\Users\LENOVO\Downloads\yasiru_Ai_part")
DATASET_DIR = PROJECT_DIR / "paddy field.v1i.coco-segmentation"
AUG_DIR = DATASET_DIR / "train_augmented_3000"
AUG_JSON = AUG_DIR / "_annotations.coco.json"
FINAL_TEST_DIR = DATASET_DIR / "valid"
INFERENCE_DIR = DATASET_DIR / "test"
OUTPUT_DIR = PROJECT_DIR / "SegFormer_B0_GroupSplit_Fixed"

MODEL_NAME = "nvidia/mit-b0"
CLASSES = {0: "Existing plants", 1: "Soil", 2: "Weeds"}
NUM_CLASSES = len(CLASSES)
IGNORE_INDEX = 255
IMAGE_SIZE = 512
BATCH_SIZE = 4
EPOCHS = 100
PATIENCE = 12
LEARNING_RATE = 6e-5
WEIGHT_DECAY = 1e-4
VAL_FRACTION = 0.20
WORKERS = 2
SEED = 42

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
COLORS_BGR = {0: (0, 200, 0), 1: (70, 150, 220), 2: (180, 70, 180)}


def load_coco(path):
    if not path.is_file():
        raise FileNotFoundError(f"COCO JSON not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        coco = json.load(file)
    categories = {int(c["id"]): c["name"] for c in coco["categories"]}
    if categories != CLASSES:
        raise ValueError(f"Unexpected classes in {path}: {categories}\nExpected: {CLASSES}")
    return coco


def split_augmented_images(coco):
    """Recover source-image groups from augment_safe_3000.py naming/order."""
    originals = {}
    augments = []

    for image in coco["images"]:
        name = Path(image["file_name"]).stem
        original_match = re.fullmatch(r"original_(\d+)", name)
        augment_match = re.fullmatch(r"aug_(\d+)", name)
        if original_match:
            originals[int(original_match.group(1))] = image
        elif augment_match:
            augments.append((int(augment_match.group(1)), image))
        else:
            raise ValueError(f"Unknown image naming pattern: {name}")

    count = len(originals)
    if count < 5 or set(originals) != set(range(1, count + 1)):
        raise ValueError("Original filenames must be original_00001 ... original_XXXXX without gaps.")

    all_numbers = set(originals)
    all_numbers.update(number for number, _ in augments)
    if len(all_numbers) != len(coco["images"]) or all_numbers != set(range(1, len(coco["images"]) + 1)):
        raise ValueError("The generated sample numbering is missing or duplicated. Rebuild augmentation first.")

    rng = random.Random(SEED)
    groups = list(range(1, count + 1))
    rng.shuffle(groups)
    num_val = max(1, min(count - 1, round(count * VAL_FRACTION)))
    valid_group_ids = set(groups[:num_val])
    train_group_ids = set(groups[num_val:])

    train_images = [originals[i] for i in sorted(train_group_ids)]
    valid_images = [originals[i] for i in sorted(valid_group_ids)]

    # The earlier augmentation script processes sources in round-robin order.
    # Augmented sample N+1 is from original 1, sample N+2 from original 2, etc.
    for number, image in augments:
        source_id = ((number - count - 1) % count) + 1
        if source_id in train_group_ids:
            train_images.append(image)

    assert not set(x["id"] for x in train_images) & set(x["id"] for x in valid_images)
    manifest = {
        "source_original_count": count,
        "train_source_ids": sorted(train_group_ids),
        "validation_source_ids": sorted(valid_group_ids),
        "train_sample_count": len(train_images),
        "validation_original_count": len(valid_images),
        "note": "Augmented group recovery assumes no skipped augmentation attempts during original generation."
    }
    return train_images, valid_images, manifest


def decode_mask(segmentation, height, width):
    if isinstance(segmentation, list):
        rles = mask_utils.frPyObjects(segmentation, height, width)
        rle = mask_utils.merge(rles)
    elif isinstance(segmentation, dict):
        rle = segmentation.copy()
        if isinstance(rle.get("counts"), list):
            rle = mask_utils.frPyObjects(rle, height, width)
        elif isinstance(rle.get("counts"), str):
            rle["counts"] = rle["counts"].encode("ascii")
    else:
        raise ValueError("Invalid COCO segmentation")
    result = mask_utils.decode(rle)
    if result.ndim == 3:
        result = np.any(result, axis=2)
    if result.shape != (height, width):
        raise ValueError(f"Mask shape {result.shape} != image shape {(height, width)}")
    return result.astype(bool)


class CocoSegDataset(Dataset):
    def __init__(self, image_dir, coco, images=None):
        self.image_dir = Path(image_dir)
        self.images = list(coco["images"] if images is None else images)
        self.annotations = defaultdict(list)
        for ann in coco["annotations"]:
            self.annotations[ann["image_id"]].append(ann)
        if not self.images:
            raise ValueError(f"Empty dataset: {image_dir}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        info = self.images[index]
        path = self.image_dir / info["file_name"]
        image = cv2.imread(str(path))
        if image is None:
            raise FileNotFoundError(f"Could not load image: {path}")

        height, width = image.shape[:2]
        class_masks = np.zeros((NUM_CLASSES, height, width), dtype=np.uint8)
        for ann in self.annotations[info["id"]]:
            class_id = int(ann["category_id"])
            decoded = decode_mask(ann["segmentation"], height, width)
            class_masks[class_id] |= decoded.astype(np.uint8)

        # Matches the previous training pipeline: unannotated pixels are class 0.
        # This assumption must be checked against actual annotation coverage.
        mask = np.zeros((height, width), dtype=np.uint8)
        overlap = class_masks.sum(axis=0) > 1
        mask[class_masks[1] > 0] = 1
        mask[class_masks[2] > 0] = 2
        mask[overlap] = IGNORE_INDEX

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_LINEAR)
        mask = cv2.resize(mask, (IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_NEAREST)
        image = (image.astype(np.float32) / 255.0 - MEAN) / STD
        image = np.transpose(image, (2, 0, 1)).copy()
        return (torch.from_numpy(image).float(),
                torch.from_numpy(mask.astype(np.int64)).long(),
                info["file_name"])


class DiceLoss(nn.Module):
    def forward(self, logits, targets):
        valid = targets != IGNORE_INDEX
        safe_targets = targets.masked_fill(~valid, 0)
        probabilities = torch.softmax(logits.float(), dim=1)
        one_hot = F.one_hot(safe_targets, NUM_CLASSES).permute(0, 3, 1, 2).float()
        valid = valid.unsqueeze(1).float()

        # Out-of-place operations are essential for SoftmaxBackward0.
        probabilities = probabilities * valid
        one_hot = one_hot * valid

        intersection = (probabilities * one_hot).sum(dim=(0, 2, 3))
        denominator = (probabilities + one_hot).sum(dim=(0, 2, 3))
        dice = (2 * intersection + 1.0) / (denominator + 1.0)
        return 1.0 - dice.mean()


class CombinedLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.ce = nn.CrossEntropyLoss(ignore_index=IGNORE_INDEX)
        self.dice = DiceLoss()

    def forward(self, logits, masks):
        return self.ce(logits.float(), masks) + self.dice(logits, masks)


def update_confusion(confusion, logits, labels):
    preds = logits.argmax(1)
    valid = (labels != IGNORE_INDEX) & (labels >= 0) & (labels < NUM_CLASSES)
    values = labels[valid] * NUM_CLASSES + preds[valid]
    counts = torch.bincount(values.reshape(-1), minlength=NUM_CLASSES ** 2)
    confusion += counts.cpu().numpy().reshape(NUM_CLASSES, NUM_CLASSES)


def get_metrics(confusion):
    matrix = confusion.astype(np.float64)
    tp = np.diag(matrix)
    real = matrix.sum(1)
    predicted = matrix.sum(0)
    union = real + predicted - tp
    iou = np.divide(tp, union, out=np.zeros_like(tp), where=union > 0)
    dice = np.divide(2 * tp, real + predicted, out=np.zeros_like(tp), where=(real + predicted) > 0)
    precision = np.divide(tp, predicted, out=np.zeros_like(tp), where=predicted > 0)
    recall = np.divide(tp, real, out=np.zeros_like(tp), where=real > 0)
    present = union > 0
    return {
        "pixel_accuracy": float(tp.sum() / matrix.sum()) if matrix.sum() else 0.0,
        "mean_iou": float(iou[present].mean()) if present.any() else 0.0,
        "mean_dice": float(dice[present].mean()) if present.any() else 0.0,
        "per_class": {
            CLASSES[k]: {
                "iou": float(iou[k]), "dice": float(dice[k]),
                "precision": float(precision[k]), "recall": float(recall[k]),
                "gt_pixels": int(real[k]),
            }
            for k in CLASSES
        },
    }


def run_epoch(model, loader, criterion, device, optimizer=None, scaler=None, desc="Evaluation"):
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    confusion = np.zeros((NUM_CLASSES, NUM_CLASSES), dtype=np.int64)

    for images, masks, _ in tqdm(loader, desc=desc, leave=False):
        images = images.to(device, non_blocking=True)
        masks = masks.to(device, non_blocking=True)

        if training:
            optimizer.zero_grad(set_to_none=True)

        with torch.set_grad_enabled(training):
            with torch.autocast(device_type=device.type, dtype=torch.float16,
                                enabled=(device.type == "cuda")):
                output = model(pixel_values=images)
                logits = F.interpolate(output.logits, size=masks.shape[-2:],
                                       mode="bilinear", align_corners=False)
                loss = criterion(logits, masks)

            if training:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()

        total_loss += float(loss.item()) * images.size(0)
        if not training:
            update_confusion(confusion, logits.detach(), masks)

    avg = total_loss / len(loader.dataset)
    return avg, (get_metrics(confusion) if not training else None), confusion


def write_history(rows, path):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_history(rows):
    epochs = [r["epoch"] for r in rows]
    for filename, title, fields in [
        ("loss_curve.png", "Training and validation loss", ["train_loss", "val_loss"]),
        ("validation_miou.png", "Validation mean IoU", ["val_miou"]),
    ]:
        plt.figure(figsize=(9, 5))
        for key in fields:
            plt.plot(epochs, [r[key] for r in rows], label=key)
        plt.title(title)
        plt.xlabel("Epoch")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / filename, dpi=160)
        plt.close()


@torch.no_grad()
def infer_test_images(model, device):
    output_dir = OUTPUT_DIR / "inference_only"
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(p for p in INFERENCE_DIR.iterdir()
                   if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    model.eval()
    for path in tqdm(paths, desc="Inference"):
        image = cv2.imread(str(path))
        if image is None:
            continue
        h, w = image.shape[:2]
        rgb = cv2.cvtColor(cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE)), cv2.COLOR_BGR2RGB)
        tensor = (rgb.astype(np.float32) / 255.0 - MEAN) / STD
        tensor = torch.from_numpy(tensor.transpose(2, 0, 1).copy()).unsqueeze(0).float().to(device)
        with torch.autocast(device_type=device.type, dtype=torch.float16,
                            enabled=(device.type == "cuda")):
            logits = model(pixel_values=tensor).logits
            logits = F.interpolate(logits, size=(h, w), mode="bilinear", align_corners=False)
        predicted = logits.argmax(1)[0].cpu().numpy()
        colored = np.zeros_like(image)
        for label, color in COLORS_BGR.items():
            colored[predicted == label] = color
        overlay = cv2.addWeighted(image, 0.60, colored, 0.40, 0)
        combined = np.hstack([image, overlay, colored])
        cv2.imwrite(str(output_dir / f"{path.stem}_prediction.jpg"), combined)
    print(f"Inference images saved: {output_dir}")


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    augmented = load_coco(AUG_JSON)
    train_images, val_images, manifest = split_augmented_images(augmented)
    final_test = load_coco(FINAL_TEST_DIR / "_annotations.coco.json")
    (OUTPUT_DIR / "split_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Source originals: {manifest['source_original_count']}")
    print(f"Training samples: {len(train_images)}")
    print(f"Validation: {len(val_images)} (original images only)")
    print(f"Final labelled test: {len(final_test['images'])} (old valid folder)")
    print("Old test folder: inference only")
    print("WARNING: Unannotated pixels are assigned to 'Existing plants' (class 0).")

    train_ds = CocoSegDataset(AUG_DIR, augmented, train_images)
    val_ds = CocoSegDataset(AUG_DIR, augmented, val_images)
    test_ds = CocoSegDataset(FINAL_TEST_DIR, final_test)
    def loader(dataset, shuffle):
        return DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=shuffle,
                          num_workers=WORKERS, pin_memory=(device.type == "cuda"),
                          persistent_workers=WORKERS > 0)
    train_loader = loader(train_ds, True)
    val_loader = loader(val_ds, False)
    test_loader = loader(test_ds, False)

    model = SegformerForSemanticSegmentation.from_pretrained(
        MODEL_NAME, num_labels=NUM_CLASSES,
        id2label=CLASSES, label2id={v: k for k, v in CLASSES.items()},
        ignore_mismatched_sizes=True).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE,
                                  weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=EPOCHS, eta_min=1e-7)
    scaler = torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))
    criterion = CombinedLoss()
    best_path = OUTPUT_DIR / "best_segformer_b0.pt"
    best_miou, stale, history = -1.0, 0, []
    start = time.time()

    for epoch in range(1, EPOCHS + 1):
        print(f"\n{'=' * 65}\nEPOCH {epoch}/{EPOCHS}\n{'=' * 65}")
        train_loss, _, _ = run_epoch(model, train_loader, criterion, device,
                                     optimizer, scaler, desc="Training")
        val_loss, metrics, _ = run_epoch(model, val_loader, criterion, device,
                                         desc="Validation")
        scheduler.step()
        miou = metrics["mean_iou"]
        history.append({
            "epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
            "val_miou": miou, "val_dice": metrics["mean_dice"],
            "val_pixel_accuracy": metrics["pixel_accuracy"],
        })
        write_history(history, OUTPUT_DIR / "training_history.csv")
        print(f"Train loss: {train_loss:.4f} | Val loss: {val_loss:.4f} | "
              f"Val mIoU: {miou:.4f} | Val Dice: {metrics['mean_dice']:.4f}")
        for name, scores in metrics["per_class"].items():
            print(f"{name:<18} IoU={scores['iou']:.4f} Dice={scores['dice']:.4f}")

        if miou > best_miou:
            best_miou, stale = miou, 0
            torch.save({
                "model_state_dict": model.state_dict(), "epoch": epoch,
                "best_val_miou": best_miou, "model_name": MODEL_NAME,
                "classes": CLASSES, "image_size": IMAGE_SIZE,
            }, best_path)
            print(f"BEST MODEL SAVED (mIoU={best_miou:.4f})")
        else:
            stale += 1
            print(f"No improvement: {stale}/{PATIENCE}")
            if stale >= PATIENCE:
                print("Early stopping triggered.")
                break

    plot_history(history)
    checkpoint = torch.load(best_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    print(f"\nBest epoch: {checkpoint['epoch']}; best validation mIoU: {best_miou:.4f}")
    test_loss, test_metrics, matrix = run_epoch(model, test_loader, criterion, device,
                                                 desc="Final labelled test")
    test_metrics["test_loss"] = test_loss
    (OUTPUT_DIR / "final_test_metrics.json").write_text(
        json.dumps(test_metrics, indent=2), encoding="utf-8")
    np.savetxt(OUTPUT_DIR / "final_test_confusion_matrix.csv", matrix,
               delimiter=",", fmt="%d")
    print(f"Final test: mIoU={test_metrics['mean_iou']:.4f} | "
          f"Dice={test_metrics['mean_dice']:.4f} | "
          f"Pixel accuracy={test_metrics['pixel_accuracy']:.4f}")
    for name, scores in test_metrics["per_class"].items():
        print(f"{name:<18} IoU={scores['iou']:.4f} Dice={scores['dice']:.4f}")
    infer_test_images(model, device)
    print(f"Training + evaluation time: {(time.time() - start) / 60:.1f} min")
    print(f"Best checkpoint: {best_path}")


if __name__ == "__main__":
    main()
