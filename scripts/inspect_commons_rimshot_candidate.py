#!/usr/bin/env python3
"""Verify the licence-free-to-fetch Rimshot discovery fixture.

The source labels the whole recording as Rimshots and says it contains four
rolls, but does not publish event timestamps.  Preserve that distinction so a
source discovery cannot be mistaken for independently timed accuracy evidence.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import wave


EXPECTED_SHA1 = "11b1e0f8e317aed2a75a7a1b0750c2d13e9221fd"
EXPECTED_SECONDS = 15.9078004535147


def sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render(path: Path) -> list[str]:
    actual_sha1 = sha1(path)
    if actual_sha1 != EXPECTED_SHA1:
        raise ValueError(f"{path}: expected SHA-1 {EXPECTED_SHA1}, got {actual_sha1}")
    with wave.open(str(path), "rb") as source:
        frames = source.getnframes()
        rate = source.getframerate()
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
    seconds = frames / rate
    if abs(seconds - EXPECTED_SECONDS) > 0.02:
        raise ValueError(f"{path}: expected {EXPECTED_SECONDS:.6f}s, got {seconds:.6f}s")
    return [
        "commons_rimshot_candidate: "
        f"sha1_verified=1 source_labelled=1 expected_rolls=4 temporal_annotations=0 "
        f"duration_seconds={seconds:.6f} channels={channels} sample_rate={rate} sample_width_bytes={sample_width}",
        "commons_rimshot_candidate: "
        "source=https://commons.wikimedia.org/wiki/File:Kevin_MacLeod_assorted_rimshots_-_13-second_roll.wav "
        "licence=CC-BY-3.0 candidate_only=1 reason=the source has no per-roll timestamps",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        lines = render(args.audio)
    except (OSError, ValueError, wave.Error) as error:
        parser.error(str(error))
    text = "\n".join(lines) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"commons_rimshot_candidate: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
