#!/usr/bin/env python3
import json
import os
import sys
import wave


AUDIO_EXTENSIONS = (".wav", ".wave")
GUITARSET_CHILD_NAMES = (
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
FALSE_VALUES = ("0", "false", "FALSE", "no", "NO")


def truthy(name, fallback=False):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    return value not in FALSE_VALUES


def positive_int_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = int(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0 else fallback


def join_path(lhs, rhs):
    return os.path.join(lhs, rhs)


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_GUITARSET_ROOT") or os.environ.get("GUITARSET_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in GUITARSET_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0/0.00/0"
    return f"{label} min/avg/max {min(values)}/{sum(values) / len(values):.2f}/{max(values)}"


def lower_name(path):
    return os.path.basename(path).lower()


def is_audio_file(path):
    return lower_name(path).endswith(AUDIO_EXTENSIONS)


def collect_files(root, max_depth):
    collected = []
    root = os.path.abspath(root)
    for current, dirs, files in os.walk(root):
        rel = os.path.relpath(current, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > max_depth:
            dirs[:] = []
            continue
        for filename in files:
            collected.append(join_path(current, filename))
    return collected


def normalized_excerpt_id(path):
    name = os.path.splitext(os.path.basename(path))[0]
    for suffix in STRIP_SUFFIXES:
        if name.lower().endswith(suffix):
            return name[: -len(suffix)]
    return name


def collect_annotations(root):
    annotations = {}
    candidate_roots = [root]
    for child in ANNOTATION_DIR_NAMES:
        candidate = join_path(root, child)
        if os.path.isdir(candidate):
            candidate_roots.append(candidate)

    seen = set()
    for candidate_root in candidate_roots:
        if not os.path.isdir(candidate_root):
            continue
        for path in collect_files(candidate_root, 5):
            if not lower_name(path).endswith(".jams"):
                continue
            absolute = os.path.abspath(path)
            if absolute in seen:
                continue
            seen.add(absolute)
            annotations[normalized_excerpt_id(path)] = path
    return annotations


def read_audio_summary(path):
    with wave.open(path, "rb") as wav:
        return {
            "channels": wav.getnchannels(),
            "sample_rate": wav.getframerate(),
            "frames": wav.getnframes(),
            "duration": wav.getnframes() / float(max(1, wav.getframerate())),
        }


def collect_audio(root):
    audio = {}
    failures = []
    for path in collect_files(root, 5):
        if not is_audio_file(path):
            continue
        excerpt_id = normalized_excerpt_id(path)
        try:
            summary = read_audio_summary(path)
        except (wave.Error, EOFError, OSError) as exc:
            failures.append(f"{path}: {exc}")
            continue
        audio.setdefault(excerpt_id, []).append({"path": path, **summary})
    return audio, failures


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


def inspect_jams(path):
    with open(path, "r", encoding="utf-8") as jams_file:
        data = json.load(jams_file)

    annotations = data.get("annotations", [])
    if not isinstance(annotations, list):
        raise ValueError("annotations must be a list")

    note_annotations = 0
    pitch_annotations = 0
    chord_annotations = 0
    note_events = 0
    pitch_classes = set()
    fretted_events = 0

    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue
        namespace = namespace_name(annotation)
        rows = annotation.get("data", [])
        if not isinstance(rows, list):
            rows = []

        if namespace in ("note_midi", "midi_note"):
            note_annotations += 1
            for row in rows:
                if not isinstance(row, dict):
                    continue
                midi = value_to_midi(row.get("value"))
                if midi is not None:
                    note_events += 1
                    pitch_classes.add(midi % 12)
                value = row.get("value")
                if isinstance(value, dict) and isinstance(value.get("fret"), (int, float)):
                    fretted_events += 1
        elif namespace == "pitch_contour":
            pitch_annotations += 1
        elif namespace.startswith("chord"):
            chord_annotations += 1

    return {
        "note_annotations": note_annotations,
        "pitch_annotations": pitch_annotations,
        "chord_annotations": chord_annotations,
        "note_events": note_events,
        "pitch_classes": len(pitch_classes),
        "fretted_events": fretted_events,
    }


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_guitarset_dataset: set MUSIC_ANALYZER_GUITARSET_ROOT, GUITARSET_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_guitarset_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_excerpts = positive_int_env("MUSIC_ANALYZER_GUITARSET_REQUIRED_EXCERPTS", 20)
    min_note_annotations = positive_int_env("MUSIC_ANALYZER_GUITARSET_MIN_NOTE_ANNOTATIONS", 6)
    min_chord_annotations = positive_int_env("MUSIC_ANALYZER_GUITARSET_MIN_CHORD_ANNOTATIONS", 2)
    min_note_events = positive_int_env("MUSIC_ANALYZER_GUITARSET_MIN_NOTE_EVENTS", 12)
    min_hex_channels = positive_int_env("MUSIC_ANALYZER_GUITARSET_MIN_HEX_CHANNELS", 6)
    require_hex_audio = truthy("MUSIC_ANALYZER_GUITARSET_REQUIRE_HEX_AUDIO", True)

    annotations = collect_annotations(root)
    audio, audio_failures = collect_audio(root)
    inspected = []
    failures = list(audio_failures[:10])

    for excerpt_id, jams_path in sorted(annotations.items()):
        try:
            jams = inspect_jams(jams_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            failures.append(f"{jams_path}: {exc}")
            continue

        audio_entries = audio.get(excerpt_id, [])
        hex_entries = [entry for entry in audio_entries if entry["channels"] >= min_hex_channels]
        complete_annotations = (
            jams["note_annotations"] >= min_note_annotations
            and jams["chord_annotations"] >= min_chord_annotations
            and jams["note_events"] >= min_note_events
        )
        complete_audio = bool(audio_entries) and (bool(hex_entries) or not require_hex_audio)
        inspected.append(
            {
                "id": excerpt_id,
                "jams": jams,
                "audio_entries": len(audio_entries),
                "hex_entries": len(hex_entries),
                "complete_annotations": complete_annotations,
                "complete_audio": complete_audio,
            }
        )

    complete = [item for item in inspected if item["complete_annotations"] and item["complete_audio"]]
    note_counts = [item["jams"]["note_events"] for item in complete]
    pitch_class_counts = [item["jams"]["pitch_classes"] for item in complete]
    hex_counts = [item["hex_entries"] for item in complete]

    print(
        "inspect_guitarset_dataset: "
        f"root={root} jams={len(annotations)} audio_excerpts={len(audio)} complete_excerpts={len(complete)} "
        f"require_hex_audio={int(require_hex_audio)} "
        f"{range_summary(note_counts, 'note events')} "
        f"{range_summary(pitch_class_counts, 'pitch classes')} "
        f"{range_summary(hex_counts, 'hex audio files')}"
    )

    if len(complete) < required_excerpts:
        print(
            f"inspect_guitarset_dataset: expected at least {required_excerpts} excerpts with "
            f"{min_note_annotations}+ note_midi annotations, {min_chord_annotations}+ chord annotations, "
            f"{min_note_events}+ note events, and "
            f"{min_hex_channels}+-channel hex audio; got {len(complete)}",
            file=sys.stderr,
        )
        for failure in failures[:10]:
            print(f"inspect_guitarset_dataset: {failure}", file=sys.stderr)
        return 1

    print(
        "inspect_guitarset_dataset: local GuitarSet excerpts are present; "
        "use this as a guitar/fretboard real-audio add-on, not as a replacement for URMP mixed-source coverage"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
