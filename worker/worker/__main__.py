import logging
import signal
import threading
import time

from worker import queue
from worker.config import settings
from worker.pipeline import load_detectors, process
from worker.video import VideoDecodeError

log = logging.getLogger("worker")
stop = threading.Event()


def _heartbeat(lease: queue.Lease, done: threading.Event, lost: threading.Event) -> None:
    while not done.wait(settings.worker_lease_seconds / 3):
        try:
            queue.renew(lease)
        except queue.LeaseLost:
            lost.set()
            return


def run_one(detectors) -> bool:
    lease = queue.claim()
    if lease is None:
        return False
    log.info("claimed job %s (attempt %d)", lease.job_id, lease.attempt)
    done, lost = threading.Event(), threading.Event()
    hb = threading.Thread(target=_heartbeat, args=(lease, done, lost), daemon=True)
    hb.start()
    started = time.monotonic()
    try:
        incidents = process(lease.object_key, detectors)
        if lost.is_set():
            raise queue.LeaseLost(str(lease.job_id))
        queue.complete(lease, incidents)
        log.info(
            "job %s completed: %d incidents in %.1fs",
            lease.job_id, len(incidents), time.monotonic() - started,
        )
    except queue.LeaseLost:
        log.warning("lost lease on job %s; discarding results", lease.job_id)
    except VideoDecodeError as e:
        queue.fail(lease, f"decode error: {e}", retryable=False)
    except Exception as e:
        log.exception("job %s failed", lease.job_id)
        queue.fail(lease, repr(e), retryable=True)
    finally:
        done.set()
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    detectors = load_detectors()
    if not detectors:
        log.warning("no detectors configured (set FIGHT_MODEL_PATH); jobs will complete empty")
    log.info("worker %s polling", settings.worker_id)
    while not stop.is_set():
        if not run_one(detectors):
            stop.wait(settings.worker_poll_seconds)


if __name__ == "__main__":
    main()
