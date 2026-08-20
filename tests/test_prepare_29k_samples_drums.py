#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import tempfile
import wave
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_29k_samples_drums as prep


def wav_bytes() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16000)
        output.writeframes(b"\0\0" * 1600)
    return buffer.getvalue()


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "fixture.zip"
        with zipfile.ZipFile(archive, "w") as output:
            for code in ("ft", "mt", "ht", "cy"):
                for index in range(2):
                    output.writestr(f"29kSamples/{code}/sample_{index}.wav", wav_bytes())
            output.writestr("29kSamples/kd/ignored.wav", wav_bytes())
            output.writestr("../cy/unsafe.wav", wav_bytes())
        fixture = root / "fixture"
        assert prep.prepare(archive, fixture, limit=3, minimum=2) == 5
        rows = (fixture / "manifest.tsv").read_text(encoding="utf-8").splitlines()
        assert rows[0].split("\t") == list(prep.HEADER)
        assert sum(line.startswith("tom\t") for line in rows) == 3
        assert sum(line.startswith("ride\t") for line in rows) == 2
        assert not any("unsafe" in line for line in rows)
        assert prep.prepare(archive, fixture, limit=3, minimum=2) == 5
    print("test_prepare_29k_samples_drums: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
