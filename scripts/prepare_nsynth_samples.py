#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path


MODE_BY_FAMILY = {
    "bass": "bass",
    "guitar": "guitar",
    "keyboard": "piano",
    "organ": "piano",
    "mallet": "piano",
    "vocal": "vocals",
    "brass": "other",
    "flute": "other",
    "reed": "other",
    "string": "other",
    "synth_lead": "other",
}

MIDI_RANGE_BY_MODE = {
    "bass": (28, 67),
    "guitar": (40, 88),
    "piano": (24, 95),
    "vocals": (40, 84),
    "other": (36, 84),
}

UNCLEAN_ONE_NOTE_QUALITIES = {"multiphonic", "tempo-synced"}

ONE_NOTE_EXCLUSIONS = {
    "brass_acoustic_046-084-025":
        "annotated C6 is dominated by unrelated upper partials in the analysis window",
    "brass_acoustic_046-084-075":
        "annotated C6 is dominated by unrelated upper partials in the analysis window",
    "brass_acoustic_046-084-100":
        "annotated C6 is dominated by unrelated upper partials in the analysis window",
    "keyboard_acoustic_004-087-025":
        "annotated D#6 is dominated by lower resonant components in the analysis window",
    "organ_electronic_104-074-075":
        "annotated D5 is dominated by a louder mixture-stop fifth in the analysis window",
    "organ_electronic_104-077-100":
        "annotated F5 is dominated by a louder mixture-stop fifth in the analysis window",
    "organ_electronic_104-078-050":
        "annotated F#5 is dominated by a louder mixture-stop fifth in the analysis window",
}


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def source_allowed(source, allow_synthetic):
    if allow_synthetic:
        return True
    return source in ("acoustic", "electronic")


def midi_allowed(analyzer_family, midi):
    low, high = MIDI_RANGE_BY_MODE[analyzer_family]
    return low <= midi <= high


def qualities_allowed(qualities, allow_unclean):
    if allow_unclean:
        return True
    return not (set(qualities) & UNCLEAN_ONE_NOTE_QUALITIES)


def main():
    parser = argparse.ArgumentParser(description="Prepare real NSynth note sample manifest.")
    parser.add_argument("--nsynth-root", default=os.environ.get("NSYNTH_SAMPLE_ROOT", "build/real_sample_sources/nsynth-test"))
    parser.add_argument("--output", default=os.environ.get("REAL_NOTE_SAMPLE_DIR", "build/real_note_samples"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("REAL_NOTE_SAMPLE_LIMIT", "0")))
    parser.add_argument("--allow-synthetic", action="store_true",
                        default=os.environ.get("REAL_NOTE_SAMPLE_ALLOW_SYNTHETIC", "0") == "1")
    parser.add_argument("--allow-unclean-qualities", action="store_true",
                        default=os.environ.get("REAL_NOTE_SAMPLE_ALLOW_UNCLEAN_QUALITIES", "0") == "1")
    args = parser.parse_args()

    root = Path(args.nsynth_root)
    metadata_path = root / "examples.json"
    audio_dir = root / "audio"
    if not metadata_path.is_file():
        raise SystemExit(f"prepare_nsynth_samples: missing {metadata_path}")
    if not audio_dir.is_dir():
        raise SystemExit(f"prepare_nsynth_samples: missing {audio_dir}")

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    rows = []
    counts = {}
    skipped = {}

    def skip(reason):
        skipped[reason] = skipped.get(reason, 0) + 1

    for sample_id, item in sorted(metadata.items()):
        if sample_id in ONE_NOTE_EXCLUSIONS:
            skip("unstable_pitch_reference")
            continue

        family = str(item.get("instrument_family_str", "")).strip()
        source = str(item.get("instrument_source_str", "")).strip()
        analyzer_family = MODE_BY_FAMILY.get(family)
        if not analyzer_family or not source_allowed(source, args.allow_synthetic):
            skip("source_or_family")
            continue

        try:
            midi = int(item.get("pitch"))
        except (TypeError, ValueError):
            skip("bad_pitch")
            continue

        if not midi_allowed(analyzer_family, midi):
            skip("outside_range")
            continue

        qualities = item.get("qualities_str", [])
        if not isinstance(qualities, list):
            qualities = []
        qualities = [str(quality) for quality in qualities]
        if not qualities_allowed(qualities, args.allow_unclean_qualities):
            skip("unclean_quality")
            continue

        wav_path = audio_dir / f"{sample_id}.wav"
        if not wav_path.is_file():
            skip("missing_audio")
            continue

        rel_path = os.path.relpath(wav_path, args.output)
        rows.append((
            sample_id,
            analyzer_family,
            family,
            source,
            str(midi),
            note_name(midi),
            rel_path,
            ",".join(qualities),
        ))
        counts[analyzer_family] = counts.get(analyzer_family, 0) + 1
        if args.limit > 0 and len(rows) >= args.limit:
            break

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "manifest.tsv"
    with manifest.open("w", encoding="utf-8") as file:
        file.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities\n")
        for row in rows:
            file.write("\t".join(row) + "\n")

    count_text = " ".join(f"{name}={counts[name]}" for name in sorted(counts))
    skipped_text = " ".join(f"{name}={skipped[name]}" for name in sorted(skipped))
    print(
        f"prepare_nsynth_samples: wrote {len(rows)} rows to {manifest} "
        f"({count_text}, skipped {skipped_text})"
    )
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
