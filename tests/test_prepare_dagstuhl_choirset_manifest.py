#!/usr/bin/env python3
"""Regression check for deterministic DCS SATB manifest import."""

from __future__ import annotations

import json
import tempfile
import importlib.util
from pathlib import Path


PROJECT = Path(__file__).parents[1]
SCRIPT = PROJECT / "scripts" / "prepare_dagstuhl_choirset_manifest.py"
SPEC = importlib.util.spec_from_file_location("prepare_dcs", SCRIPT)
assert SPEC and SPEC.loader
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "DagstuhlChoirSet"
        scores = root / "annotations_csv_scorerepresentation"
        audio = root / "audio_wav_22050_mono"
        scores.mkdir(parents=True)
        audio.mkdir()
        for index in range(20):
            prefix = f"DCS_Test_{index:02d}"
            for role in "SATB":
                (scores / f"{prefix}_Stereo_STM_{role}.csv").write_text("0.0,1.0,60\n", encoding="utf-8")
                (audio / f"{prefix}_{role}1_LRX.wav").write_bytes(b"fixture")
        output = Path(temporary) / "prepared"
        assert IMPORTER.main(["--root", str(root), "--output", str(output)]) == 0
        pieces = json.loads((output / "manifest.json").read_text(encoding="utf-8"))["pieces"]
        assert len(pieces) == 20
        assert [source["instrument"] for source in pieces[0]["sources"]] == [52, 53, 54, 55]
        assert all(Path(source["notes"]).is_file() for source in pieces[0]["sources"])
    print("test_prepare_dagstuhl_choirset_manifest: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
