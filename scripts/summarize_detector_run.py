#!/usr/bin/env python3
"""Summarize an existing detector training run without relabeling it as the paper model."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/detector_retraining"))
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for name in ("opt.yaml", "hyp.yaml", "results.csv", "results.png", "PR_curve.png"):
        source = run_dir / name
        if source.exists():
            shutil.copy2(source, output_dir / name)

    with (run_dir / "results.csv").open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = [
            {str(key).strip(): str(value).strip() for key, value in row.items()}
            for row in reader
        ]
    map_key = "metrics/mAP_0.5"
    precision_key = "metrics/precision"
    recall_key = "metrics/recall"
    best = max(rows, key=lambda row: float(row[map_key]))
    last = rows[-1]

    weights = {}
    for name in ("best.pt", "last.pt"):
        path = run_dir / "weights" / name
        if path.exists():
            weights[name] = {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "tracked_in_git": False,
            }

    summary = {
        "scope": "available YOLOv9 DualDDetect retraining run; not the manuscript's complete reconstruction-guided model",
        "epochs_recorded": len(rows),
        "best_map50_epoch": int(float(best["epoch"])),
        "best_map50_metrics": {
            "precision": float(best[precision_key]),
            "recall": float(best[recall_key]),
            "map50": float(best[map_key]),
            "map50_95": float(best["metrics/mAP_0.5:0.95"]),
        },
        "last_epoch_metrics": {
            "epoch": int(float(last["epoch"])),
            "precision": float(last[precision_key]),
            "recall": float(last[recall_key]),
            "map50": float(last[map_key]),
            "map50_95": float(last["metrics/mAP_0.5:0.95"]),
        },
        "weights": weights,
    }
    (output_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
