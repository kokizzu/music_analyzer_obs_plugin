#!/usr/bin/env python3
import os
import sys


FIXTURE_MARKER = ".music_analyzer_generated_urmp_fixture"
OFFICIAL_IDS = (
    "01_Jupiter",
    "02_Sonata",
    "03_Dance",
    "04_Allegro",
    "05_Entertainer",
    "06_Entertainer",
    "07_GString",
    "08_Spring",
    "09_Jesus",
    "10_March",
    "11_Maria",
    "12_Spring",
    "13_Hark",
    "14_Waltz",
    "15_Surprise",
    "16_Surprise",
    "17_Nocturne",
    "18_Nocturne",
    "19_Pavane",
    "20_Pavane",
    "21_Rejouissance",
    "22_Rejouissance",
    "23_Rejouissance",
    "24_Pirates",
    "25_Pirates",
    "26_King",
    "27_King",
    "28_Fugue",
    "29_Fugue",
    "30_Fugue",
    "31_Slavonic",
    "32_Fugue",
    "33_Elise",
    "34_Fugue",
    "35_Rondeau",
    "36_Rondeau",
    "37_Rondeau",
    "38_Jerusalem",
    "39_Jerusalem",
    "40_Miserere",
    "41_Miserere",
    "42_Arioso",
    "43_Chorale",
    "44_K515",
)


def truthy(name):
    value = os.environ.get(name, "")
    return value and value not in ("0", "false", "FALSE")


def join_path(lhs, rhs):
    return os.path.join(lhs, rhs)


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_URMP_ROOT")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in (
        "URMP",
        "urmp",
        "University_of_Rochester_Multi-Modal_Music_Performance",
    ):
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return dataset_root


def starts_with_any(text, prefixes):
    return any(text.startswith(prefix) for prefix in prefixes)


def parse_track_number(name, prefix):
    if not name.startswith(prefix):
        return None
    pos = len(prefix)
    digits = []
    while pos < len(name) and name[pos].isdigit():
        digits.append(name[pos])
        pos += 1
    return int("".join(digits)) if digits else None


def has_piece_markers(path):
    try:
        names = os.listdir(path)
    except OSError:
        return False
    return any(name.startswith("AuMix_") and name.endswith(".wav") for name in names) and any(
        name.startswith("Notes_") and name.endswith(".txt") for name in names
    )


def collect_piece_dirs(path, depth=4):
    if has_piece_markers(path):
        return [path]
    if depth <= 0:
        return []

    pieces = []
    try:
        names = sorted(os.listdir(path))
    except OSError:
        return pieces
    for name in names:
        child = join_path(path, name)
        if os.path.isdir(child):
            pieces.extend(collect_piece_dirs(child, depth - 1))
    return pieces


def inspect_piece(path, require_official):
    basename = os.path.basename(path)
    if require_official and not starts_with_any(basename, OFFICIAL_IDS):
        return False, "not an official URMP piece folder"

    try:
        names = os.listdir(path)
    except OSError as exc:
        return False, f"cannot list directory: {exc}"

    mixes = [name for name in names if name.startswith("AuMix_") and name.endswith(".wav")]
    scores = [name for name in names if name.startswith("Sco_") and name.endswith(".mid")]
    sep_tracks = {
        track
        for track in (parse_track_number(name, "AuSep_") for name in names if name.endswith(".wav"))
        if track is not None
    }
    note_tracks = {
        track
        for track in (parse_track_number(name, "Notes_") for name in names if name.endswith(".txt"))
        if track is not None
    }
    matched_tracks = sep_tracks & note_tracks

    if not mixes:
        return False, "missing AuMix_*.wav"
    if require_official and not scores:
        return False, "missing Sco_*.mid"
    if len(matched_tracks) < 2:
        return False, "fewer than two matched AuSep/Notes tracks"
    return True, f"{len(matched_tracks)} matched tracks"


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_urmp_dataset: set MUSIC_ANALYZER_URMP_ROOT or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_urmp_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    generated_fixture = os.path.exists(join_path(root, FIXTURE_MARKER))
    allow_fixture = truthy("MUSIC_ANALYZER_URMP_ALLOW_GENERATED_FIXTURE")
    if generated_fixture and not allow_fixture:
        print(
            f"inspect_urmp_dataset: `{root}` is a generated fixture, not the real URMP dataset",
            file=sys.stderr,
        )
        return 1

    require_official = not allow_fixture
    pieces = collect_piece_dirs(root)
    ok_count = 0
    official_count = 0
    failures = []
    for piece in pieces:
        if starts_with_any(os.path.basename(piece), OFFICIAL_IDS):
            official_count += 1
        ok, detail = inspect_piece(piece, require_official)
        if ok:
            ok_count += 1
        elif len(failures) < 8:
            failures.append((os.path.basename(piece), detail))

    print(
        "inspect_urmp_dataset: "
        f"root={root} discovered={len(pieces)} official={official_count} complete={ok_count} "
        f"mode={'fixture' if allow_fixture else 'real'}"
    )
    for name, detail in failures:
        print(f"inspect_urmp_dataset: skip {name}: {detail}", file=sys.stderr)

    required = 20
    if ok_count < required:
        print(
            f"inspect_urmp_dataset: expected at least {required} complete pieces, got {ok_count}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
