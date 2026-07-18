#!/usr/bin/env python3

import csv
from pathlib import Path
import sys
import tempfile
import wave


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_gaps_guitar_samples


def write_wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)
        wav.writeframes(b"\x00\x00" * 22050)


def write_match(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join([
            "info(midiClockUnits,480).",
            "info(midiClockRate,500000).",
            "snote(p0n0,[C,n],4,1:1,0,1/4,0.0000,1.0000,[v1])-note(n1,60,0,480,90,0,0).",
            "insertion-note(n2,64,240,720,80,0,0).",
            "snote(p0n1,[G,n],4,1:2,0,1/8,1.0000,1.5000,[v1])-deletion.",
            "snote(p0n2,[G,n],4,1:3,0,1/4,1.5000,2.0000,[v1])-note(n3,67,720,960,70,0,0).",
            "",
        ]),
        encoding="utf-8",
    )


def write_metadata(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "audio_path", "midi_path", "split"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def manifest_lines(path):
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_prepare(base, rows, limit=0, min_samples=1):
    source = base / "source"
    for row in rows:
        sample_id = row["id"]
        write_wav(source / row["audio_path"])
        write_match(source / "match" / f"{sample_id}.match")
    metadata = base / "metadata.csv"
    write_metadata(metadata, rows)
    output = base / "out"
    prepare_gaps_guitar_samples.main([
        "--metadata",
        str(metadata),
        "--base-url",
        source.as_uri(),
        "--output",
        str(output),
        "--source-dir",
        str(base / "sources"),
        "--limit",
        str(limit),
        "--min-samples",
        str(min_samples),
        "--min-notes",
        "1",
        "--progress-every",
        "0",
    ])
    return output


def test_gaps_manifest_is_prepared_from_match_notes():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        rows = [{
            "id": "001_test",
            "audio_path": "audio/001_test.wav",
            "midi_path": "midi/001_test.mid",
            "split": "train",
        }]
        output = run_prepare(base, rows, min_samples=1)
        lines = manifest_lines(output / "manifest.tsv")
        audio = [line for line in lines if line.startswith("AUDIO\t")]
        notes = [line for line in lines if line.startswith("NOTE\t")]
        if len(audio) != 1:
            raise AssertionError(f"expected 1 AUDIO row, got {audio}")
        if len(notes) != 3:
            raise AssertionError(f"expected 3 NOTE rows from match notes, got {notes}")
        if not any("\t0.250000\t0.750000\t64" in line for line in notes):
            raise AssertionError(f"expected tick-to-second conversion for E4 insertion, got {notes}")
        audio_path = Path(audio[0].split("\t")[2])
        if not audio_path.is_absolute() or not audio_path.is_file():
            raise AssertionError(f"expected absolute cached audio path, got {audio_path}")


def test_gaps_limit_spreads_across_splits():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        rows = [
            {"id": "001_train", "audio_path": "audio/001_train.wav",
             "midi_path": "midi/001_train.mid", "split": "train"},
            {"id": "002_train", "audio_path": "audio/002_train.wav",
             "midi_path": "midi/002_train.mid", "split": "train"},
            {"id": "003_test", "audio_path": "audio/003_test.wav",
             "midi_path": "midi/003_test.mid", "split": "test"},
        ]
        output = run_prepare(base, rows, limit=2, min_samples=2)
        audio_ids = [line.split("\t")[1] for line in manifest_lines(output / "manifest.tsv")
                     if line.startswith("AUDIO\t")]
        if set(audio_ids) != {"001_train", "003_test"}:
            raise AssertionError(f"expected split-spread rows, got {audio_ids}")


def test_gaps_minimum_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        rows = [{
            "id": "001_test",
            "audio_path": "audio/001_test.wav",
            "midi_path": "midi/001_test.mid",
            "split": "train",
        }]
        try:
            run_prepare(base, rows, min_samples=2)
        except SystemExit:
            partial = base / "out" / "manifest.tsv.partial"
            lines = manifest_lines(partial)
            if len([line for line in lines if line.startswith("AUDIO\t")]) != 1:
                raise AssertionError("partial manifest should contain the prepared GAPS row")
        else:
            raise AssertionError("expected min-samples failure")


def main():
    test_gaps_manifest_is_prepared_from_match_notes()
    test_gaps_limit_spreads_across_splits()
    test_gaps_minimum_failure_writes_partial_manifest()
    print("test_prepare_gaps_guitar_samples: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
