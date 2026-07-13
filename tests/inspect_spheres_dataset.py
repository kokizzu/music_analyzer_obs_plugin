#!/usr/bin/env python3
import os
import sys
import wave


AUDIO_EXTENSIONS = (".wav", ".wave", ".flac", ".aiff", ".aif", ".mp3", ".m4a")
SPHERES_CHILD_NAMES = (
    "TheSpheresDataset",
    "The_Spheres_Dataset",
    "Spheres",
    "spheres",
    "TheSpheres",
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
    root = os.environ.get("MUSIC_ANALYZER_SPHERES_ROOT") or os.environ.get("SPHERES_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in SPHERES_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def lower_name(path):
    return os.path.basename(path).lower()


def is_audio_file(path):
    return lower_name(path).endswith(AUDIO_EXTENSIONS)


def is_mix_like_folder(path):
    name = lower_name(path)
    return "stereo" in name or "mix" in name


def range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0/0.00/0"
    return f"{label} min/avg/max {min(values)}/{sum(values) / len(values):.2f}/{max(values)}"


def float_range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0.00/0.00/0.00"
    return f"{label} min/avg/max {min(values):.2f}/{sum(values) / len(values):.2f}/{max(values):.2f}"


def audio_duration_seconds(path):
    lowered = lower_name(path)
    if not lowered.endswith((".wav", ".wave")):
        return 0.0
    try:
        with wave.open(path, "rb") as audio:
            return audio.getnframes() / float(max(1, audio.getframerate()))
    except (OSError, EOFError, wave.Error):
        return 0.0


def audio_files_below(root, max_depth):
    root = os.path.abspath(root)
    files = []
    for current, dirs, filenames in os.walk(root):
        rel = os.path.relpath(current, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > max_depth:
            dirs[:] = []
            continue
        for filename in filenames:
            path = join_path(current, filename)
            if is_audio_file(path):
                files.append(path)
    return files


def candidate_piece_dirs(root, max_depth=3):
    root = os.path.abspath(root)
    candidates = []
    for current, dirs, _files in os.walk(root):
        rel = os.path.relpath(current, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > max_depth:
            dirs[:] = []
            continue
        if dirs:
            candidates.append(current)
    return candidates


def inspect_piece_dir(
    path,
    min_audio_files_per_folder,
    min_audio_seconds,
    required_reconstructable_folders,
    required_source_folders,
):
    reconstructable_counts = []
    source_folder_count = 0
    mix_folder_count = 0
    folder_durations = []
    for entry in sorted(os.scandir(path), key=lambda item: item.name):
        if not entry.is_dir():
            continue
        audio_files = audio_files_below(entry.path, max_depth=2)
        if len(audio_files) < min_audio_files_per_folder:
            continue
        duration = max((audio_duration_seconds(audio_file) for audio_file in audio_files), default=0.0)
        if duration < min_audio_seconds:
            continue
        reconstructable_counts.append(len(audio_files))
        folder_durations.append(duration)
        if is_mix_like_folder(entry.path):
            mix_folder_count += 1
        else:
            source_folder_count += 1

    return {
        "path": path,
        "reconstructable_folders": len(reconstructable_counts),
        "source_folders": source_folder_count,
        "mix_folders": mix_folder_count,
        "audio_counts": reconstructable_counts,
        "folder_durations": folder_durations,
        "complete": (
            mix_folder_count >= 1
            and source_folder_count >= required_source_folders
            and len(reconstructable_counts) >= required_reconstructable_folders
        ),
    }


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_spheres_dataset: set MUSIC_ANALYZER_SPHERES_ROOT, SPHERES_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_spheres_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_pieces = positive_int_env("MUSIC_ANALYZER_SPHERES_REQUIRED_PIECES", 2)
    required_reconstructable_folders = positive_int_env(
        "MUSIC_ANALYZER_SPHERES_REQUIRED_RECONSTRUCTABLE_FOLDERS", 2
    )
    required_source_folders = positive_int_env("MUSIC_ANALYZER_SPHERES_REQUIRED_SOURCE_FOLDERS", 1)
    min_audio_files_per_folder = positive_int_env(
        "MUSIC_ANALYZER_SPHERES_MIN_AUDIO_FILES_PER_FOLDER", 2
    )
    min_audio_seconds = positive_float_env("MUSIC_ANALYZER_SPHERES_MIN_AUDIO_SECONDS", 0.5)

    inspected = [
        inspect_piece_dir(
            path,
            min_audio_files_per_folder,
            min_audio_seconds,
            required_reconstructable_folders,
            required_source_folders,
        )
        for path in candidate_piece_dirs(root)
    ]
    complete = [piece for piece in inspected if piece["complete"]]
    reconstructable_folder_counts = [piece["reconstructable_folders"] for piece in complete]
    source_folder_counts = [piece["source_folders"] for piece in complete]
    mix_folder_counts = [piece["mix_folders"] for piece in complete]
    audio_counts = [
        audio_count
        for piece in complete
        for audio_count in piece["audio_counts"]
    ]
    durations = [
        duration
        for piece in complete
        for duration in piece["folder_durations"]
    ]

    print(
        "inspect_spheres_dataset: "
        f"root={root} discovered_piece_candidates={len(inspected)} complete_pieces={len(complete)} "
        f"{range_summary(reconstructable_folder_counts, 'reconstructable folders')} "
        f"{range_summary(source_folder_counts, 'source folders')} "
        f"{range_summary(mix_folder_counts, 'mix folders')} "
        f"{range_summary(audio_counts, 'audio files per folder')} "
        f"{float_range_summary(durations, 'audio seconds per folder')}"
    )

    if len(complete) < required_pieces:
        print(
            f"inspect_spheres_dataset: expected at least {required_pieces} complete pieces "
            f"with a readable mix/stereo folder, {required_source_folders}+ source folders, "
            f"and {required_reconstructable_folders}+ reconstructable folders containing "
            f"{min_audio_files_per_folder}+ audio files of at least {min_audio_seconds:.2f}s",
            file=sys.stderr,
        )
        return 1

    print(
        "inspect_spheres_dataset: note this is a weak-truth real-stem preflight; "
        "The Spheres Dataset has two full works and no full per-note MIDI truth, "
        "so it does not replace the URMP note/chord gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
