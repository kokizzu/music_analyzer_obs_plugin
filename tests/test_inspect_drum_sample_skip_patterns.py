#!/usr/bin/env python3

import math
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write_wav(path: Path, frequency: float = 120.0, seconds: float = 0.08, sample_rate: int = 48000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for index in range(int(seconds * sample_rate)):
        sample = int(math.sin(2.0 * math.pi * frequency * index / sample_rate) * 12000)
        frames.append(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sample_rate)
        file.writeframes(b"".join(frames))


def test_reports_skip_reasons_and_tokens() -> None:
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "source"
        write_wav(source / "kit" / "Kick 01.wav", frequency=80.0)
        write_wav(source / "kit" / "Noise Burst.wav", frequency=900.0)
        write_wav(source / "kit" / "Snare Loop.wav", frequency=250.0)
        write_wav(source / "kit" / "Handclap.wav", frequency=850.0)
        write_wav(source / "kit" / "Crash Long.wav", frequency=500.0, seconds=3.5)

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_drum_sample_skip_patterns.py"),
                "--source",
                str(source),
                "--no-archives",
                "--top",
                "4",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = completed.stdout

        for expected in (
            "excluded_loop=1",
            "unsupported_percussion=1",
            "uncategorized=1",
            "bad_duration=1",
        ):
            if expected not in output:
                raise AssertionError(output)
        if "reason uncategorized rows=1" not in output or "tokens noise=1 burst=1" not in output:
            raise AssertionError(output)
        if "reason unsupported_percussion rows=1" not in output or "stems handclap=1" not in output:
            raise AssertionError(output)
        if "reason bad_duration rows=1" not in output or "crash long" not in output:
            raise AssertionError(output)


def test_filters_skipped_rows_by_label_and_reason() -> None:
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "source"
        write_wav(source / "kit" / "Noise Burst.wav", frequency=900.0)
        write_wav(source / "kit" / "Handclap.wav", frequency=850.0)

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_drum_sample_skip_patterns.py"),
                "--source",
                str(source),
                "--no-archives",
                "--top",
                "4",
                "--skip-label-filter",
                "noise",
                "--skip-reason",
                "uncategorized",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = completed.stdout

        if "skipped=1" not in output or "uncategorized=1" not in output:
            raise AssertionError(output)
        if "noise burst" not in output or "handclap" in output:
            raise AssertionError(output)


def test_reports_invalid_filter_regex() -> None:
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "source"
        write_wav(source / "kit" / "Noise Burst.wav", frequency=900.0)

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "inspect_drum_sample_skip_patterns.py"),
                "--source",
                str(source),
                "--no-archives",
                "--skip-label-filter",
                "(",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if completed.returncode == 0:
            raise AssertionError("invalid regex should fail")
        if "invalid regex" not in completed.stderr:
            raise AssertionError(completed.stderr)


def main() -> int:
    test_reports_skip_reasons_and_tokens()
    test_filters_skipped_rows_by_label_and_reason()
    test_reports_invalid_filter_regex()
    print("test_inspect_drum_sample_skip_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
