#!/usr/bin/env python3
import os
import sys


AUDIO_EXTENSIONS = (".wav", ".wave")
ANNOTATION_EXTENSIONS = (".csv", ".txt")


def truthy(name):
    value = os.environ.get(name, "")
    return value and value not in ("0", "false", "FALSE")


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
    root = os.environ.get("MUSIC_ANALYZER_MEDLEYDB_ROOT") or os.environ.get("MEDLEYDB_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in (
        "MedleyDB",
        "medleydb",
        "MedleyDB_sample",
        "MedleyDB_2.0",
        "MedleyDB2",
    ):
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return dataset_root


def candidate_annotation_roots(audio_root):
    roots = []
    explicit = (
        os.environ.get("MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT")
        or os.environ.get("MEDLEYDB_ANNOTATIONS_PATH")
    )
    if explicit:
        roots.append(explicit)

    for base in (audio_root, os.environ.get("MEDLEYDB_PATH", "")):
        if not base:
            continue
        roots.extend(
            [
                join_path(base, "Annotations"),
                join_path(base, "annotations"),
                join_path(base, "medleydb/data/Annotations"),
                join_path(base, "data/Annotations"),
            ]
        )

    deduped = []
    seen = set()
    for root in roots:
        normalized = os.path.abspath(root)
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(root)
    return deduped


def lower_name(path):
    return os.path.basename(path).lower()


def is_audio_file(path):
    return lower_name(path).endswith(AUDIO_EXTENSIONS)


def is_annotation_file(path):
    return lower_name(path).endswith(ANNOTATION_EXTENSIONS)


def track_id_from_mix(name):
    lowered = name.lower()
    marker = "_mix."
    pos = lowered.rfind(marker)
    if pos < 0:
        return ""
    return name[:pos]


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


def collect_track_dirs(root):
    tracks = {}
    for path in collect_files(root, 5):
        name = os.path.basename(path)
        track_id = track_id_from_mix(name)
        if not track_id or not is_audio_file(path):
            continue
        track_dir = os.path.dirname(path)
        tracks[track_id] = {
            "track_id": track_id,
            "track_dir": track_dir,
            "mix": path,
            "stems": [],
        }

    for track in tracks.values():
        for path in collect_files(track["track_dir"], 3):
            name = lower_name(path)
            if not is_audio_file(path):
                continue
            if "_stem_" in name or "/stems/" in path.lower() or "_stems" in path.lower():
                track["stems"].append(path)

    return tracks


def annotation_track_id(path):
    name = os.path.basename(path)
    lowered = name.lower()
    if "melody" not in lowered:
        return ""
    for marker in ("_melody", ".melody"):
        pos = lowered.find(marker)
        if pos > 0:
            return name[:pos]
    return ""


def collect_melody_annotations(roots):
    annotations = {}
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in collect_files(root, 6):
            if not is_annotation_file(path):
                continue
            track_id = annotation_track_id(path)
            if track_id:
                annotations.setdefault(track_id, []).append(path)
    return annotations


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_medleydb_dataset: set MUSIC_ANALYZER_MEDLEYDB_ROOT, MEDLEYDB_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_medleydb_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_tracks = positive_int_env("MUSIC_ANALYZER_MEDLEYDB_REQUIRED_TRACKS", 20)
    required_melody_tracks = positive_int_env("MUSIC_ANALYZER_MEDLEYDB_REQUIRED_MELODY_TRACKS", 20)
    min_stems = positive_int_env("MUSIC_ANALYZER_MEDLEYDB_MIN_STEMS", 2)

    tracks = collect_track_dirs(root)
    annotation_roots = candidate_annotation_roots(root)
    annotations = collect_melody_annotations(annotation_roots)

    complete_tracks = [
        track for track in tracks.values() if track["mix"] and len(track["stems"]) >= min_stems
    ]
    melody_tracks = [
        track for track in complete_tracks if annotations.get(track["track_id"])
    ]

    print(
        "inspect_medleydb_dataset: "
        f"root={root} tracks={len(tracks)} complete_multitracks={len(complete_tracks)} "
        f"melody_annotated_multitracks={len(melody_tracks)} annotation_roots="
        f"{','.join(annotation_roots) if annotation_roots else '(none)'}"
    )

    if len(complete_tracks) < required_tracks:
        print(
            f"inspect_medleydb_dataset: expected at least {required_tracks} complete multitracks "
            f"with mix plus {min_stems}+ stems, got {len(complete_tracks)}",
            file=sys.stderr,
        )
        return 1

    if len(melody_tracks) < required_melody_tracks:
        print(
            f"inspect_medleydb_dataset: expected at least {required_melody_tracks} multitracks "
            f"with melody annotations, got {len(melody_tracks)}",
            file=sys.stderr,
        )
        if not truthy("MUSIC_ANALYZER_MEDLEYDB_ALLOW_NO_MELODY"):
            return 1

    print(
        "inspect_medleydb_dataset: note this is a partial real-stem preflight; "
        "MedleyDB melody F0 does not replace the full URMP per-source note/chord gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
