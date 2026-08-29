#!/usr/bin/env python3
"""Validate the externally cached official NSynth test split."""

import json
from pathlib import Path


ROOT = Path("build/nsynth_test_samples")


def main() -> None:
    examples = ROOT / "examples.json"
    audio = ROOT / "audio"
    if not examples.is_file() or not audio.is_dir():
        raise SystemExit("missing NSynth test fixtures; run make setup-nsynth-test-fixtures")
    metadata = json.loads(examples.read_text(encoding="utf-8"))
    wav_count = sum(1 for path in audio.iterdir() if path.suffix == ".wav")
    if len(metadata) != 4096:
        raise SystemExit(f"expected 4096 NSynth test metadata rows, got {len(metadata)}")
    if wav_count != len(metadata):
        raise SystemExit(f"expected {len(metadata)} NSynth test WAV files, got {wav_count}")
    families = sorted({row["instrument_family_str"] for row in metadata.values()})
    sources = sorted({row["instrument_source_str"] for row in metadata.values()})
    print(f"nsynth-test-examples={len(metadata)} wav={wav_count}")
    print("families=" + ",".join(families))
    print("sources=" + ",".join(sources))


if __name__ == "__main__":
    main()
