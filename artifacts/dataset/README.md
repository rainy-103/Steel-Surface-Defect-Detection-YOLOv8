# Dataset release files

- `extended_neu_det_annotations_v1.zip`: fixed split, object annotations, and
  840 test masks.
- `dataset_summary.json`: verified counts and class distribution.
- `manifest.csv`: file-level metadata and SHA-256 hashes for labels and masks.
- `SHA256SUMS`: checksum for the release ZIP.

Source images are excluded. See `../../DATA_CARD.md` for provenance and licence
constraints and run `../../scripts/prepare_dataset_artifact.py` to rebuild the
archive.
