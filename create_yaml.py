from pathlib import Path

project_dir = Path(r"C:\Users\LENOVO\Downloads\Thevindu_AI_Part")
dataset_dir = project_dir / "archive"
yaml_path = project_dir / "thevindu_pest.yaml"

yaml_content = f"""path: {dataset_dir.as_posix()}

train: train/images
val: val/images
test: test/images

nc: 4

names:
  0: MP
  1: BT
  2: T
  3: C
"""

yaml_path.write_text(yaml_content, encoding="utf-8")

print("Dataset YAML created successfully.")
print(f"Saved to: {yaml_path}")