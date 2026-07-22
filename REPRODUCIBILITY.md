# Reproducibility status

## Public artifact

This repository currently provides:

- the fixed 3,630/840 split as relative manifests;
- YOLO-format object annotations for all 4,470 samples;
- one pixel mask for each of the 840 test samples;
- dataset counts, file-level checksums, and a leakage audit;
- the available detector training and validation code;
- configuration and logs from a 200-epoch detector retraining run.

## Model-scope boundary

The audited local checkpoint is a YOLOv9 `DualDDetect` model with 60,804,152
parameters. It is not the 4.23-million-parameter reconstruction-guided model
reported in the manuscript. The checkpoint therefore must not be used as
evidence for the manuscript's 79.6% mAP50 or 96.7% pixel AUROC.

The complete paper artifact still requires the exact shared-encoder
reconstruction branch, DCNv4 implementation, Efficient Multi-Scale Attention
module, inference-only aligned feature addition, pixel-AUROC evaluation script,
and the checkpoint that produced the reported headline results. These files
must be released before the repository can claim end-to-end reproduction of the
paper.

## Available detector run

The local detector run used Python 3.10, PyTorch 2.5.1 with CUDA 12.1, Adam,
200 epochs, a 640 x 640 input, batch size 4, four workers, and seed 0. Its exact
configuration and full metric history are under `artifacts/detector_retraining`.
Large checkpoints are excluded from Git history; their SHA-256 digests are
recorded in `run_summary.json` for later GitHub Release or Zenodo deposition.

## Required release gate

Before changing the manuscript statement to say that the paper is fully
reproducible from this repository, verify all of the following:

1. The released architecture has 4.23 million parameters and produces both
   object detections and a 640 x 640 continuous anomaly score.
2. The same checkpoint supports fusion-off and fusion-on inference.
3. The evaluation script reproduces the reported object metrics and 96.7%
   pixel AUROC on the fixed 840-image test split.
4. The release records package versions, the exact command line, model hash,
   split hash, and output metrics.
