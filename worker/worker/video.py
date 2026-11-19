"""Decode a video into overlapping clips of frames."""

from collections.abc import Iterator
from dataclasses import dataclass

import cv2
import numpy as np


class VideoDecodeError(Exception):
    pass


@dataclass
class Clip:
    start_ms: int
    end_ms: int
    frames: list[np.ndarray]  # RGB, HxWx3


def iter_clips(
    path: str, clip_frames: int = 16, sample_fps: float = 8.0, stride_frames: int = 8
) -> Iterator[Clip]:
    """Sample frames at `sample_fps` and yield clips of `clip_frames` with `stride_frames` hop."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise VideoDecodeError(f"cannot open {path}")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, round(src_fps / sample_fps))
    buf: list[tuple[int, np.ndarray]] = []
    idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                ts = int(idx / src_fps * 1000)
                buf.append((ts, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                if len(buf) == clip_frames:
                    yield Clip(buf[0][0], ts, [f for _, f in buf])
                    buf = buf[stride_frames:]
            idx += 1
    finally:
        cap.release()
    if idx == 0:
        raise VideoDecodeError(f"no frames decoded from {path}")
