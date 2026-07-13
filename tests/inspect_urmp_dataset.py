#!/usr/bin/env python3
import os
import sys
import math


FIXTURE_MARKER = ".music_analyzer_generated_urmp_fixture"
AUDIO_EXTENSIONS = (".wav", ".flac")
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


def is_audio_file(name):
    return name.endswith(AUDIO_EXTENSIONS)


def midi_from_frequency(freq):
    return int(round(69.0 + 12.0 * math.log2(freq / 440.0)))


def resolve_max_windows_per_piece():
    return resolve_positive_int_env("MUSIC_ANALYZER_URMP_MAX_WINDOWS_PER_PIECE", 12)


def resolve_positive_int_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = int(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0 else fallback


class RangeStats:
    def __init__(self):
        self.count = 0
        self.total = 0
        self.minimum = 0
        self.maximum = 0

    def add(self, value):
        self.count += 1
        self.total += value
        if self.count == 1:
            self.minimum = value
            self.maximum = value
        else:
            self.minimum = min(self.minimum, value)
            self.maximum = max(self.maximum, value)

    def summary(self, label):
        if self.count == 0:
            return f"{label} min/avg/max 0/0.00/0"
        return (
            f"{label} min/avg/max {self.minimum}/"
            f"{self.total / self.count:.2f}/{self.maximum}"
        )


def read_notes(path):
    notes = []
    try:
        with open(path, "r", encoding="utf-8") as notes_file:
            for line in notes_file:
                fields = line.split()
                if len(fields) < 3:
                    continue
                try:
                    onset = float(fields[0])
                    frequency = float(fields[1])
                    duration = float(fields[2])
                except ValueError:
                    continue
                if frequency <= 0.0 or duration <= 0.0:
                    continue
                midi = midi_from_frequency(frequency)
                if 21 <= midi <= 108:
                    notes.append((onset, duration, midi))
    except OSError:
        return []
    return notes


def active_note_at(notes, time):
    best = None
    best_margin = -1.0
    for onset, duration, midi in notes:
        edge = min(0.035, duration * 0.20)
        start = onset + edge
        end = onset + duration - edge
        if time < start or time > end:
            continue
        margin = min(time - onset, onset + duration - time)
        if margin > best_margin:
            best_margin = margin
            best = midi
    return best


def candidate_window_at(track_notes, time, min_active_tracks, min_pitch_classes):
    active = []
    pitch_classes = set()
    for notes in track_notes:
        midi = active_note_at(notes, time)
        if midi is None:
            continue
        active.append(midi)
        pitch_classes.add(midi % 12)
    if len(active) < min_active_tracks or len(pitch_classes) < min_pitch_classes:
        return None
    score = len(active) * 100 + len(pitch_classes) * 10
    return {
        "time": time,
        "score": score,
        "active_tracks": len(active),
        "pitch_classes": len(pitch_classes),
    }


def select_candidate_windows(track_notes, max_windows, min_active_tracks=2, min_pitch_classes=2):
    candidates = []
    for notes in track_notes:
        for onset, duration, _midi in notes:
            candidate = candidate_window_at(
                track_notes,
                onset + duration * 0.5,
                min_active_tracks,
                min_pitch_classes,
            )
            if candidate is not None:
                candidates.append(candidate)

    candidates.sort(key=lambda item: (-item["score"], item["time"]))
    selected = []
    for candidate in candidates:
        if any(abs(existing["time"] - candidate["time"]) < 0.20 for existing in selected):
            continue
        selected.append(candidate)
        if len(selected) >= max_windows:
            break
    selected.sort(key=lambda item: item["time"])
    return selected


def has_piece_markers(path):
    try:
        names = os.listdir(path)
    except OSError:
        return False
    return any(name.startswith("AuMix_") and is_audio_file(name) for name in names) and any(
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


def empty_piece_stats(matched_tracks=0):
    return {
        "matched_tracks": matched_tracks,
        "candidate_windows": 0,
        "active_tracks": [],
        "pitch_classes": [],
    }


def piece_stats(matched_tracks, candidate_windows):
    return {
        "matched_tracks": matched_tracks,
        "candidate_windows": len(candidate_windows),
        "active_tracks": [candidate["active_tracks"] for candidate in candidate_windows],
        "pitch_classes": [candidate["pitch_classes"] for candidate in candidate_windows],
    }


def inspect_piece(path, require_official, max_windows, min_active_tracks, min_pitch_classes):
    basename = os.path.basename(path)
    if require_official and not starts_with_any(basename, OFFICIAL_IDS):
        return False, "not an official URMP piece folder", empty_piece_stats()

    try:
        names = os.listdir(path)
    except OSError as exc:
        return False, f"cannot list directory: {exc}", empty_piece_stats()

    mixes = [name for name in names if name.startswith("AuMix_") and is_audio_file(name)]
    scores = [name for name in names if name.startswith("Sco_") and name.endswith(".mid")]
    sep_tracks = set()
    note_files = {}
    for name in names:
        if is_audio_file(name):
            track = parse_track_number(name, "AuSep_")
            if track is not None:
                sep_tracks.add(track)
        if name.endswith(".txt"):
            track = parse_track_number(name, "Notes_")
            if track is not None:
                note_files[track] = join_path(path, name)
    matched_tracks = sep_tracks & set(note_files.keys())

    if not mixes:
        return False, "missing AuMix audio", empty_piece_stats()
    if require_official and not scores:
        return False, "missing Sco_*.mid", empty_piece_stats()
    if len(matched_tracks) < 2:
        return False, "fewer than two matched AuSep/Notes tracks", empty_piece_stats(len(matched_tracks))

    track_notes = []
    for track in sorted(matched_tracks):
        notes = read_notes(note_files[track])
        if notes:
            track_notes.append(notes)
    if len(track_notes) < 2:
        return False, "fewer than two matched tracks with readable note annotations", empty_piece_stats(len(track_notes))

    candidate_windows = select_candidate_windows(
        track_notes, max_windows, min_active_tracks, min_pitch_classes
    )
    if not candidate_windows:
        return (
            False,
            f"no overlapping window with {min_active_tracks}+ active tracks and "
            f"{min_pitch_classes}+ pitch classes",
            empty_piece_stats(len(track_notes)),
        )
    return (
        True,
        f"{len(track_notes)} matched tracks, {len(candidate_windows)} candidate windows",
        piece_stats(len(track_notes), candidate_windows),
    )


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
    max_windows = resolve_max_windows_per_piece()
    min_active_tracks = resolve_positive_int_env("MUSIC_ANALYZER_URMP_MIN_ACTIVE_TRACKS_PER_WINDOW", 2)
    min_pitch_classes = resolve_positive_int_env("MUSIC_ANALYZER_URMP_MIN_PITCH_CLASSES_PER_WINDOW", 2)
    required = resolve_positive_int_env("MUSIC_ANALYZER_URMP_REQUIRED_PIECES", 20)
    required_windows = resolve_positive_int_env(
        "MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS", min(required * 4, max_windows * required)
    )
    pieces = collect_piece_dirs(root)
    ok_count = 0
    official_count = 0
    candidate_windows = 0
    matched_track_stats = RangeStats()
    active_track_stats = RangeStats()
    pitch_class_stats = RangeStats()
    failures = []
    for piece in pieces:
        if starts_with_any(os.path.basename(piece), OFFICIAL_IDS):
            official_count += 1
        ok, detail, stats = inspect_piece(
            piece,
            require_official,
            max_windows,
            min_active_tracks,
            min_pitch_classes,
        )
        if ok:
            ok_count += 1
            candidate_windows += stats["candidate_windows"]
            matched_track_stats.add(stats["matched_tracks"])
            for value in stats["active_tracks"]:
                active_track_stats.add(value)
            for value in stats["pitch_classes"]:
                pitch_class_stats.add(value)
        elif len(failures) < 8:
            failures.append((os.path.basename(piece), detail))

    print(
        "inspect_urmp_dataset: "
        f"root={root} discovered={len(pieces)} official={official_count} complete={ok_count} "
        f"candidate_windows={candidate_windows} mode={'fixture' if allow_fixture else 'real'} "
        f"{matched_track_stats.summary('matched tracks')} "
        f"{active_track_stats.summary('candidate active tracks')} "
        f"{pitch_class_stats.summary('candidate pitch classes')}"
    )
    for name, detail in failures:
        print(f"inspect_urmp_dataset: skip {name}: {detail}", file=sys.stderr)

    if ok_count < required:
        print(
            f"inspect_urmp_dataset: expected at least {required} complete pieces, got {ok_count}",
            file=sys.stderr,
        )
        return 1
    if candidate_windows < required_windows:
        print(
            f"inspect_urmp_dataset: expected at least {required_windows} candidate windows, got {candidate_windows}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
