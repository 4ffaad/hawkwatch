# HawkWatch build checklist

Paths are proposed for a new project. Each numbered item has a completion check.

## Local proof of concept

- [ ] **1. Run pretrained detection** · No dependencies · Small, `experiments/`. Run YOLO26n on one authorized short clip. Play the annotated output and record model version, device, elapsed time, and video duration.
- [ ] **2. Lock dataset splits** · No dependencies · Medium, `ml/data/`. Record RWF-2000 usage terms, checksums, seed, and source grouping in a manifest. Verify no source group or known near-duplicate crosses splits. Record provenance gaps.
- [ ] **3. Evaluate a fight model** · After 2 · Medium, `ml/fight/`. Fine-tune VideoMAE on a GPU, select threshold on validation data, and generate held-out results with confusion counts, precision, recall, F1, and false-positive rate. Verify a saved checkpoint reproduces predictions on a small fixture.

**Checkpoint** Run detection and reproduce the fight benchmark from its manifest and checkpoint.

## First end-to-end release

- [ ] **4. Upload and verify one video** · After 1 · Medium, `api/`, `web/`, `infra/compose.yaml`. An authenticated user can upload to private storage and see the resulting job ID. Verify missing, oversized, and unauthorized uploads cannot enqueue work.
- [ ] **5. Process jobs asynchronously** · After 4 · Medium, `worker/`, `api/migrations/`. Process a fixture via a durable leased job, expose queued/running/completed/failed states, and report decoding errors. Kill a worker mid-job and verify another retries with bounded attempts and only one committed result.
- [ ] **6. Review real fight candidates** · After 3 and 5 · Medium, `worker/`, `web/`. Run overlapping windows, merge adjacent positives, and return timestamps, scores, model version, and evidence. Open a clip from the timeline and confirm or dismiss it. Verify review attribution, cross-user isolation, and retained evidence deletion.

**Checkpoint** Upload one positive and one negative authorized recording through the UI. Verify evidence playback, a valid empty timeline, and recovery after a forced retry. Record false alerts per hour and timing error on annotated long clips.

## Additional incident types

- [ ] **7. Add fire and smoke** · After 6 · Medium, `ml/fire/`, `worker/`. Fine-tune on D-Fire and produce reviewable intervals through the existing pipeline. Report per-class AP and review errors on confounder clips.
- [ ] **8. Add the fall pilot** · After 6 · Medium, `ml/fall/`, `worker/`. Use MediaPipe landmarks and a temporal classifier on UR Fall. Verify participant separation where supported and report performance on daily activities and missing-pose sequences.
- [ ] **9. Add timestamped report drafts** · After 6 · Small, `api/`, `web/`. Generate an observable-event summary for each candidate. Verify summary timestamps and categories match stored evidence. Evaluate a VLM only if templates leave a demonstrated gap.

**Checkpoint** Verify each supported category reaches the same review workflow, with metrics tied to its model version.

## AWS and portfolio demo

- [ ] **10. Deploy staging API and storage** · After 6 · Medium, `infra/aws/`, `.github/workflows/`. Deploy two API tasks behind an ALB, private S3, and RDS. Verify routing to both tasks, scoped evidence access, and an automated staging smoke test.
- [ ] **11. Deploy queue and GPU workers** · After 10 · Medium, `infra/aws/`, `api/`, `worker/`. Publish through an outbox to SQS, use a dead-letter queue, and set worker capacity bounds. Force a duplicate delivery and a worker restart. Verify neither duplicates incidents nor strands jobs.
- [ ] **12. Run and record the scale demo** · After 7–11 · Medium, `tests/load/`, `infra/aws/`. Exercise five simultaneous uploads and compare one-worker and two-worker runs. Report queue wait, inference duration, end-to-end latency and error rate. Verify CloudWatch alarms for aged jobs and worker failures, and display held-out model metrics in the dashboard.

**Checkpoint** Demonstrate the upload-to-review workflow, independent worker scaling, and successful recovery under the stated load. Capture the measured results and stage teardown steps.
