"""Senanayake paddy field: DeepLabV3+ / EfficientNet-B4 semantic segmentation.

Training labels must be genuine COCO instance polygons/RLE for EXACTLY these
classes: Existing plants, Soil, Weeds. The network learns pixel masks directly;
no color thresholds, morphology, contour/area rules or inferred gap rules.

Splits:
  train/ -> train + validation (split original photos BEFORE augmentation)
  valid/ -> labelled FINAL TEST, never used for checkpoint selection
  test/  -> inference ONLY, no metrics or training use

Your 3000 offline augmented files are intentionally NOT used because augmentation
source mappings cannot be independently verified and would risk data leakage.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from pycocotools import mask as mask_utils
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

try:
    import albumentations as A
    import segmentation_models_pytorch as smp
except ImportError as exc:
    raise SystemExit(
        "Missing dependency. From activated torch_gpu environment, run:\n"
        "python -m pip install segmentation-models-pytorch==0.5.0 albumentations pycocotools tqdm matplotlib"
    ) from exc

# -----------------------------------------------------------------------------
# Environment and paths
# -----------------------------------------------------------------------------
PROJECT = Path(r"C:\Users\LENOVO\Downloads\yasiru_Ai_part")
DATA_ROOT = PROJECT / "paddy field.v1i.coco-segmentation"
TRAIN_DIR = DATA_ROOT / "train"
FINAL_TEST_DIR = DATA_ROOT / "valid"
INFER_DIR = DATA_ROOT / "test"
OUT_DIR = PROJECT / "DeepLabV3Plus_EfficientNetB4_results"
BEST_PATH = OUT_DIR / "best_deeplabv3plus_b4.pt"

LABELS = ("Existing plants", "Soil", "Weeds")
NUM_CLASSES = 3
IGNORE = 255
ENCODER = "efficientnet-b4"
INPUT_SIZE = 320  # 384 after confirming memory headroom; must be divisible by 32
BATCH_SIZE = 2   # >=2 for ASPP BatchNorm; drop_last=True in train loader
GRAD_ACCUMULATION = 2
EPOCHS = 80
PATIENCE = 12
VAL_RATIO = 0.20
LR = 1e-4
WEIGHT_DECAY = 1e-4
WORKERS = 0  # robust on Windows and simpler traceback
SEED = 42

COLORS_BGR = np.array([(0, 185, 0), (75, 155, 225), (180, 65, 185)], dtype=np.uint8)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_coco(folder: Path) -> dict:
    json_path = folder / "_annotations.coco.json"
    if not json_path.exists():
        raise FileNotFoundError(f"COCO annotations not found: {json_path}")
    with json_path.open(encoding="utf-8") as fh:
        coco = json.load(fh)

    # Map by CATEGORY NAME, not numeric ID, to handle differences across splits.
    category_map = {str(x["name"]).strip().lower(): int(x["id"])
                    for x in coco["categories"]}
    desired = {name.lower() for name in LABELS}
    if set(category_map) != desired:
        raise ValueError(
            f"Unexpected categories in {json_path}: {category_map}.\n"
            f"Expected exactly {list(LABELS)}. Clean and verify all splits first."
        )
    coco["_id_to_class"] = {category_map[name.lower()]: i for i, name in enumerate(LABELS)}
    return coco


def decode_segmentation(segmentation, h: int, w: int) -> np.ndarray:
    if isinstance(segmentation, list):
        # A COCO polygon list or a list of polygons for one instance.
        if not segmentation:
            return np.zeros((h, w), dtype=bool)
        rle = mask_utils.merge(mask_utils.frPyObjects(segmentation, h, w))
    elif isinstance(segmentation, dict):
        rle = dict(segmentation)
        if isinstance(rle.get("counts"), list):
            rle = mask_utils.frPyObjects(rle, h, w)
        elif isinstance(rle.get("counts"), str):
            rle["counts"] = rle["counts"].encode("ascii")
    else:
        raise ValueError(f"Unknown COCO segmentation type: {type(segmentation)}")
    mask = mask_utils.decode(rle)
    if mask.ndim == 3:
        mask = np.any(mask, axis=2)
    if mask.shape != (h, w):
        raise ValueError(f"COCO mask shape mismatch {mask.shape} vs {(h, w)}")
    return mask.astype(bool)


def make_augmentations(training: bool):
    if training:
        return A.Compose([
            A.Resize(INPUT_SIZE, INPUT_SIZE),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.RandomBrightnessContrast(brightness_limit=0.12, contrast_limit=0.12, p=0.4),
            A.HueSaturationValue(hue_shift_limit=7, sat_shift_limit=12, val_shift_limit=10, p=0.2),
        ])
    return A.Compose([A.Resize(INPUT_SIZE, INPUT_SIZE)])


class PaddyDataset(Dataset):
    def __init__(self, folder: Path, coco: dict, selected: list[dict],
                 training: bool, mean: np.ndarray, std: np.ndarray):
        self.folder = folder
        self.selected = selected
        self.training = training
        self.mean = mean
        self.std = std
        self.transforms = make_augmentations(training)
        self.id_to_class = coco["_id_to_class"]
        self.by_image = defaultdict(list)
        for ann in coco["annotations"]:
            self.by_image[int(ann["image_id"])].append(ann)
        if len(selected) == 0:
            raise ValueError(f"No images selected for {folder}")

    def __len__(self):
        return len(self.selected)

    def __getitem__(self, index: int):
        info = self.selected[index]
        file_path = self.folder / info["file_name"]
        bgr = cv2.imread(str(file_path), cv2.IMREAD_COLOR)
        if bgr is None:
            raise FileNotFoundError(f"Image unreadable: {file_path}")
        h, w = bgr.shape[:2]
        masks = np.zeros((NUM_CLASSES, h, w), dtype=bool)
        for ann in self.by_image.get(int(info["id"]), []):
            label = self.id_to_class.get(int(ann["category_id"]))
            if label is None:
                raise ValueError(f"Unmapped annotation category {ann['category_id']}")
            if "segmentation" not in ann:
                raise ValueError(f"Missing segmentation for image {info['file_name']}")
            masks[label] |= decode_segmentation(ann["segmentation"], h, w)

        # Explicit annotation ONLY. Unlabelled pixels are UNKNOWN, not plants.
        # This corrects the previous default-green mask problem.
        target = np.full((h, w), IGNORE, dtype=np.uint8)
        counts = np.sum(masks, axis=0)
        for label in range(NUM_CLASSES):
            target[(masks[label]) & (counts == 1)] = label
        # All overlaps and unannotated areas remain IGNORE.
        transformed = self.transforms(image=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), mask=target)
        rgb, target = transformed["image"], transformed["mask"]
        if not np.any(target != IGNORE):
            raise ValueError(
                f"No annotated pixels in {info['file_name']} after resize. "
                "Check the mask or remove this sample."
            )
        normalized = (rgb.astype(np.float32) / 255.0 - self.mean) / self.std
        tensor = torch.from_numpy(normalized.transpose(2, 0, 1).copy()).float()
        labels = torch.from_numpy(target.astype(np.int64)).long()
        return tensor, labels, info["file_name"]


def split_originals(coco: dict) -> tuple[list[dict], list[dict]]:
    # Note: nearby drone frames can still be visually correlated. For a true
    # out-of-scene evaluation, split by flight/location (requires metadata).
    all_images = [im for im in coco["images"] if
                  Path(im["file_name"]).suffix.lower() in (".jpg", ".jpeg", ".png")]
    rng = random.Random(SEED)
    rng.shuffle(all_images)
    val_count = max(1, min(len(all_images) - 2, round(len(all_images) * VAL_RATIO)))
    valid = all_images[:val_count]
    train = all_images[val_count:]
    return train, valid


class DiceLoss(nn.Module):
    def forward(self, logits: torch.Tensor, labels: torch.Tensor):
        valid = labels != IGNORE
        safe_labels = labels.masked_fill(~valid, 0)
        probs = torch.softmax(logits.float(), dim=1)
        valid4 = valid.unsqueeze(1).float()
        probs = probs * valid4  # NOT in place; prevents SoftmaxBackward0 errors
        onehot = F.one_hot(safe_labels, NUM_CLASSES).permute(0, 3, 1, 2).float()
        onehot = onehot * valid4
        intersection = (probs * onehot).sum((0, 2, 3))
        denominator = (probs + onehot).sum((0, 2, 3))
        # Classes absent in an individual batch are omitted from batch Dice.
        present = onehot.sum((0, 2, 3)) > 0
        scores = (2 * intersection + 1.0) / (denominator + 1.0)
        return 1.0 - scores[present].mean() if present.any() else logits.sum() * 0.0


class SegmentationLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.ce = nn.CrossEntropyLoss(ignore_index=IGNORE)
        self.dice = DiceLoss()

    def forward(self, logits: torch.Tensor, mask: torch.Tensor):
        return self.ce(logits.float(), mask) + self.dice(logits, mask)


def confusion_update(matrix: np.ndarray, logits: torch.Tensor, mask: torch.Tensor):
    pred = logits.argmax(dim=1)
    valid = mask != IGNORE
    ids = (mask[valid] * NUM_CLASSES + pred[valid]).reshape(-1)
    freq = torch.bincount(ids, minlength=NUM_CLASSES * NUM_CLASSES)
    matrix += freq.detach().cpu().numpy().reshape(NUM_CLASSES, NUM_CLASSES)


def metrics(matrix: np.ndarray) -> dict:
    tp = np.diag(matrix).astype(np.float64)
    row = matrix.sum(axis=1).astype(np.float64)
    col = matrix.sum(axis=0).astype(np.float64)
    union = row + col - tp
    iou = np.divide(tp, union, out=np.zeros_like(tp), where=union != 0)
    dice = np.divide(2 * tp, row + col, out=np.zeros_like(tp), where=(row + col) != 0)
    present = union > 0
    return {
        "pixel_accuracy": float(tp.sum() / matrix.sum()) if matrix.sum() else 0.,
        "mean_iou": float(iou[present].mean()) if np.any(present) else 0.,
        "mean_dice": float(dice[present].mean()) if np.any(present) else 0.,
        "per_class": {name: {"iou": float(iou[i]), "dice": float(dice[i]),
                             "ground_truth_pixels": int(row[i]), "prediction_pixels": int(col[i])}
                      for i, name in enumerate(LABELS)},
    }


def make_model(pretrained: bool):
    # The DeepLabV3+ segmentation head is newly learned from labelled pixels.
    return smp.DeepLabV3Plus(
        encoder_name=ENCODER,
        encoder_weights="imagenet" if pretrained else None,
        encoder_output_stride=16,
        in_channels=3,
        classes=NUM_CLASSES,
        activation=None,
    )


def run_epoch(model, loader, criterion, device, optimizer=None, scaler=None):
    training = optimizer is not None
    model.train(training)
    if training and len(loader) == 0:
        raise RuntimeError("No complete training batches; BATCH_SIZE must be <= train images")
    total_loss, n_samples = 0.0, 0
    cm = np.zeros((NUM_CLASSES, NUM_CLASSES), dtype=np.int64)
    if training:
        optimizer.zero_grad(set_to_none=True)
    for step, (images, labels, _names) in enumerate(
        tqdm(loader, desc="Train" if training else "Evaluate", leave=False), start=1
    ):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        with torch.set_grad_enabled(training):
            with torch.autocast(device_type="cuda", enabled=(device.type == "cuda")):
                logits = model(images)
                if logits.shape[-2:] != labels.shape[-2:]:
                    logits = F.interpolate(logits, size=labels.shape[-2:],
                                           mode="bilinear", align_corners=False)
                loss = criterion(logits, labels)
            if not torch.isfinite(loss):
                raise RuntimeError(f"Non-finite loss; inspect annotations in batch {step}")
            if training:
                # Divide by actual accumulated step count so last update is scaled.
                remaining = len(loader) - (step - 1)
                divisor = GRAD_ACCUMULATION if remaining >= GRAD_ACCUMULATION else (
                    (len(loader) - 1) % GRAD_ACCUMULATION + 1
                )
                scaler.scale(loss / divisor).backward()
                if step % GRAD_ACCUMULATION == 0 or step == len(loader):
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad(set_to_none=True)
        n_samples += images.shape[0]
        total_loss += float(loss.detach().item()) * images.shape[0]
        if not training:
            confusion_update(cm, logits.detach(), labels)
    return total_loss / n_samples, (None if training else metrics(cm)), cm


def save_history(history: list[dict]):
    with (OUT_DIR / "training_history.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(history[0]))
        w.writeheader()
        w.writerows(history)


def plot_history(history: list[dict]):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib absent: skipping plots")
        return
    for filename, columns in (("loss_curves.png", ("train_loss", "val_loss")),
                              ("validation_miou.png", ("val_miou",))):
        fig, ax = plt.subplots(figsize=(9, 4.5))
        for name in columns:
            ax.plot([item["epoch"] for item in history], [item[name] for item in history], label=name)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Value")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT_DIR / filename, dpi=150)
        plt.close(fig)


def print_metrics(split: str, results: dict):
    print(f"{split}: pixel Acc={results['pixel_accuracy']:.4f} "
          f"mIoU={results['mean_iou']:.4f} mDice={results['mean_dice']:.4f}")
    for name, values in results["per_class"].items():
        print(f"  {name:<18} IoU={values['iou']:.4f} Dice={values['dice']:.4f} "
              f"GT pixels={values['ground_truth_pixels']}")


@torch.no_grad()
def save_inference(model, device, mean, std):
    save_dir = OUT_DIR / "inference_only"
    save_dir.mkdir(exist_ok=True, parents=True)
    if not INFER_DIR.exists():
        print(f"Inference folder missing, skipped: {INFER_DIR}")
        return
    image_paths = sorted(p for p in INFER_DIR.iterdir() if p.is_file() and
                         p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    model.eval()
    for path in tqdm(image_paths, desc="Inference"):
        original = cv2.imread(str(path))
        if original is None:
            print(f"Skipping unreadable image: {path}")
            continue
        height, width = original.shape[:2]
        resized = cv2.resize(cv2.cvtColor(original, cv2.COLOR_BGR2RGB),
                             (INPUT_SIZE, INPUT_SIZE), interpolation=cv2.INTER_LINEAR)
        tensor = ((resized.astype(np.float32) / 255.0 - mean) / std).transpose(2, 0, 1)
        tensor = torch.from_numpy(tensor.copy()).float().unsqueeze(0).to(device)
        with torch.autocast(device_type="cuda", enabled=(device.type == "cuda")):
            scores = model(tensor)
        scores = F.interpolate(scores.float(), size=(height, width),
                               mode="bilinear", align_corners=False)
        predicted = scores.argmax(dim=1)[0].cpu().numpy()
        color_mask = COLORS_BGR[predicted]
        overlay = cv2.addWeighted(original, 0.60, color_mask, 0.40, 0)
        triptych = np.concatenate((original, overlay, color_mask), axis=1)
        cv2.imwrite(str(save_dir / f"{path.stem}_prediction.jpg"), triptych)
    print(f"Inference result images: {save_dir}")


def main(mode: str):
    set_seed(SEED)
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("\nSENANAYAKE | DEEPLABV3+ / EFFICIENTNET-B4")
    print(f"Device: {device} " + (torch.cuda.get_device_name(0) if device.type == "cuda" else ""))
    print(f"Image size={INPUT_SIZE}, batch={BATCH_SIZE}, epochs={EPOCHS}")
    print("NO heuristic segmentation or gap detection. Predictions are network outputs.")
    print("Unlabelled pixels and overlaps are IGNORE (255), NOT Existing plants.")
    prep = smp.encoders.get_preprocessing_params(ENCODER, pretrained="imagenet")
    mean = np.array(prep["mean"], dtype=np.float32)
    std = np.array(prep["std"], dtype=np.float32)

    if mode == "infer":
        if not BEST_PATH.exists():
            raise FileNotFoundError(f"Trained checkpoint not found: {BEST_PATH}")
        model = make_model(pretrained=False).to(device)
        ckpt = torch.load(BEST_PATH, map_location="cpu", weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"])
        save_inference(model, device, mean, std)
        return

    train_coco = load_coco(TRAIN_DIR)
    final_test_coco = load_coco(FINAL_TEST_DIR)
    train_items, val_items = split_originals(train_coco)
    test_items = final_test_coco["images"]
    # Don't train on the 3000 offline augmented images; on-the-fly augmentation
    # only affects the training set, NEVER the validation or final test set.
    manifest = {
        "train_original_count": len(train_items),
        "validation_original_count": len(val_items),
        "final_test_count": len(test_items),
        "train_originals": [x["file_name"] for x in train_items],
        "validation_originals": [x["file_name"] for x in val_items],
        "final_test_source": str(FINAL_TEST_DIR),
        "inference_only_source": str(INFER_DIR),
        "unlabelled_policy": "ignore_index_255",
        "warning": "For truly independent validation, group frames by flight/field/session; filenames alone cannot establish independence."
    }
    (OUT_DIR / "split_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Train originals: {len(train_items)} | Internal validation: {len(val_items)} "
          f"| Final labelled test: {len(test_items)}")
    print(f"Old test folder reserved strictly for inference: {INFER_DIR}")
    print("NOTE: Drone frames from one capture session may still be correlated across splits.")

    train_ds = PaddyDataset(TRAIN_DIR, train_coco, train_items, True, mean, std)
    val_ds = PaddyDataset(TRAIN_DIR, train_coco, val_items, False, mean, std)
    test_ds = PaddyDataset(FINAL_TEST_DIR, final_test_coco, test_items, False, mean, std)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              drop_last=True, num_workers=WORKERS,
                              pin_memory=device.type == "cuda")
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False,
                            num_workers=WORKERS, pin_memory=device.type == "cuda")
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False,
                             num_workers=WORKERS, pin_memory=device.type == "cuda")

    print("Loading ImageNet-pretrained EfficientNet-B4 encoder (first run downloads weights)...")
    model = make_model(pretrained=True).to(device)
    criterion = SegmentationLoss().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)
    scaler = torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))
    best_miou = -1.0
    patience_left = PATIENCE
    history = []
    start = time.time()
    for epoch in range(1, EPOCHS + 1):
        print(f"\n{'=' * 60}\nEPOCH {epoch}/{EPOCHS}\n{'=' * 60}")
        train_loss, _, _ = run_epoch(model, train_loader, criterion, device,
                                     optimizer=optimizer, scaler=scaler)
        val_loss, val_metrics, _ = run_epoch(model, val_loader, criterion, device)
        scheduler.step()
        print(f"Training loss={train_loss:.4f} | Validation loss={val_loss:.4f}")
        print_metrics("VAL", val_metrics)
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
                        "val_miou": val_metrics["mean_iou"],
                        "val_dice": val_metrics["mean_dice"],
                        "val_acc": val_metrics["pixel_accuracy"]})
        save_history(history)
        if val_metrics["mean_iou"] > best_miou:
            best_miou = val_metrics["mean_iou"]
            patience_left = PATIENCE
            torch.save({"epoch": epoch, "model_state_dict": model.state_dict(),
                        "best_val_miou": best_miou, "encoder": ENCODER,
                        "input_size": INPUT_SIZE, "labels": LABELS,
                        "unlabelled_policy": "ignore_index_255"}, BEST_PATH)
            print(f"BEST CHECKPOINT saved (validation mIoU={best_miou:.4f})")
        else:
            patience_left -= 1
            print(f"No new best; early stopping remaining={patience_left}")
            if patience_left <= 0:
                break

    plot_history(history)
    ckpt = torch.load(BEST_PATH, map_location="cpu", weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    print(f"\nBEST epoch={ckpt['epoch']}, validation mIoU={ckpt['best_val_miou']:.4f}")
    test_loss, test_metrics, matrix = run_epoch(model, test_loader, criterion, device)
    test_metrics["loss"] = test_loss
    (OUT_DIR / "final_test_metrics.json").write_text(json.dumps(test_metrics, indent=2), encoding="utf-8")
    with (OUT_DIR / "final_test_confusion_matrix.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Ground truth / Predicted"] + list(LABELS))
        for idx, row in enumerate(matrix):
            writer.writerow([LABELS[idx]] + row.tolist())
    print_metrics("FINAL LABELLED TEST", test_metrics)
    save_inference(model, device, mean, std)
    print(f"Elapsed={(time.time()-start)/60:.1f} min | best checkpoint: {BEST_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("train", "infer"), default="train")
    args = parser.parse_args()
    main(args.mode)
