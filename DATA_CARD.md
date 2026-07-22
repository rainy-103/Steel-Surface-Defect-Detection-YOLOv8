# Data card: extended three-class NEU-DET split

## Scope

The manuscript evaluates inclusions, patches, and scratches on a fixed split of
an extended steel-surface collection. The repository distributes annotations,
test masks, and split manifests. It does not redistribute source images.

## Verified inventory

| Split | Images | Inclusions | Patches | Scratches | All instances | Pixel masks |
|---|---:|---:|---:|---:|---:|---:|
| Training | 3,630 | 4,050 | 3,054 | 3,425 | 10,529 | — |
| Test | 840 | 1,134 | 727 | 930 | 2,791 | 840 |
| Total | 4,470 | 5,184 | 3,781 | 4,355 | 13,320 | 840 |

The artifact builder verifies that every labeled sample has one image, every
test sample has one pixel mask, all normalized box coordinates lie in `[0, 1]`,
and no byte-identical image occurs in both splits.

## Files and formats

- Object annotations use YOLO text format: `class_id x_center y_center width height`.
- Class IDs are `1` for inclusions, `2` for patches, and `3` for scratches.
- Test masks are single-channel PNG files aligned by sample ID.
- `artifacts/dataset/manifest.csv` records the SHA-256 digest of every released
  label and mask.
- `artifacts/dataset/extended_neu_det_annotations_v1.zip` contains the complete
  annotation artifact.

## Source images and licence

The source images are not included in this repository. Users must obtain the
original NEU surface-defect data from its official source and place compatible
images under `images/train` and `images/test`. Additional image provenance and
redistribution permission must be confirmed by the authors before any extended
image collection is deposited publicly. The annotation archive does not grant
rights to third-party source images.

## Rebuilding the artifact

```bash
python scripts/prepare_dataset_artifact.py \
  --dataset-root /path/to/NEU_Seg-main \
  --output-dir artifacts/dataset
```
