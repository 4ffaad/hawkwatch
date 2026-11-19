"""Create leakage-free train/val/test splits and write a manifest.

TODO(milestone 2):
- Walk the dataset root, list clips with labels.
- Derive a group id per clip (source recording) — RWF-2000 has none, so cluster by
  perceptual hash of the first frame + filename prefix and record the method.
- GroupShuffleSplit 70/15/15 with a fixed seed; assert no group crosses splits.
- Write {seed, method, splits: {train: [...], val: [...], test: [...]}, sha256} JSON.
"""

import argparse

p = argparse.ArgumentParser()
p.add_argument("--dataset", required=True)
p.add_argument("--root", required=True)
p.add_argument("--seed", type=int, default=13)
args = p.parse_args()
raise SystemExit("not implemented yet — see module docstring")
