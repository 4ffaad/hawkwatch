"""Turn per-window scores into reviewable intervals."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WindowScore:
    start_ms: int
    end_ms: int
    score: float


@dataclass(frozen=True)
class Interval:
    start_ms: int
    end_ms: int
    score: float  # max window score inside the interval


def merge_positive_windows(
    windows: list[WindowScore], threshold: float, max_gap_ms: int = 1000
) -> list[Interval]:
    """Merge overlapping/adjacent windows whose score >= threshold into intervals."""
    out: list[Interval] = []
    for w in sorted(windows, key=lambda w: w.start_ms):
        if w.score < threshold:
            continue
        if out and w.start_ms <= out[-1].end_ms + max_gap_ms:
            last = out[-1]
            out[-1] = Interval(last.start_ms, max(last.end_ms, w.end_ms), max(last.score, w.score))
        else:
            out.append(Interval(w.start_ms, w.end_ms, w.score))
    return out
