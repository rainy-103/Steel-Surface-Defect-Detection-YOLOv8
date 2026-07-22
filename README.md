# Reconstruction-guided dual-branch learning for steel surface defect detection and anomaly localization

This repository is the public artifact for the manuscript *Reconstruction-guided
dual-branch learning for steel surface defect detection and anomaly
localization*, submitted to the *Journal of Electronic Imaging*.

The paper studies one shared visual encoder with two task paths: a detector
returns class-specific boxes, while a reconstruction path returns a continuous
pixel-level anomaly score. The paper aligns 80 x 80 x 256 reconstruction and
detection features and adds them before the high-resolution detection head at
inference.

## Manuscript scope and reported results

The proposed method combines a YOLOv8-based object detector with a
normal-appearance reconstruction branch. DCNv4 operators improve geometric
adaptation, Efficient Multi-Scale Attention recalibrates the three detection
scales, and an aligned reconstruction feature is added to the high-resolution
detection feature during inference. The model therefore produces both
category-aware bounding boxes and a continuous pixel-level anomaly score.

The manuscript reports the following results on the fixed three-class split:

| Precision | Recall | mAP50 | Pixel AUROC | Parameters | GFLOPs |
|---:|---:|---:|---:|---:|---:|
| 82.3% | 71.1% | 79.6% | 96.7% | 4.23 M | 10.8 |

These values define the verification targets for the paper-specific model
release described in `REPRODUCIBILITY.md`; they are distinct from the reference
YOLOv9 detector run preserved in this repository.

## Artifact status

| Component | Public status | Location |
|---|---|---|
| Fixed 3,630/840 split | Available and verified | `artifacts/dataset/` |
| Object annotations | Available for all 4,470 samples | annotation ZIP |
| Test masks | Available for all 840 test samples | annotation ZIP |
| Dataset manifest and SHA-256 hashes | Available | `artifacts/dataset/manifest.csv` |
| Detector training code | Available | repository root, `models/`, and `utils/` |
| Audited 200-epoch detector run | Configuration and metrics available | `artifacts/detector_retraining/` |
| Paper-specific full model package | Release pending | see `REPRODUCIBILITY.md` |
| Large checkpoints | Hashes recorded; release asset pending | `run_summary.json` |

The current detector checkpoint is a 60.8-million-parameter YOLOv9
`DualDDetect` model. It is not the manuscript's reported 4.23-million-parameter
reconstruction-guided model. `REPRODUCIBILITY.md` defines the release gate that
must be satisfied before this repository can claim end-to-end reproduction of
the paper's 79.6% mAP50 and 96.7% pixel AUROC.

## Repository map

- `DATA_CARD.md`: dataset scope, counts, formats, provenance, and access limits.
- `REPRODUCIBILITY.md`: verified artifacts, model boundary, and release gate.
- `artifacts/dataset/`: annotation archive, manifest, summary, and checksum.
- `artifacts/detector_retraining/`: exact detector configuration and metric log.
- `scripts/prepare_dataset_artifact.py`: rebuilds and audits the data release.
- `scripts/summarize_detector_run.py`: summarizes a detector run and hashes its weights.
- `train_dual.py`, `val_dual.py`, and `detect_dual.py`: reference detector workflow.
- `models/` and `utils/`: model definitions, data loading, losses, and evaluation utilities.

## Dataset artifact

The released archive contains YOLO-format box annotations and pixel masks, but
not source images. Obtain the original NEU surface-defect images from the
[official dataset page](https://faculty.neu.edu.cn/songkc/en/zdylm/263265) and
follow the image-use conditions stated by the data provider. The extended image
provenance and redistribution rights require author confirmation before the
additional images can be deposited publicly.

Expected local layout:

```text
parent/
|-- Steel-Surface-Defect-Detection-YOLOv8/
`-- NEU_Seg-main/
    |-- images/
    |   |-- train/
    |   `-- test/
    |-- labels/
    |   |-- train/
    |   `-- test/
    `-- annotations/
        `-- test/
```

Rebuild and verify the released annotation package:

```bash
python scripts/prepare_dataset_artifact.py \
  --dataset-root ../NEU_Seg-main \
  --output-dir artifacts/dataset
```

The command fails if the split counts differ from Table 1, if a labeled image
or test mask is missing, if box coordinates fall outside `[0, 1]`, or if an
exact image duplicate crosses the train-test boundary.

## Reference detector environment

The audited detector run used Python 3.10, PyTorch 2.5.1 with CUDA 12.1, an
NVIDIA GPU, and the packages in `requirements.txt`.

```bash
pip install -r requirements.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

## Reference detector training

The available training log records Adam optimization for 200 epochs at
640 x 640 resolution, batch size 4, four workers, and seed 0:

```bash
python train_dual.py \
  --device 0 \
  --workers 4 \
  --batch-size 4 \
  --imgsz 640 \
  --epochs 200 \
  --optimizer Adam \
  --data data/neu_det.yaml \
  --cfg models/detect/yolov9.yaml \
  --hyp data/hyps/hyp.ch4.yaml \
  --project runs/train \
  --name detector_retraining \
  --save-period 10
```

Summarize the run and compute checkpoint hashes:

```bash
python scripts/summarize_detector_run.py \
  --run-dir runs/train/detector_retraining \
  --output-dir artifacts/detector_retraining
```

## Reference detector inference

```bash
python detect_dual.py \
  --weights runs/train/detector_retraining/weights/best.pt \
  --source ../NEU_Seg-main/images/test/000001.jpg \
  --imgsz 640 \
  --device 0
```

Large checkpoints remain outside Git history. Publish them as a versioned
GitHub Release or Zenodo record, then record the persistent URL and the existing
SHA-256 digest in `artifacts/detector_retraining/run_summary.json`.

## Citation

Citation metadata are provided in `CITATION.cff`. Until the manuscript receives
a DOI, cite the repository version and the original NEU-DET source:

> K. Song and Y. Yan, "A noise robust method based on completed local binary
> patterns for hot-rolled steel strip surface defects," *Applied Surface
> Science* 285, 858-864 (2013). https://doi.org/10.1016/j.apsusc.2013.09.002

## Licence and attribution

The detector code derives from
[WongKinYiu/yolov9](https://github.com/WongKinYiu/yolov9) and remains under the
GNU General Public License v3.0. See `LICENSE.md` and `NOTICE.md`. The code
licence does not transfer rights to third-party images.
