from typing import Protocol

from worker.video import Clip


class ClipDetector(Protocol):
    category: str  # matches incidents.category enum
    model_version: str
    threshold: float

    def score(self, clips: list[Clip]) -> list[float]: ...
