#!/usr/bin/env python3
"""Verify the actual native display path against an independent paired engine."""
import csv
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from measure_sustained_analyzer import source_reference

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-notes", action="store_true")
    parser.add_argument("--spectral", action="store_true")
    parser.add_argument("--primary", action="store_true")
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, default=1)
    args = parser.parse_args()
    assert args.shards > 0 and 0 <= args.shard < args.shards
    if args.single_notes:
        base = ROOT / "build/real_note_samples"
        with (base / "manifest.tsv").open() as stream:
            manifest = list(csv.DictReader(stream, delimiter="\t"))
        subset = [row for index, row in enumerate(manifest) if index % args.shards == args.shard]
        selected = {row["id"]: dict(id=row["id"], family=row["family"], midi=int(row["midi"]), cohort="protected",
                    original_audio=str((base / row["path"]).relative_to(ROOT)), audio_sha256=digest(base / row["path"])) for row in subset}
        preparation = dict(selection=list(selected.values()), manifest_sha256=digest(base / "manifest.tsv"))
    else:
        base = ROOT / "build/next_piano_timbre" / ("cdf899eac5ec" if args.spectral else "583e69ce750b")
        preparation = json.loads((base / "checkpoint.json").read_text())
        selected = {row["id"]: row for row in preparation["selection"]}
        assert digest(base / "manifest.tsv") == preparation["manifest_sha256"]
        assert all(digest(base / "audio" / (sample + ".wav")) == expected for sample, expected in preparation["derived_audio_sha256"].items())
    paths = ["src/analyzer.cpp", "src/analyzer.hpp", "src/keyboard_voice_classifier.hpp", "src/keyboard_voice_model_data.hpp",
             "src/native_mfcc_voice.hpp", "src/native_mfcc_voice_model_data.hpp", "src/native_timbre_features.hpp",
             "tests/native_keyboard_voice_pair.cpp", "tests/non_tempo_snapshot.hpp", "build/native_keyboard_voice_pair", "scripts/measure_keyboard_voice_pair.py"]
    binary = ROOT / 'build/native_keyboard_voice_pair'
    if args.primary:
        checkpoints = sorted((ROOT / 'build/primary_voice_trial').glob('*/checkpoint.json'), key=lambda p: p.stat().st_mtime)
        assert checkpoints, 'Run make prepare-native-voice-primary first'
        checkpoint = checkpoints[-1]
        primary = checkpoint.parent
        pinned = json.loads(checkpoint.read_text())
        assert digest(primary / 'src/analyzer.cpp') == pinned['candidate_cpp_sha256']
        assert digest(primary / 'src/analyzer.hpp') == pinned['candidate_hpp_sha256']
        assert digest(primary / 'build/native_keyboard_voice_pair') == pinned['binary_sha256']
        replacements = ['src/analyzer.cpp', 'src/analyzer.hpp', 'tests/native_keyboard_voice_pair.cpp',
                        'tests/non_tempo_snapshot.hpp', 'build/native_keyboard_voice_pair']
        paths = [str((primary / p).relative_to(ROOT)) if p in replacements else p for p in paths]
        paths += [str(checkpoint.relative_to(ROOT)), 'scripts/prepare_native_voice_primary.py']
        binary = primary / 'build/native_keyboard_voice_pair'
    signatures = {p: digest(ROOT / p) for p in paths}
    signatures["preparation"] = hashlib.sha256(json.dumps(preparation, sort_keys=True).encode()).hexdigest()
    key = hashlib.sha256(json.dumps(signatures, sort_keys=True).encode()).hexdigest()[:12]
    directory = ROOT / "build/next_detection" / ("integrated-voice-" + key)
    directory.mkdir(parents=True, exist_ok=True)
    if args.single_notes:
        fixture = directory / "input"
        fixture.mkdir(exist_ok=True)
        fields = list(subset[0])
        with (fixture / "manifest.tsv").open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            for row in subset:
                writer.writerow({**row, "path": source_reference(base, row["path"], fixture)})
    else:
        fixture = base
    (directory / "checkpoint.json").write_text(json.dumps(dict(signatures=signatures, selection=selected, complete=False), indent=2) + "\n")
    output = directory / "frames.tsv"
    subprocess.run([str(binary), str(fixture), str(output)], check=True, timeout=7200)
    with output.open() as stream:
        frames = list(csv.DictReader(stream, delimiter="\t"))
    metrics, ends = {}, {}
    for row in frames:
        sample = selected[row["sample_id"]]
        end = int(row["end_sample"])
        hop = int(int(row["rate"]) * .05 + .5)
        assert end == ends.get(row["sample_id"], 0) + hop
        ends[row["sample_id"]] = end
        assert row["other_difference"] == "" and row["bpm_changed"] == "0" and row["existing_voice_changed"] == "0"
        assert not row["all_lost"], "A visible pitch was lost from every row"
        before, after = ({int(value) for value in row[key].split(",") if value} for key in ("voice_before", "voice_after"))
        assert after <= before, "Suppression added a Voice pitch"
        removed = before - after
        correct = sample["midi"] if sample["family"] == "vocals" else None
        cohort = sample["family"] + "-" + sample["cohort"]
        count = metrics.setdefault(cohort, dict(frames=0, correct_losses=0, wrong_removed=0, unscored_removals=0))
        count["frames"] += 1
        valid = sample.get("valid_end_seconds") is None or round(end / int(row["rate"]), 3) in sample["valid_end_seconds"]
        count["correct_losses"] += valid and correct in removed
        if valid and not sample.get("incomplete_pitch_labels"):
            count["wrong_removed"] += len(removed - {correct})
        count["unscored_removals"] += len(removed) if not valid else (len(removed - {correct}) if sample.get("incomplete_pitch_labels") else 0)
    assert set(ends) == set(selected)
    import wave
    for sample in selected:
        audio_path = ROOT / selected[sample]["original_audio"] if args.single_notes else fixture / "audio" / (sample + ".wav")
        with wave.open(str(audio_path), "rb") as audio:
            hop = int(audio.getframerate() * .05 + .5)
            assert ends[sample] == audio.getnframes() // hop * hop
    passed = not any(row["correct_losses"] or row["unscored_removals"] for row in metrics.values())
    if not args.single_notes:
        passed &= any(row["wrong_removed"] for name, row in metrics.items() if "heldout" in name)
    assert all(digest(ROOT / p) == expected for p, expected in signatures.items() if p != "preparation")
    for sample in selected.values():
        assert digest(ROOT / sample["original_audio"]) == sample["audio_sha256"]
    report = dict(signatures=signatures, selection=selected, passed=bool(passed), frames_sha256=digest(output), metrics=metrics,
                  frames=len(frames), scope="Paired current-source native engines; exact unrelated outputs/BPM preservation, no any-row pitch losses or surviving Voice-cell modifications; piano and singer-disjoint voice cohorts")
    (directory / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))
    print(directory.relative_to(ROOT) / "report.json")
    assert passed, "Integrated native Voice preservation/gain gate failed; report retained"


if __name__ == "__main__":
    main()
