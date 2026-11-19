# HawkWatch implementation plan

Build a private, upload-only incident review application with timestamped evidence and human decisions. Start with possible fights, then add visible fire and smoke, then a fall detection pilot. Keep the first demo limited to authorized footage, authenticated reviewers, and in-app alerts.

## Architecture

Next.js requests an upload through FastAPI. The browser uploads directly to private object storage using a short-lived signed URL. FastAPI verifies the stored object before recording a queued job. A separate Python worker reads the video, produces candidate intervals, and saves incidents and evidence references. The dashboard polls FastAPI for progress and lets a reviewer confirm or dismiss each candidate.

Use PostgreSQL for job state, incident records, and review history. Start with a PostgreSQL-backed queue with renewable leases in Docker Compose. On AWS, publish to SQS via a transactional outbox so an API restart between transaction commit and delivery cannot lose jobs. Tie each job to the verified object version or an immutable object key, and make result commits idempotent across deliveries. Use S3, RDS PostgreSQL, an Application Load Balancer with two FastAPI tasks on ECS/Fargate, and separate ECS on EC2 GPU capacity. Use SQS backlog and age to tune worker scaling and CloudWatch to observe failures. Add Redis caching when measured read load warrants it. [ECS scaling guidance](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/capacity-autoscaling-best-practice.html)

## Model and release decisions

- **Person tracking.** First benchmark pretrained [YOLO26n](https://docs.ultralytics.com/models/yolo26/) on your MacBook and produce annotated output. Add ByteTrack when track continuity helps the review evidence. Keep person tracking optional in fight inference until evaluation shows a benefit.
- **Fights.** Fine-tune [VideoMAE Base](https://huggingface.co/MCG-NJU/videomae-base-finetuned-kinetics) using [RWF-2000](https://github.com/mchengny/RWF2000-Video-Database-for-Violence-Detection). Group by source recording where provenance permits and check near-duplicates before splitting. Use validation to choose thresholds and held-out footage for final reporting. Report clip precision, recall, F1 and false-positive rate. On separate authorized long videos, label intervals and measure false alerts per video hour and timestamp accuracy. Clip scores alone cannot establish localization quality.
- **Fire and smoke.** Fine-tune a separate YOLO26n detector on [D-Fire](https://github.com/gaia-solutions-on-demand/DFireDataset). Measure per-class AP and test temporal aggregation on held-out footage with steam, glare, or haze.
- **Falls.** Extract pose landmarks with [MediaPipe Pose](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker) and fit a small temporal classifier on [UR Fall](https://fenix.ur.edu.pl/~mkepski/ds/uf.html). Group by participant where IDs are available. Report confusion with sitting and bending and track unavailable pose estimates. Keep this a pilot until evaluated on broader authorized footage.
- **Reports.** Start with timestamped templates tied to model evidence. Optionally evaluate [Qwen3-VL](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct) or [Gemini](https://ai.google.dev/gemini-api/docs/video-understanding) for draft summaries. Review reports against the clip and restrict external processing to footage cleared for that provider.
- **Permissions.** Record dataset provenance and allowed uses before downloading, training, or publishing artifacts. Keep raw footage private with scoped playback, audit history, and tested retention/deletion. Review dataset and model terms before sharing weights or making a public demo.
- **Later research.** Use an authorized [UCF-Crime](https://www.crcv.ucf.edu/research/real-world-anomaly-detection-in-surveillance-videos/) subset for temporal localization if needed. Bookmark [XD-Violence](https://roc-ng.github.io/XD-Violence/) for audio-video experiments. Live CCTV, identity recognition, and automated dispatch are outside the planned release.

## Demo target

Start with five concurrent authorized uploads as a proposed test workload. Show two API replicas, independent worker scaling, a recovered worker failure with one incident set, and a review timeline with timestamped evidence. Display backlog, queue wait, inference time, and upload-to-review latency. Show model metrics from a versioned evaluation report alongside operational metrics. Establish latency and accuracy targets after measuring the baseline.

The [implementation checklist](todo.md) records dependencies and verification. Dataset provenance and the upload workflow can advance independently after the local proof of concept. The first merged model path depends on both.
