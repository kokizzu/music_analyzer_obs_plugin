#!/usr/bin/env python3
"""Fixture test for AG-PT archive schema validation."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_agpt_guitar_archive.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        archive_path = Path(temporary) / "fixture.zip"
        root = "aGPTset"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(f"{root}/data/audio.zip", b"nested audio archive")
            archive.writestr(
                f"{root}/metadata/note_labels.csv",
                "onset_label_seconds,audio_file_path,onset_label_samples,expressive_technique_id,pitch_midi,string_number,playing_intensity\n"
                "0.0,player01.wav,0,1,64,1,forte\n",
            )
            archive.writestr(f"{root}/metadata/expressive_techniques.csv", "id,name\n1,pick\n")
            archive.writestr(f"{root}/metadata/files.csv", "filename\nplayer01.wav\n")
            archive.writestr(f"{root}/metadata/instruments.csv", "id,name\n1,guitar\n")
        result = subprocess.run(
            ["python3", str(SCRIPT), str(archive_path)], text=True, capture_output=True, check=False
        )
    assert result.returncode == 0, result.stderr
    assert "audio_file_metadata=1" in result.stdout
    assert "note_labels=1" in result.stdout
    assert "pitch_labelled_notes=1" in result.stdout
    print("test_inspect_agpt_guitar_archive: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
