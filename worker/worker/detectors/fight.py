"""VideoMAE fight classifier. Requires `uv sync --extra models` and a fine-tuned checkpoint."""

import numpy as np

from worker.video import Clip


class VideoMAEFightDetector:
    category = "possible_fight"

    def __init__(self, checkpoint: str, threshold: float, device: str = "cpu"):
        import torch
        from transformers import AutoModelForVideoClassification, VideoMAEImageProcessor

        self._torch = torch
        self.processor = VideoMAEImageProcessor.from_pretrained(checkpoint)
        self.model = AutoModelForVideoClassification.from_pretrained(checkpoint).to(device).eval()
        self.device = device
        self.threshold = threshold
        self.model_version = f"videomae:{checkpoint}"
        self.fight_idx = self.model.config.label2id.get("fight", 1)

    def score(self, clips: list[Clip]) -> list[float]:
        if not clips:
            return []
        batch = self.processor([c.frames for c in clips], return_tensors="pt").to(self.device)
        with self._torch.no_grad():
            logits = self.model(**batch).logits
        probs = logits.softmax(-1)[:, self.fight_idx].cpu().numpy()
        return np.asarray(probs, dtype=float).tolist()
