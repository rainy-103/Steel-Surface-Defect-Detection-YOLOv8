#!/usr/bin/env python3
"""Build and verify the annotation artifact used by the JEI manuscript.

The archive intentionally excludes source images. It contains the fixed split,
YOLO-format object annotations, test masks, a file manifest, and checksums.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import Counter
from pathlib import Path


EXPECTED = {
    "train_images": 3630,
    "test_images": 840,
    "train_instances": 10529,
    "test_instances": 2791,
    "train_classes": {1: 4050, 2: 3054, 3: 3425},
    "test_classes": {1: 1134, 2: 727, 3: 930},
}
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
FIXED_ZIP_TIME = (2026, 7, 22, 0, 0, 0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_for_stem(directory: Path, stem: str) -> Path:
    matches = [directory / f"{stem}{suffix}" for suffix in IMAGE_SUFFIXES]
    existing = [path for path in matches if path.exists()]
    if len(existing) != 1:
        raise RuntimeError(
            f"Expected exactly one image for {stem!r} in {directory}, found {existing}"
        )
    return existing[0]


def label_inventory(directory: Path) -> tuple[list[Path], Counter[int], int]:
    labels = sorted(directory.glob("*.txt"))
    classes: Counter[int] = Counter()
    instances = 0
    for path in labels:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            fields = line.split()
            if not fields:
                continue
            if len(fields) != 5:
                raise RuntimeError(f"{path}:{line_number} has {len(fields)} fields, expected 5")
            class_id = int(fields[0])
            coordinates = [float(value) for value in fields[1:]]
            if class_id not in (1, 2, 3):
                raise RuntimeError(f"{path}:{line_number} uses unsupported class {class_id}")
            if any(value < 0.0 or value > 1.0 for value in coordinates):
                raise RuntimeError(f"{path}:{line_number} has coordinates outside [0, 1]")
            classes[class_id] += 1
            instances += 1
    return labels, classes, instances


def add_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("artifacts/dataset"), help="Artifact directory"
    )
    args = parser.parse_args()

    root = args.dataset_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    inventories = {}
    image_hashes: dict[str, list[tuple[str, str]]] = {}
    manifest_rows: list[dict[str, object]] = []
    archive_members: list[tuple[str, bytes]] = []

    for split in ("train", "test"):
        label_dir = root / "labels" / split
        image_dir = root / "images" / split
        labels, classes, instances = label_inventory(label_dir)
        image_paths = [image_for_stem(image_dir, path.stem) for path in labels]

        for image_path in image_paths:
            digest = sha256_file(image_path)
            image_hashes.setdefault(digest, []).append((split, image_path.stem))

        inventories[split] = {
            "images": len(image_paths),
            "instances": instances,
            "class_instances": dict(sorted(classes.items())),
        }

        split_text = "".join(f"images/{split}/{path.name}\n" for path in image_paths).encode()
        archive_members.append((f"splits/{split}.txt", split_text))

        for label_path in labels:
            data = label_path.read_bytes()
            archive_name = f"labels/{split}/{label_path.name}"
            archive_members.append((archive_name, data))
            manifest_rows.append(
                {
                    "path": archive_name,
                    "kind": "object_label",
                    "split": split,
                    "sample_id": label_path.stem,
                    "bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )

    mask_dir = root / "annotations" / "test"
    test_stems = {path.stem for path in (root / "labels" / "test").glob("*.txt")}
    masks = sorted(path for path in mask_dir.glob("*.png") if path.stem in test_stems)
    missing_masks = sorted(test_stems - {path.stem for path in masks})
    if missing_masks:
        raise RuntimeError(f"Missing test masks: {missing_masks[:10]}")
    for mask_path in masks:
        data = mask_path.read_bytes()
        archive_name = f"masks/test/{mask_path.name}"
        archive_members.append((archive_name, data))
        manifest_rows.append(
            {
                "path": archive_name,
                "kind": "pixel_mask",
                "split": "test",
                "sample_id": mask_path.stem,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )

    duplicates = [
        occurrences
        for occurrences in image_hashes.values()
        if {split for split, _ in occurrences} == {"train", "test"}
    ]

    observed = {
        "train_images": inventories["train"]["images"],
        "test_images": inventories["test"]["images"],
        "train_instances": inventories["train"]["instances"],
        "test_instances": inventories["test"]["instances"],
        "train_classes": inventories["train"]["class_instances"],
        "test_classes": inventories["test"]["class_instances"],
    }
    normalized_expected = {
        key: ({str(k): v for k, v in value.items()} if isinstance(value, dict) else value)
        for key, value in EXPECTED.items()
    }
    normalized_observed = {
        key: ({str(k): v for k, v in value.items()} if isinstance(value, dict) else value)
        for key, value in observed.items()
    }
    if normalized_observed != normalized_expected:
        raise RuntimeError(
            "Dataset counts differ from the manuscript:\n"
            + json.dumps({"expected": normalized_expected, "observed": normalized_observed}, indent=2)
        )
    if duplicates:
        raise RuntimeError(f"Found exact train/test duplicate images: {duplicates[:10]}")

    summary = {
        "artifact_version": "1.0.0",
        "classes": {"1": "Inclusions", "2": "Patches", "3": "Scratches"},
        "train": inventories["train"],
        "test": {**inventories["test"], "pixel_masks": len(masks)},
        "all": {
            "images": inventories["train"]["images"] + inventories["test"]["images"],
            "instances": inventories["train"]["instances"] + inventories["test"]["instances"],
        },
        "exact_train_test_image_duplicates": 0,
        "source_images_included": False,
    }
    summary_bytes = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()

    manifest_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        manifest_buffer, fieldnames=("path", "kind", "split", "sample_id", "bytes", "sha256")
    )
    writer.writeheader()
    writer.writerows(sorted(manifest_rows, key=lambda row: str(row["path"])))
    manifest_bytes = manifest_buffer.getvalue().encode()

    readme = "# Extended NEU-DET annotation artifact\n\n"
    readme += "This archive supports the fixed three-class split used in the manuscript.\n"
    readme += "It contains YOLO-format object labels for 3,630 training and 840 test images, "
    readme += "plus one pixel mask for each test image. Source images are not redistributed.\n\n"
    readme += "Class IDs: 1 = inclusions, 2 = patches, 3 = scratches.\n\n"
    readme += "Use `manifest.csv` and `dataset_summary.json` to verify file integrity and counts.\n"
    readme_bytes = readme.encode()

    archive_path = output_dir / "extended_neu_det_annotations_v1.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        add_bytes(archive, "README.md", readme_bytes)
        add_bytes(archive, "dataset_summary.json", summary_bytes)
        add_bytes(archive, "manifest.csv", manifest_bytes)
        for name, data in sorted(archive_members):
            add_bytes(archive, name, data)

    (output_dir / "dataset_summary.json").write_bytes(summary_bytes)
    (output_dir / "manifest.csv").write_bytes(manifest_bytes)
    archive_hash = sha256_file(archive_path)
    (output_dir / "SHA256SUMS").write_text(
        f"{archive_hash}  {archive_path.name}\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(summary, indent=2))
    print(f"Archive: {archive_path}")
    print(f"SHA-256: {archive_hash}")


if __name__ == "__main__":
    main()
