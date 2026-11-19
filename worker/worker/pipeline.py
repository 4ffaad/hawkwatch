import os
import tempfile

from worker.config import settings
from worker.detectors import ClipDetector
from worker.intervals import WindowScore, merge_positive_windows
from worker.storage import download
from worker.video import iter_clips


def load_detectors() -> list[ClipDetector]:
    detectors: list[ClipDetector] = []
    if ckpt := os.getenv("FIGHT_MODEL_PATH"):
        from worker.detectors.fight import VideoMAEFightDetector

        detectors.append(
            VideoMAEFightDetector(
                ckpt, float(os.getenv("FIGHT_THRESHOLD", "0.5")), settings.worker_device
            )
        )
    # TODO: fire/smoke (YOLO26 + D-Fire), fall (MediaPipe pose + temporal classifier)
    return detectors


def process(object_key: str, detectors: list[ClipDetector], batch_size: int = 8) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "video")
        download(object_key, path)
        scores: dict[str, list[WindowScore]] = {d.category: [] for d in detectors}
        batch = []
        for clip in iter_clips(path):
            batch.append(clip)
            if len(batch) == batch_size:
                _score(batch, detectors, scores)
                batch = []
        _score(batch, detectors, scores)

    incidents = []
    for d in detectors:
        for iv in merge_positive_windows(scores[d.category], d.threshold):
            incidents.append(
                {
                    "category": d.category,
                    "start_ms": iv.start_ms,
                    "end_ms": iv.end_ms,
                    "score": iv.score,
                    "model_version": d.model_version,
                }
            )
    return incidents


def _score(batch, detectors, scores) -> None:
    if not batch:
        return
    for d in detectors:
        for clip, s in zip(batch, d.score(batch), strict=True):
            scores[d.category].append(WindowScore(clip.start_ms, clip.end_ms, s))
