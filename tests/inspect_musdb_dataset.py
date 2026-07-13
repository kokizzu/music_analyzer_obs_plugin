#!/usr/bin/env python3
import os
import sys
import wave


EXPECTED_STEMS = ("mixture", "drums", "bass", "other", "vocals")
AUDIO_EXTENSIONS = (".wav", ".wave")
MUSDB_CHILD_NAMES = (
    "MUSDB18-HQ",
    "musdb18-hq",
    "musdb18hq",
    "MUSDB18",
    "musdb18",
)


def positive_int_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = int(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0 else fallback


def positive_float_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = float(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0.0 else fallback


def join_path(lhs, rhs):
    return os.path.join(lhs, rhs)


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_MUSDB_ROOT") or os.environ.get("MUSDB_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in MUSDB_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def lower_name(path):
    return os.path.basename(path).lower()


def normalized_stem_name(path):
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    if stem == "accompaniment":
        return "other"
    return stem


def audio_summary(path):
    try:
        with wave.open(path, "rb") as audio:
            frames = audio.getnframes()
            sample_rate = audio.getframerate()
            return {
                "channels": audio.getnchannels(),
                "sample_rate": sample_rate,
                "frames": frames,
                "duration": frames / float(max(1, sample_rate)),
            }
    except (OSError, EOFError, wave.Error):
        return None


def candidate_track_dirs(root):
    candidates = []
    for split in ("train", "test"):
        split_dir = join_path(root, split)
        if not os.path.isdir(split_dir):
            continue
        for entry in sorted(os.scandir(split_dir), key=lambda item: item.name):
            if entry.is_dir():
                candidates.append(entry.path)
    if candidates:
        return candidates

    for entry in sorted(os.scandir(root), key=lambda item: item.name):
        if entry.is_dir():
            candidates.append(entry.path)
    return candidates


def inspect_track_dir(path, min_audio_seconds):
    stems = {}
    failures = []
    for entry in sorted(os.scandir(path), key=lambda item: item.name):
        if not entry.is_file() or not lower_name(entry.path).endswith(AUDIO_EXTENSIONS):
            continue
        stem = normalized_stem_name(entry.path)
        if stem not in EXPECTED_STEMS:
            continue
        summary = audio_summary(entry.path)
        if not summary:
            failures.append(f"{entry.path}: unreadable WAV")
            continue
        stems[stem] = summary

    missing = [stem for stem in EXPECTED_STEMS if stem not in stems]
    short = [stem for stem, summary in stems.items() if summary["duration"] < min_audio_seconds]
    durations = [summary["duration"] for summary in stems.values()]
    channels = [summary["channels"] for summary in stems.values()]
    sample_rates = {summary["sample_rate"] for summary in stems.values()}

    return {
        "path": path,
        "complete": not missing and not short,
        "missing": missing,
        "short": short,
        "stem_count": len(stems),
        "durations": durations,
        "channels": channels,
        "sample_rates": sample_rates,
        "failures": failures,
    }


def range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0/0.00/0"
    return f"{label} min/avg/max {min(values)}/{sum(values) / len(values):.2f}/{max(values)}"


def float_range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0.00/0.00/0.00"
    return f"{label} min/avg/max {min(values):.2f}/{sum(values) / len(values):.2f}/{max(values):.2f}"


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_musdb_dataset: set MUSIC_ANALYZER_MUSDB_ROOT, MUSDB_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_musdb_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_tracks = positive_int_env("MUSIC_ANALYZER_MUSDB_REQUIRED_TRACKS", 20)
    min_audio_seconds = positive_float_env("MUSIC_ANALYZER_MUSDB_MIN_AUDIO_SECONDS", 1.0)

    inspected = [inspect_track_dir(path, min_audio_seconds) for path in candidate_track_dirs(root)]
    complete = [track for track in inspected if track["complete"]]
    stem_counts = [track["stem_count"] for track in complete]
    durations = [duration for track in complete for duration in track["durations"]]
    channels = [channel for track in complete for channel in track["channels"]]
    sample_rate_counts = [len(track["sample_rates"]) for track in complete]

    print(
        "inspect_musdb_dataset: "
        f"root={root} discovered_tracks={len(inspected)} complete_tracks={len(complete)} "
        f"expected_stems={','.join(EXPECTED_STEMS)} "
        f"{range_summary(stem_counts, 'stems per track')} "
        f"{range_summary(channels, 'channels')} "
        f"{range_summary(sample_rate_counts, 'sample-rate variants per track')} "
        f"{float_range_summary(durations, 'audio seconds per stem')}"
    )

    if len(complete) < required_tracks:
        print(
            f"inspect_musdb_dataset: expected at least {required_tracks} complete tracks with "
            f"{','.join(EXPECTED_STEMS)} WAV stems of at least {min_audio_seconds:.2f}s; "
            f"got {len(complete)}",
            file=sys.stderr,
        )
        for track in inspected[:10]:
            if track["complete"]:
                continue
            missing = ",".join(track["missing"]) if track["missing"] else "-"
            short = ",".join(track["short"]) if track["short"] else "-"
            print(
                f"inspect_musdb_dataset: incomplete {track['path']} missing={missing} short={short}",
                file=sys.stderr,
            )
            for failure in track["failures"][:3]:
                print(f"inspect_musdb_dataset: {failure}", file=sys.stderr)
        return 1

    print(
        "inspect_musdb_dataset: note this is a weak-truth stem preflight; "
        "MUSDB18 has 20+ same-song stems but no per-note MIDI truth, so it does not replace "
        "the URMP note/chord gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
