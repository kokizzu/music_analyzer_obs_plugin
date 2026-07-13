#!/usr/bin/env python3
import inspect_urmp_dataset


def test_candidate_windows_respect_density_thresholds():
    track_notes = [
        [(0.0, 1.0, 60)],
        [(0.0, 1.0, 64)],
        [(0.0, 1.0, 67)],
    ]

    candidates = inspect_urmp_dataset.select_candidate_windows(
        track_notes,
        max_windows=4,
        min_active_tracks=3,
        min_pitch_classes=3,
    )
    assert len(candidates) == 1
    assert candidates[0]["active_tracks"] == 3
    assert candidates[0]["pitch_classes"] == 3

    assert not inspect_urmp_dataset.select_candidate_windows(
        track_notes,
        max_windows=4,
        min_active_tracks=4,
        min_pitch_classes=3,
    )
    assert not inspect_urmp_dataset.select_candidate_windows(
        track_notes,
        max_windows=4,
        min_active_tracks=3,
        min_pitch_classes=4,
    )


def test_density_summary():
    stats = inspect_urmp_dataset.RangeStats()
    stats.add(2)
    stats.add(4)
    assert stats.summary("candidate active tracks") == "candidate active tracks min/avg/max 2/3.00/4"


def main():
    test_candidate_windows_respect_density_thresholds()
    test_density_summary()
    print("test_inspect_urmp_dataset: 2 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
