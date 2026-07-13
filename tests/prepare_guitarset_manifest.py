#!/usr/bin/env python3
import json
import os
import sys
import wave


AUDIO_EXTENSIONS = (".wav", ".wave")
CHILD_NAMES = (
    "GuitarSet",
    "guitarset",
    "GuitarSet-1.1.0",
    "guitarset-1.1.0",
)
ANNOTATION_DIR_NAMES = ("annotation", "annotations")
STRIP_SUFFIXES = (
    "_hex_cln",
    "_hex",
    "_mic",
    "_mono-mic",
    "_mono-pickup_mix",
    "_pickup_mix",
    "_mix",
)


def join_path(lhs, rhs):
    return os.path.join(lhs, rhs)


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_GUITARSET_ROOT") or os.environ.get("GUITARSET_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return ""

    for child in CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def lower_name(path):
    return os.path.basename(path).lower()


def normalized_excerpt_id(path):
    name = os.path.splitext(os.path.basename(path))[0]
    lowered = name.lower()
    for suffix in STRIP_SUFFIXES:
        if lowered.endswith(suffix):
            return name[: -len(suffix)]
    return name


def collect_files(root, max_depth):
    root = os.path.abspath(root)
    collected = []
    for current, dirs, files in os.walk(root):
        rel = os.path.relpath(current, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > max_depth:
            dirs[:] = []
            continue
        for filename in files:
            collected.append(join_path(current, filename))
    return collected


def collect_annotations(root):
    annotations = {}
    candidate_roots = [root]
    for child in ANNOTATION_DIR_NAMES:
        candidate = join_path(root, child)
        if os.path.isdir(candidate):
            candidate_roots.append(candidate)

    for candidate_root in candidate_roots:
        for path in collect_files(candidate_root, 5):
            if lower_name(path).endswith(".jams"):
                annotations.setdefault(normalized_excerpt_id(path), path)
    return annotations


def audio_channels(path):
    try:
        with wave.open(path, "rb") as wav:
            return wav.getnchannels()
    except (OSError, EOFError, wave.Error):
        return 0


def collect_audio(root):
    audio = {}
    for path in collect_files(root, 5):
        if not lower_name(path).endswith(AUDIO_EXTENSIONS):
            continue
        channels = audio_channels(path)
        if channels <= 0:
            continue
        audio.setdefault(normalized_excerpt_id(path), []).append((path, channels))
    return audio


def audio_preference(entry):
    path, channels = entry
    lowered = lower_name(path)
    if "_hex_cln" in lowered:
        kind = 0
    elif "_hex" in lowered:
        kind = 1
    elif "_mic" in lowered:
        kind = 2
    else:
        kind = 3
    return (0 if channels >= 6 else 1, kind, path)


def selected_audio(entries):
    if not entries:
        return ""
    return sorted(entries, key=audio_preference)[0][0]


def namespace_name(annotation):
    return str(annotation.get("namespace", "")).lower().strip()


def value_to_midi(value):
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if isinstance(value, dict):
        for key in ("midi_note", "note", "pitch"):
            candidate = value.get(key)
            if isinstance(candidate, (int, float)):
                return int(round(candidate))
    return None


def parse_jams(path):
    with open(path, "r", encoding="utf-8") as jams_file:
        payload = json.load(jams_file)

    notes = []
    chords = []
    for annotation in payload.get("annotations", []):
        if not isinstance(annotation, dict):
            continue
        namespace = namespace_name(annotation)
        rows = annotation.get("data", [])
        if not isinstance(rows, list):
            continue

        if namespace in ("note_midi", "midi_note"):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                midi = value_to_midi(row.get("value"))
                if midi is None:
                    continue
                start = float(row.get("time", 0.0))
                duration = float(row.get("duration", 0.0))
                if duration <= 0.0:
                    continue
                notes.append((start, start + duration, midi))
        elif namespace.startswith("chord"):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                value = row.get("value")
                if not isinstance(value, str) or not value:
                    continue
                start = float(row.get("time", 0.0))
                duration = float(row.get("duration", 0.0))
                if duration <= 0.0:
                    continue
                chords.append((start, start + duration, value))
    return notes, chords


def write_manifest(root, output_path):
    annotations = collect_annotations(root)
    audio = collect_audio(root)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    written = 0
    with open(output_path, "w", encoding="utf-8") as output:
        output.write("# GuitarSet analyzer manifest v1\n")
        for excerpt_id, jams_path in sorted(annotations.items()):
            audio_path = selected_audio(audio.get(excerpt_id, []))
            if not audio_path:
                continue
            try:
                notes, chords = parse_jams(jams_path)
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                continue
            if not notes:
                continue
            output.write(f"AUDIO\t{excerpt_id}\t{audio_path}\n")
            for start, end, midi in notes:
                output.write(f"NOTE\t{excerpt_id}\t{start:.6f}\t{end:.6f}\t{midi}\n")
            for start, end, label in chords:
                output.write(f"CHORD\t{excerpt_id}\t{start:.6f}\t{end:.6f}\t{label}\n")
            written += 1
    return written


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_guitarset_manifest.py OUTPUT_PATH", file=sys.stderr)
        return 2

    root = resolve_root()
    if not root:
        print(
            "prepare_guitarset_manifest: set MUSIC_ANALYZER_GUITARSET_ROOT, GUITARSET_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"prepare_guitarset_manifest: `{root}` is not a directory", file=sys.stderr)
        return 1

    written = write_manifest(root, argv[1])
    print(f"prepare_guitarset_manifest: wrote {written} excerpts to {argv[1]}")
    return 0 if written > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
