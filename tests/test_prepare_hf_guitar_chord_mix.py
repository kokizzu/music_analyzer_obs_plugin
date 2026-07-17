#!/usr/bin/env python3

import json
from pathlib import Path
import sys
import tempfile
import wave


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_hf_guitar_chord_mix


def write_wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)
        wav.writeframes(b"\x00\x00" * 22050)


def write_jams(path, notes):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"annotations": [], "file_metadata": {"duration": 1.0}}
    for string_index, midi in enumerate(notes):
        payload["annotations"].append({
            "namespace": "note_midi",
            "annotation_metadata": {"data_source": str(string_index)},
            "data": [{
                "time": 0.100,
                "duration": 0.800,
                "value": float(midi),
                "confidence": None,
            }],
        })
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_source_clip(root, name, notes):
    stem = Path("clips") / "isolated-chords" / name
    write_wav(root / stem.with_suffix(".wav"))
    write_jams(root / stem.with_suffix(".jams"), notes)
    return stem


def write_tree(path, stems):
    entries = []
    for stem in stems:
        entries.append({"type": "file", "path": str(stem.with_suffix(".jams"))})
        entries.append({"type": "file", "path": str(stem.with_suffix(".wav"))})
    path.write_text(json.dumps(entries), encoding="utf-8")


def manifest_lines(path):
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_prepare(base, stems, limit=0, min_samples=1):
    tree = base / "tree.json"
    write_tree(tree, stems)
    output = base / "out"
    prepare_hf_guitar_chord_mix.main([
        "--tree-json",
        str(tree),
        "--base-url",
        (base / "source").as_uri(),
        "--output",
        str(output),
        "--limit",
        str(limit),
        "--min-samples",
        str(min_samples),
        "--timeout",
        "5",
        "--progress-every",
        "0",
    ])
    return output


def test_hf_guitar_chord_mix_manifest_is_prepared():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        stems = [
            write_source_clip(source, "C_C_guitar_1", [40, 48, 52, 55, 60, 64]),
            write_source_clip(source, "G_G_guitar_1", [43, 47, 50, 55, 59, 67]),
        ]
        output = run_prepare(base, stems, min_samples=2)
        lines = manifest_lines(output / "manifest.tsv")
        audio = [line for line in lines if line.startswith("AUDIO\t")]
        notes = [line for line in lines if line.startswith("NOTE\t")]
        if len(audio) != 2:
            raise AssertionError(f"expected 2 AUDIO rows, got {len(audio)}")
        if len(notes) != 12:
            raise AssertionError(f"expected 12 NOTE rows, got {len(notes)}")
        for line in audio:
            audio_path = Path(line.split("\t")[2])
            if not audio_path.is_absolute() or not audio_path.is_file():
                raise AssertionError(f"expected absolute downloaded audio path, got {audio_path}")


def test_limit_spreads_across_chord_labels():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        stems = [
            write_source_clip(source, "C_C_guitar_1", [40, 48, 52, 55, 60, 64]),
            write_source_clip(source, "C_C_guitar_2", [40, 48, 52, 55, 60, 64]),
            write_source_clip(source, "G_G_guitar_1", [43, 47, 50, 55, 59, 67]),
        ]
        output = run_prepare(base, stems, limit=2, min_samples=2)
        lines = manifest_lines(output / "manifest.tsv")
        audio_ids = [line.split("\t")[1] for line in lines if line.startswith("AUDIO\t")]
        if len(audio_ids) != 2:
            raise AssertionError(f"expected 2 limited AUDIO rows, got {audio_ids}")
        if not any("_C_C_" in item for item in audio_ids) or not any("_G_G_" in item for item in audio_ids):
            raise AssertionError(f"expected spread across C and G labels, got {audio_ids}")


def test_minimum_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = base / "source"
        stems = [
            write_source_clip(source, "C_C_guitar_1", [40, 48, 52, 55, 60, 64]),
        ]
        try:
            run_prepare(base, stems, min_samples=2)
        except SystemExit:
            partial = base / "out" / "manifest.tsv.partial"
            lines = manifest_lines(partial)
            if len([line for line in lines if line.startswith("AUDIO\t")]) != 1:
                raise AssertionError("partial manifest should contain the prepared row")
        else:
            raise AssertionError("expected min-samples failure")


def main():
    test_hf_guitar_chord_mix_manifest_is_prepared()
    test_limit_spreads_across_chord_labels()
    test_minimum_failure_writes_partial_manifest()
    print("test_prepare_hf_guitar_chord_mix: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
