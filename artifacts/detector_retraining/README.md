# Available detector retraining run

This directory records an audited 200-epoch YOLOv9 `DualDDetect` run. It is
included as detector-development evidence and is not the complete
reconstruction-guided model described in the manuscript.

- `opt.yaml` and `hyp.yaml` record the exact run configuration.
- `results.csv` contains all 200 epochs.
- `results.png` and `PR_curve.png` visualize the training history and PR curve.
- `run_summary.json` identifies the peak-mAP50 epoch, the final epoch, and the
  SHA-256 hashes of the excluded checkpoints.

The checkpoint files exceed GitHub's normal file limit and must be deposited as
a GitHub Release or Zenodo asset. Their hashes allow the released files to be
matched to the audited local weights.
