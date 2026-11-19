"""Fine-tune VideoMAE Base on RWF-2000 (fight / nonfight).

Follows https://huggingface.co/docs/transformers/main/tasks/video_classification

TODO(milestone 2):
- Load splits manifest; build datasets that sample 16 frames per clip.
- Start from MCG-NJU/videomae-base-finetuned-kinetics with a 2-class head
  (label2id={"nonfight": 0, "fight": 1}; the worker reads label2id["fight"]).
- Train with Trainer; pick threshold on val by maximising F1 at a capped FPR.
- Evaluate once on test; write eval_report.json (precision, recall, F1, FPR, confusion, threshold,
  checkpoint sha, manifest sha).
- Save with save_pretrained() so the worker can load it via FIGHT_MODEL_PATH.
"""

BASE_CHECKPOINT = "MCG-NJU/videomae-base-finetuned-kinetics"
LABELS = {"nonfight": 0, "fight": 1}

if __name__ == "__main__":
    raise SystemExit("not implemented yet — see module docstring")
