"""Standalone testing and inference for the saved Senanayake DeepLabV3+ EfficientNet-B4 checkpoint.

Place NEXT TO train_deeplabv3plus_efficientnetb4.py (the original trainer).
No model training occurs here. No postprocessing heuristics, color rules, or
manual thresholds are applied to model outputs.

Modes:
  python test_infer_deeplabv3plus_b4.py --mode both
  python test_infer_deeplabv3plus_b4.py --mode test
  python test_infer_deeplabv3plus_b4.py --mode infer
  python test_infer_deeplabv3plus_b4.py --mode image --image "C:\\path\\photo.jpg"

Original dataset split preserved:
  valid/ = labelled FINAL TEST (quantitative metrics + previews)
  test/  = INFERENCE ONLY (predictions only, no ground-truth metrics)
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

import train_deeplabv3plus_efficientnetb4 as trainer

OUTPUT = trainer.OUT_DIR / "checkpoint_evaluation"
COLOR = trainer.COLORS_BGR
UNKNOWN_BGR = (100, 100, 100)  # Preview ONLY for pixels without labels


def load_checkpoint():
    path = trainer.BEST_PATH
    if not path.is_file():
        raise FileNotFoundError(
            f"Best model checkpoint not found:\n  {path}\n"
            "First finish training the DeepLabV3+ EfficientNet-B4 model. "
            "The checkpoint must be saved as best_deeplabv3plus_b4.pt."
        )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    if checkpoint.get("encoder", trainer.ENCODER) != trainer.ENCODER:
        raise ValueError(f"Encoder mismatch in checkpoint: {checkpoint.get('encoder')}")
    if "labels" in checkpoint and tuple(checkpoint["labels"]) != tuple(trainer.LABELS):
        raise ValueError(f"Unexpected checkpoint label order: {checkpoint['labels']}")
    trainer.INPUT_SIZE = int(checkpoint.get("input_size", trainer.INPUT_SIZE))
    model = trainer.make_model(pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model = model.to(device).eval()
    prep = trainer.smp.encoders.get_preprocessing_params(trainer.ENCODER, pretrained="imagenet")
    mean, std = [np.asarray(prep[key], dtype=np.float32) for key in ("mean", "std")]
    print("\nDEEP LAB V3+ / EFFICIENTNET-B4 | SAVED CHECKPOINT EVALUATION")
    print(f"Checkpoint: {path}")
    print(f"Device: {device}")
    print(f"Input size: {trainer.INPUT_SIZE} x {trainer.INPUT_SIZE}")
    if "epoch" in checkpoint:
        print(f"Loaded best epoch: {checkpoint['epoch']}")
    if "best_val_miou" in checkpoint:
        print(f"Training-validation mIoU: {checkpoint['best_val_miou']:.4f}")
    print("Class order: " + " | ".join(trainer.LABELS))
    return model, device, mean, std


@torch.inference_mode()
def predict_original(image_bgr, model, device, mean, std):
    height, width = image_bgr.shape[:2]
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (trainer.INPUT_SIZE, trainer.INPUT_SIZE),
                         interpolation=cv2.INTER_LINEAR)
    normalized = (resized.astype(np.float32) / 255.0 - mean) / std
    tensor = torch.from_numpy(normalized.transpose(2, 0, 1).copy()).unsqueeze(0).to(device)
    with torch.autocast(device_type="cuda", enabled=(device.type == "cuda")):
        logits = model(tensor)
    logits = F.interpolate(logits.float(), size=(height, width),
                           mode="bilinear", align_corners=False)
    probs = torch.softmax(logits, dim=1)
    prediction = probs.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)
    confidence = probs.max(dim=1).values[0].cpu().numpy()
    return prediction, confidence


def colorize_prediction(pred):
    return COLOR[pred]


def annotate_header(image, heading):
    strip = np.zeros((42, image.shape[1], 3), dtype=np.uint8)
    cv2.putText(strip, heading, (12, 28), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (245, 245, 245), 2, cv2.LINE_AA)
    return np.concatenate((strip, image), axis=0)


def write_prediction(image_path, save_dir, model, device, mean, std, gt=None):
    original = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if original is None:
        raise ValueError(f"Cannot read image: {image_path}")
    prediction, confidence = predict_original(original, model, device, mean, std)
    colored = colorize_prediction(prediction)
    overlay = cv2.addWeighted(original, 0.60, colored, 0.40, 0)
    panels = [annotate_header(original, "ORIGINAL")]
    if gt is not None:
        gt_color = np.full(original.shape, UNKNOWN_BGR, dtype=np.uint8)
        for class_id in range(trainer.NUM_CLASSES):
            gt_color[gt == class_id] = COLOR[class_id]
        panels.append(annotate_header(gt_color, "GROUND TRUTH (GREY = UNLABELLED)"))
    panels += [annotate_header(overlay, "MODEL OVERLAY"),
               annotate_header(colored, "MODEL PREDICTION")]
    triptych = np.concatenate(panels, axis=1)
    save_dir.mkdir(exist_ok=True, parents=True)
    cv2.imwrite(str(save_dir / (image_path.stem + "_prediction.jpg")),
                triptych, [cv2.IMWRITE_JPEG_QUALITY, 92])
    portion = {name: round(float(np.mean(prediction == idx) * 100), 2)
               for idx, name in enumerate(trainer.LABELS)}
    return {
        "image": image_path.name,
        "prediction_percent": portion,
        "mean_prediction_confidence": round(float(confidence.mean()), 4),
    }


def original_gt_by_image(coco):
    by_image = defaultdict(list)
    for annotation in coco["annotations"]:
        by_image[int(annotation["image_id"])].append(annotation)
    return by_image


def build_ground_truth(info, anns, category_lookup, shape):
    height, width = shape
    classes = np.zeros((trainer.NUM_CLASSES, height, width), dtype=bool)
    for ann in anns:
        class_id = category_lookup.get(int(ann["category_id"]))
        if class_id is None:
            raise ValueError(f"Unknown class ID {ann['category_id']}")
        classes[class_id] |= trainer.decode_segmentation(ann["segmentation"], height, width)
    count = classes.sum(axis=0)
    gt = np.full((height, width), trainer.IGNORE, dtype=np.uint8)
    for idx in range(trainer.NUM_CLASSES):
        gt[classes[idx] & (count == 1)] = idx
    return gt


def labeled_test(model, device, mean, std):
    print("\n[FINAL LABELLED TEST] 'valid' folder; this is NOT the model-selection set")
    coco = trainer.load_coco(trainer.FINAL_TEST_DIR)
    by_image = original_gt_by_image(coco)
    # Images with zero annotations cannot contribute to a labelled-pixel metric.
    items = [info for info in coco["images"] if by_image.get(int(info["id"]))]
    excluded = len(coco["images"]) - len(items)
    if not items:
        raise ValueError("No annotated test images found in old 'valid' folder")
    if excluded:
        print(f"Excluded {excluded} images with zero annotations from labelled test metrics.")
    ds = trainer.PaddyDataset(trainer.FINAL_TEST_DIR, coco, items, False, mean, std)
    loader = DataLoader(ds, batch_size=trainer.BATCH_SIZE,
                        shuffle=False, num_workers=0,
                        pin_memory=(device.type == "cuda"))
    loss_fn = trainer.SegmentationLoss().to(device)
    loss, values, matrix = trainer.run_epoch(model, loader, loss_fn, device)
    values["loss"] = float(loss)
    values["evaluated_test_images"] = len(items)
    values["unlabelled_policy"] = "ignored, not reclassified as plants"
    values["note"] = "Pixel metrics evaluated ONLY on explicitly labelled nonoverlapping pixels."
    OUTPUT.mkdir(exist_ok=True, parents=True)
    (OUTPUT / "final_test_metrics.json").write_text(
        json.dumps(values, indent=2), encoding="utf-8")
    with (OUTPUT / "final_test_confusion_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["GT / Predicted"] + list(trainer.LABELS))
        for idx, line in enumerate(matrix):
            w.writerow([trainer.LABELS[idx]] + [int(x) for x in line])
    trainer.print_metrics("FINAL TEST", values)
    print(f"Full metrics: {OUTPUT / 'final_test_metrics.json'}")
    preview_dir = OUTPUT / "labelled_test_previews"
    for info in tqdm(items, desc="Labelled-test previews"):
        p = trainer.FINAL_TEST_DIR / info["file_name"]
        image = cv2.imread(str(p))
        if image is None:
            raise FileNotFoundError(str(p))
        gt = build_ground_truth(info, by_image[int(info["id"])],
                                coco["_id_to_class"], image.shape[:2])
        write_prediction(p, preview_dir, model, device, mean, std, gt)
    print(f"Ground-truth comparison images: {preview_dir}")


def inference_folder(model, device, mean, std):
    print("\n[INFERENCE ONLY] old 'test' folder; no metric claims")
    folder = trainer.INFER_DIR
    if not folder.exists():
        raise FileNotFoundError(str(folder))
    images = sorted(p for p in folder.iterdir() if p.is_file()
                    and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    if not images:
        print(f"No images found: {folder}")
        return
    result_dir = OUTPUT / "unlabelled_inference"
    records = []
    for path in tqdm(images, desc="Inference"):
        records.append(write_prediction(path, result_dir, model, device, mean, std))
    (OUTPUT / "inference_summary.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8")
    print(f"Predictions: {result_dir}")
    print(f"Class proportions (NOT accuracy): {OUTPUT / 'inference_summary.json'}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("both", "test", "infer", "image"), default="both")
    parser.add_argument("--image", type=Path, default=None,
                        help="Path to a single image (used when --mode image)")
    args = parser.parse_args()
    if args.mode == "image" and args.image is None:
        parser.error("--mode image requires --image PATH")
    model, device, mean, std = load_checkpoint()
    if args.mode in ("test", "both"):
        labeled_test(model, device, mean, std)
    if args.mode in ("infer", "both"):
        inference_folder(model, device, mean, std)
    if args.mode == "image":
        if not args.image.is_file():
            raise FileNotFoundError(str(args.image))
        result_dir = OUTPUT / "single_image_predictions"
        result = write_prediction(args.image, result_dir, model, device, mean, std)
        print(f"Single-image prediction: {result_dir}")
        print(json.dumps(result, indent=2))
    print("\nFinished without retraining.")


if __name__ == "__main__":
    main()
