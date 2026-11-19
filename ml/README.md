# ML

One folder per incident type. Raw data lives in `../data/` (git-ignored); only manifests, code, configs and evaluation reports are committed.

| Folder | Task | Model | Dataset |
| --- | --- | --- | --- |
| `data/` | Split manifests, provenance, licence notes | — | all |
| `fight/` | Clip classification | VideoMAE Base fine-tune | RWF-2000 |
| `fire/` | Object detection | YOLO26n fine-tune | D-Fire |
| `fall/` | Pose sequence classification | MediaPipe Pose + small temporal model | UR Fall |

## Rules

1. **Provenance first.** Before downloading, add an entry to `data/manifests/<dataset>.yaml`: source URL, licence/terms, allowed uses, checksum.
2. **No leakage.** Split by source recording/participant, not by clip. Check near-duplicates across splits.
3. **Thresholds from validation, numbers from test.** Never tune on the held-out split.
4. **Report:** precision, recall, F1, false-positive rate (clips); false alerts per video-hour and timing error (long videos); per-class AP (fire).
5. **Version everything.** Every reported metric references a checkpoint hash and manifest hash.

## Fight model (milestone 2)

```bash
cd ml
uv sync
uv run python data/make_splits.py --dataset rwf2000 --root ../data/RWF-2000
uv run python fight/train.py --manifest data/manifests/rwf2000.splits.json
```

Training needs a CUDA GPU in practice (Colab/Lambda/RunPod/EC2 g5). Apple MPS works for smoke tests only.
