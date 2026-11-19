"""Milestone 1: run pretrained YOLO26n on a short clip and record timing.

    uv run --with ultralytics python experiments/run_yolo.py path/to/clip.mp4
"""

import json
import platform
import sys
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
    raise SystemExit("usage: run_yolo.py <path to an existing video file>")
src = sys.argv[1]
device = "mps" if platform.system() == "Darwin" else "cpu"

cap = cv2.VideoCapture(src)
duration_s = cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or 30)
cap.release()

out_dir = Path("runs/yolo26n").resolve()
model = YOLO("models/yolo26n.pt")
t0 = time.perf_counter()
frames = 0
# stream=True yields one result per frame instead of holding the whole video in memory.
for _ in model.predict(
    source=src, device=device, classes=[0], save=True, stream=True, verbose=False,
    project=str(out_dir.parent), name=out_dir.name, exist_ok=True,
):
    frames += 1
elapsed = time.perf_counter() - t0

record = {
    "model": "models/yolo26n.pt",
    "device": device,
    "video": Path(src).name,
    "video_duration_s": round(duration_s, 2),
    "frames": frames,
    "elapsed_s": round(elapsed, 2),
    "realtime_factor": round(duration_s / elapsed, 2) if elapsed else None,
}
print(json.dumps(record, indent=2))
(out_dir / f"{Path(src).stem}.benchmark.json").write_text(json.dumps(record, indent=2))
