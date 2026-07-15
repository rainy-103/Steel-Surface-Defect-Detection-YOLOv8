# Steel Surface Defect Detection with YOLOv9

An open-source training and inference pipeline for steel-surface defect
detection using a dual-head YOLOv9 model. The current dataset configuration
recognizes three defect categories: Inclusion, Patches and Scratches.

> **Scope:** this release reflects the code that is currently runnable in the
> project folder. It is a YOLOv9 dual-head detector, not a complete reproduction
> of the thesis Chapter 4 DBA network (YOLOv8n + DCNv4 + EMA + autoencoder).

## Repository contents

- `train_dual.py`: dual-head detector training
- `detect_dual.py`: inference and optional feature visualization
- `val_dual.py`: validation
- `models/`: YOLOv9 model definitions
- `utils/`: data loading, loss functions and utilities
- `data/neu_det.yaml`: local NEU dataset configuration
- `data/hyps/hyp.ch4.yaml`: Chapter 4-style training hyperparameters

Datasets, training runs and model weights are intentionally excluded from Git
history. Large checkpoints should be distributed through a GitHub Release.

## Environment

The experiments were run with Python 3.10, PyTorch 2.5.1 + CUDA 12.1 and an
NVIDIA GPU. Create an environment with a CUDA-enabled PyTorch build, then run:

```bash
pip install -r requirements.txt
```

Verify GPU availability:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## Dataset layout

Download or prepare the NEU steel-surface defect dataset outside this
repository. The default layout is:

```text
parent/
├── Steel-Surface-Defect-Detection-YOLOv9/
└── NEU_Seg-main/
    ├── images/
    │   ├── train/
    │   └── test/
    └── labels/
        ├── train/
        └── test/
```

The labels used by this project are YOLO bounding boxes. Their class IDs are
`1`, `2` and `3`, so `data/neu_det.yaml` retains an unused class `0` for
compatibility. For a new dataset, remap the labels to zero-based IDs and update
the YAML file.

## Training

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
  --name ch4_retrain \
  --save-period 10
```

The principal checkpoints are written to:

```text
runs/train/ch4_retrain/weights/best.pt
runs/train/ch4_retrain/weights/last.pt
```

Resume an interrupted run with:

```bash
python train_dual.py --resume runs/train/ch4_retrain/weights/last.pt
```

## Inference and feature visualization

```bash
python detect_dual.py \
  --weights runs/train/ch4_retrain/weights/best.pt \
  --source ../NEU_Seg-main/images/test/000001.jpg \
  --imgsz 640 \
  --device 0 \
  --visualize
```

The `--visualize` option exports intermediate YOLO layer features. It does not
produce a reconstruction-branch activation map because the reconstruction
branch is not part of the current implementation.

## Pretrained weights

Model checkpoints are larger than GitHub's normal per-file limit and are not
committed to this repository. Publish `best.pt` as a GitHub Release asset and
add its download URL and SHA-256 checksum here.

## License and attribution

This project is based on [WongKinYiu/yolov9](https://github.com/WongKinYiu/yolov9)
and is distributed under the GNU General Public License v3.0. See
`LICENSE.md` and `NOTICE.md`.

## Citation

If this repository supports a publication, add the final paper title, authors,
DOI and BibTeX entry here. Please also cite the upstream YOLOv9 paper and the
dataset source used in your experiments.

