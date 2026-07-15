# Attribution and scope

This repository is derived from the open-source YOLOv9 implementation by
WongKinYiu and contributors:

- Upstream repository: https://github.com/WongKinYiu/yolov9
- Upstream paper: *YOLOv9: Learning What You Want to Learn Using Programmable
  Gradient Information*, arXiv:2402.13616
- License: GNU General Public License v3.0

The repository retains the upstream GPL-3.0 license. Modifications and dataset
configuration in this repository are distributed under the same license.

## Important scope note

The code currently published here implements a YOLOv9 dual-head object-detection
training pipeline for steel-surface defects. It does **not** yet implement the
complete Chapter 4 DBA architecture described in the associated thesis
(YOLOv8n + DCNv4 + EMA attention + autoencoder reconstruction branch). Please
do not describe the current release as an exact reproduction of that model.

