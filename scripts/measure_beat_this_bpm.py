#!/usr/bin/env python3
"""Measure the optional Beat This! neural tracker on an annotated fixture.

This script is deliberately offline-only.  It converts Beat This beat times to
one median local BPM inside each corpus-provided stable segment; it does not
feed the OBS analyser or claim that its non-causal model is live-safe.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import tempfile
from pathlib import Path
from statistics import median


def bpm_from_midi(path: Path) -> float:
    data = path.read_bytes()
    marker = data.find(b"\xff\x51\x03")
    if marker < 0 or marker + 6 > len(data):
        raise ValueError(f"missing MIDI tempo: {path}")
    return 60_000_000.0 / int.from_bytes(data[marker + 3:marker + 6], "big")


def tempo_from_beats(beats: list[float], start: float, duration: float) -> tuple[float, int]:
    """Return median BPM for inter-beat intervals fully inside the stable span."""
    if duration <= 0.0:
        raise ValueError("duration must be positive")
    end = start + duration
    local = sorted(float(beat) for beat in beats if start <= float(beat) <= end)
    intervals = [right - left for left, right in zip(local, local[1:]) if right > left]
    if not intervals:
        return 0.0, 0
    return 60.0 / median(intervals), len(intervals)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--model-cache-root", type=Path, required=True)
    parser.add_argument("--metadata", default="maestro-v3.0.0.csv")
    parser.add_argument("--checkpoint", default="small0")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seconds", type=float, default=20.0)
    parser.add_argument("--tolerance", type=float, default=8.0)
    args = parser.parse_args()
    if args.seconds <= 0.0 or args.tolerance < 0.0:
        parser.error("--seconds must be positive and --tolerance must be non-negative")
    site_packages = args.runtime_root / "site-packages"
    if not site_packages.is_dir():
        parser.error(f"Beat This dependencies are missing: {site_packages}")
    # Preserve the host PyTorch implementation.  The external directory only
    # supplies Beat This and the three dependencies not already available.
    sys.path.append(str(site_packages))
    # Both variables keep automatic checkpoint downloads outside the worktree.
    os.environ.setdefault("TORCH_HOME", str(args.model_cache_root / "cache"))
    os.environ.setdefault("XDG_CACHE_HOME", str(args.model_cache_root / "cache"))
    from beat_this.inference import File2Beats  # pylint: disable=import-outside-toplevel

    with (args.root / args.metadata).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    tracker = File2Beats(checkpoint_path=args.checkpoint, device=args.device, dbn=False)
    result_lines: list[str] = []
    for index, row in enumerate(rows, 1):
        expected = float(row["bpm"]) if row.get("bpm") else bpm_from_midi(args.root / row["midi_filename"])
        start = float(row.get("tempo_audio_offset_seconds", "0") or 0.0)
        available = float(row.get("tempo_duration_seconds", args.seconds) or args.seconds)
        duration = min(args.seconds, available)
        beats, _ = tracker(args.root / row["audio_filename"])
        raw, intervals = tempo_from_beats(list(beats), start, duration)
        error = abs(raw - expected)
        status = "hit" if error <= args.tolerance else "miss"
        result_lines.append(
            "Beat This tempo diag"
            f"\tid={index}\texpected={expected:.2f}\traw={raw:.2f}\tintervals={intervals}"
            f"\toffset={start:.3f}\tduration={duration:.3f}\terror={error:.2f}\tstatus={status}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.output.parent, delete=False) as handle:
        handle.write("\n".join(result_lines) + "\n")
        temporary = Path(handle.name)
    temporary.replace(args.output)
    print(f"Beat This tempo diagnostic: wrote {len(result_lines)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
