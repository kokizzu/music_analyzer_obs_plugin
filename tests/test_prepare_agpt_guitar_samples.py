#!/usr/bin/env python3
"""Fixture tests for AG-PT note-window and manifest preparation."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prepare_agpt", ROOT / "scripts" / "prepare_agpt_guitar_samples.py")
assert SPEC and SPEC.loader
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


def args() -> argparse.Namespace:
    return argparse.Namespace(limit=0, clip_seconds=0.32, attack_margin=0.03, next_note_gap=0.02)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "aGPTset"
        audio = root / "data" / "audio" / "player01.wav"
        audio.parent.mkdir(parents=True)
        audio.write_bytes(b"wav")
        metadata = root / "metadata"
        metadata.mkdir()
        (metadata / "note_labels.csv").write_text(
            "onset_label_seconds,audio_file_path,onset_label_samples,expressive_technique_id,pitch_midi\n"
            "0.0,player01.wav,0,3,64\n"
            "0.20,player01.wav,9600,3,65\n"
            "0.70,player01.wav,33600,7,60\n"
            "1.00,player01.wav,48000,7,\n",
            encoding="utf-8",
        )
        rows, skipped, labels = PREPARE.collect_candidates(root, args())
        assert labels.name == "note_labels.csv"
        assert len(rows) == 3
        assert skipped == {"unpitched_or_outside_range": 1}
        assert rows[0]["midi"] == 60
        close_row = next(row for row in rows if row["midi"] == 64)
        assert abs(close_row["duration"] - 0.15) < 1e-9
        selected = PREPARE.balanced_limit(rows, 2)
        assert len(selected) == 2
        output = Path(temporary) / "prepared"
        output.mkdir()
        for row in selected:
            path = output / row["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"wav")
        PREPARE.write_manifest(output / "manifest.tsv", selected, "fixture")
        assert PREPARE.manifest_complete(output / "manifest.tsv", "fixture", 2)
    print("test_prepare_agpt_guitar_samples: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
