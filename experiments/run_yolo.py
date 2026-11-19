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

src = sys.argv[1]
device = "mps" if platform.system() == "Darwin" else "cpu"

cap = cv2.VideoCapture(src)
duration_s = cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or 30)
cap.release()

model = YOLO("yolo26n.pt")
t0 = time.perf_counter()
model.predict(source=src, device=device, classes=[0], save=True, project="runs", name="yolo26n", verbose=False)
elapsed = time.perf_counter() - t0

record = {
    "model": "yolo26n.pt",
    "device": device,
    "video": Path(src).name,
    "video_duration_s": round(duration_s, 2),
    "elapsed_s": round(elapsed, 2),
    "realtime_factor": round(duration_s / elapsed, 2) if elapsed else None,
}
print(json.dumps(record, indent=2))
Path("runs/yolo26n").mkdir(parents=True, exist_ok=True)
Path("runs/yolo26n/benchmark.json").write_text(json.dumps(record, indent=2))
