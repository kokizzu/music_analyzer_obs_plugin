#!/usr/bin/env python3
"""Audit a bounded, delayed Beat This! tempo estimate without OBS integration.

Each result is produced from a trailing audio window ending at the annotated
stable-window endpoint.  This permits whole-window attention, but never gives
the tracker future audio.  It is still a CPU-only research diagnostic: a live
route must separately pass latency and continuous-replay safety gates.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import tempfile
import time
from pathlib import Path

from measure_beat_this_bpm import bpm_from_midi, tempo_from_beats


def rolling_window_bounds(
    sample_count: int,
    sample_rate: int,
    stable_start: float,
    stable_duration: float,
    window_seconds: float,
) -> tuple[int, int, float, float]:
    """Return sample bounds and local stable span for a trailing causal window."""
    if sample_count <= 0 or sample_rate <= 0:
        raise ValueError("audio must contain samples at a positive sample rate")
    if stable_start < 0.0 or stable_duration <= 0.0 or window_seconds < stable_duration:
        raise ValueError("invalid stable span or rolling window")
    stable_end = stable_start + stable_duration
    if stable_end > sample_count / sample_rate:
        raise ValueError("stable span extends beyond audio")
    window_start = max(0.0, stable_end - window_seconds)
    first = int(window_start * sample_rate)
    last = min(sample_count, int(round(stable_end * sample_rate)))
    if last <= first:
        raise ValueError("rolling window is empty")
    return first, last, stable_start - window_start, stable_duration


def continuous_window_bounds(
    sample_count: int,
    sample_rate: int,
    stable_start: float,
    stable_duration: float,
    window_seconds: float,
    cadence_seconds: float,
    minimum_stable_seconds: float,
) -> list[tuple[int, int, float, float]]:
    """Return causal trailing-window bounds at each eligible stable output time."""
    if cadence_seconds <= 0.0 or minimum_stable_seconds <= 0.0:
        raise ValueError("cadence and minimum stable duration must be positive")
    if minimum_stable_seconds > stable_duration:
        raise ValueError("minimum stable duration exceeds the labelled stable span")
    output_durations: list[float] = []
    duration = minimum_stable_seconds
    while duration < stable_duration - 1.0e-6:
        output_durations.append(duration)
        duration += cadence_seconds
    if not output_durations or abs(output_durations[-1] - stable_duration) > 1.0e-6:
        output_durations.append(stable_duration)
    return [
        rolling_window_bounds(
            sample_count,
            sample_rate,
            stable_start,
            duration,
            window_seconds,
        )
        for duration in output_durations
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--model-cache-root", type=Path, required=True)
    parser.add_argument("--metadata", default="maestro-v3.0.0.csv")
    parser.add_argument("--checkpoint", default="final0")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seconds", type=float, default=20.0)
    parser.add_argument("--window-seconds", type=float, default=20.0)
    parser.add_argument("--cadence-seconds", type=float, default=0.0)
    parser.add_argument("--minimum-stable-seconds", type=float, default=10.0)
    parser.add_argument("--tolerance", type=float, default=8.0)
    args = parser.parse_args()
    if args.seconds <= 0.0 or args.window_seconds < args.seconds or args.tolerance < 0.0:
        parser.error("--seconds must be positive, --window-seconds must cover it, and --tolerance non-negative")
    if args.cadence_seconds < 0.0 or args.minimum_stable_seconds <= 0.0:
        parser.error("--cadence-seconds must be non-negative and --minimum-stable-seconds must be positive")
    site_packages = args.runtime_root / "site-packages"
    if not site_packages.is_dir():
        parser.error(f"Beat This dependencies are missing: {site_packages}")
    sys.path.append(str(site_packages))
    os.environ.setdefault("TORCH_HOME", str(args.model_cache_root / "cache"))
    os.environ.setdefault("XDG_CACHE_HOME", str(args.model_cache_root / "cache"))
    from beat_this.inference import Audio2Beats  # pylint: disable=import-outside-toplevel
    from beat_this.preprocessing import load_audio  # pylint: disable=import-outside-toplevel

    with (args.root / args.metadata).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    tracker = Audio2Beats(checkpoint_path=args.checkpoint, device=args.device, dbn=False)
    result_lines: list[str] = []
    for index, row in enumerate(rows, 1):
        expected = float(row["bpm"]) if row.get("bpm") else bpm_from_midi(args.root / row["midi_filename"])
        stable_start = float(row.get("tempo_audio_offset_seconds", "0") or 0.0)
        available = float(row.get("tempo_duration_seconds", args.seconds) or args.seconds)
        stable_duration = min(args.seconds, available)
        signal, sample_rate = load_audio(args.root / row["audio_filename"])
        if args.cadence_seconds > 0.0:
            bounds = continuous_window_bounds(
                len(signal), int(sample_rate), stable_start, stable_duration,
                args.window_seconds, args.cadence_seconds, args.minimum_stable_seconds,
            )
        else:
            bounds = [rolling_window_bounds(
                len(signal), int(sample_rate), stable_start, stable_duration, args.window_seconds
            )]
        for output_index, (first, last, local_start, local_duration) in enumerate(bounds, 1):
            started = time.monotonic()
            beats, _ = tracker(signal[first:last], sample_rate)
            elapsed = time.monotonic() - started
            raw, intervals = tempo_from_beats(list(beats), local_start, local_duration)
            error = abs(raw - expected)
            status = "hit" if error <= args.tolerance else "miss"
            result_lines.append(
                "Beat This rolling tempo diag"
                f"\tid={index}\toutput={output_index}\texpected={expected:.2f}\traw={raw:.2f}\tintervals={intervals}"
                f"\tstable_offset={stable_start:.3f}\tstable_duration={local_duration:.3f}"
                f"\twindow_seconds={args.window_seconds:.3f}\twall_seconds={elapsed:.3f}"
                f"\tmodel={args.checkpoint}\terror={error:.2f}\tstatus={status}"
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.output.parent, delete=False) as handle:
        handle.write("\n".join(result_lines) + "\n")
        temporary = Path(handle.name)
    temporary.replace(args.output)
    print(f"Beat This rolling tempo diagnostic: wrote {len(result_lines)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
