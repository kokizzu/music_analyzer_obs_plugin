#!/usr/bin/env python3

import csv
from collections import Counter
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_ballroom_tempo_fixture.py"


def write_stable_beats(path: Path) -> None:
    path.write_text("".join(f"{second:.1f}\n" for second in range(16)), encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        audio_root = root / "audio"
        annotations_root = root / "annotations"
        output = root / "fixture"
        styles = ("ChaCha", "Jive", "Samba", "Waltz")
        for style in styles:
            for number in range(4):
                name = f"{style}-{number:02d}"
                wav = audio_root / style / f"{name}.wav"
                wav.parent.mkdir(parents=True, exist_ok=True)
                wav.write_bytes(b"fixture")
                annotations_root.mkdir(exist_ok=True)
                write_stable_beats(annotations_root / f"{name}.beats")
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--audio-root", str(audio_root),
                "--annotations-root", str(annotations_root),
                "--output", str(output),
                "--limit", "8",
            ],
            check=True,
        )
        with (output / "maestro-v3.0.0.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        selected_styles = Counter(
            (output / row["audio_filename"]).resolve().parent.name for row in rows
        )
        assert len(rows) == 8
        assert selected_styles == Counter({style: 2 for style in styles})
    print("test_prepare_ballroom_tempo_fixture: genre-balanced selection passed")


if __name__ == "__main__":
    main()
