"""Regression checks for the bounded ENST-Drums fixture builder."""
from __future__ import annotations

import io
import sys
import tarfile
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_enst_drums_samples as prep


def wav_bytes() -> bytes:
    data = io.BytesIO()
    with wave.open(data, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16000)
        output.writeframes(b"\0\0" * 1600)
    return data.getvalue()


def add(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    member = tarfile.TarInfo(name)
    member.size = len(data)
    archive.addfile(member, io.BytesIO(data))


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive_path = root / "enst.tar.gz"
        with tarfile.open(archive_path, "w:gz") as archive:
            for index, label in enumerate(("hits_rim-shot", "hits_cross-sticks", "hits_medium-tom", "hits_ride-cymbal"), start=1):
                base = f"enst/drummer_3/annotation/{index:03d}_{label}_sticks_x5.txt"
                add(archive, base, b"0.100 sd\n0.300 sd\n")
                audio = f"enst/drummer_3/audio/dry_mix/{index:03d}_{label}_sticks_x5.wav"
                add(archive, audio, wav_bytes())
        output = root / "fixture"
        counts = prep.prepare(archive_path, output, limit=8, minimum=1)
        assert counts == {"rim": 2, "tom": 1, "ride": 1}
        rows = (output / "manifest.tsv").read_text(encoding="utf-8").splitlines()
        assert len(rows) == 5
        assert all("\t2\tENST-Drums:" in row for row in rows[1:])
        assert prep.category_for_annotation("enst/drummer_3/annotation/047_hits_rim-shot_sticks_x5.txt") == "rim"
        assert prep.category_for_annotation("enst/drummer_3/annotation/048_hits_cross-sticks_sticks_x5.txt") == "rim"
        assert prep.category_for_annotation("enst/drummer_3/annotation/001_hits_snare-drum_sticks_x5.txt") is None
    print("test_prepare_enst_drums_samples: ok")


if __name__ == "__main__":
    main()
