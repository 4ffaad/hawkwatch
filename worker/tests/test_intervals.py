from worker.intervals import WindowScore, merge_positive_windows


def test_merges_overlapping_positive_windows():
    w = [
        WindowScore(0, 2000, 0.2),
        WindowScore(1000, 3000, 0.8),
        WindowScore(2000, 4000, 0.9),
        WindowScore(8000, 10000, 0.7),
    ]
    out = merge_positive_windows(w, threshold=0.5)
    assert [(i.start_ms, i.end_ms) for i in out] == [(1000, 4000), (8000, 10000)]
    assert out[0].score == 0.9


def test_no_positives_gives_empty_timeline():
    assert merge_positive_windows([WindowScore(0, 2000, 0.1)], threshold=0.5) == []
