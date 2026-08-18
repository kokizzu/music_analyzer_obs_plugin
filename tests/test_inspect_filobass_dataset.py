#!/usr/bin/env python3

from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import inspect_filobass_dataset  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "filobass"
        audio = root / "audio_bass_stems" / "All-The-Things-You-Are.mp3"
        midi = root / "midi_downbeat_aligned" / "All_the_Things_You_Are.mid"
        syncpoint = root / "syncpoints" / "All-the-Things-You-Are.csv"
        for path in (audio, midi, syncpoint):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fixture")
        output = root / "pairs.tsv"
        assert inspect_filobass_dataset.main(
            ["--root", str(root), "--output", str(output), "--min-pairs", "1"]
        ) == 0
        lines = output.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        assert lines[1].startswith("allthethingsyouare\t")
    print("test_inspect_filobass_dataset: 1 check passed")


if __name__ == "__main__":
    main()
