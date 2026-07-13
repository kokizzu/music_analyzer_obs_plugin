#!/usr/bin/env python3
import os
import sys


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


def inspect_piece_dir(path, min_audio_files_per_folder, required_reconstructable_folders):
    reconstructable_counts = []
    has_mix_folder = False
    for entry in sorted(os.scandir(path), key=lambda item: item.name):
        if not entry.is_dir():
            continue
        audio_files = audio_files_below(entry.path, max_depth=2)
        if len(audio_files) < min_audio_files_per_folder:
            continue
        reconstructable_counts.append(len(audio_files))
        if is_mix_like_folder(entry.path):
            has_mix_folder = True

    return {
        "path": path,
        "reconstructable_folders": len(reconstructable_counts),
        "audio_counts": reconstructable_counts,
        "complete": has_mix_folder and len(reconstructable_counts) >= required_reconstructable_folders,
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
    min_audio_files_per_folder = positive_int_env(
        "MUSIC_ANALYZER_SPHERES_MIN_AUDIO_FILES_PER_FOLDER", 2
    )

    inspected = [
        inspect_piece_dir(path, min_audio_files_per_folder, required_reconstructable_folders)
        for path in candidate_piece_dirs(root)
    ]
    complete = [piece for piece in inspected if piece["complete"]]
    reconstructable_folder_counts = [piece["reconstructable_folders"] for piece in complete]
    audio_counts = [
        audio_count
        for piece in complete
        for audio_count in piece["audio_counts"]
    ]

    print(
        "inspect_spheres_dataset: "
        f"root={root} discovered_piece_candidates={len(inspected)} complete_pieces={len(complete)} "
        f"{range_summary(reconstructable_folder_counts, 'reconstructable folders')} "
        f"{range_summary(audio_counts, 'audio files per folder')}"
    )

    if len(complete) < required_pieces:
        print(
            f"inspect_spheres_dataset: expected at least {required_pieces} complete pieces "
            f"with a mix/stereo folder and {required_reconstructable_folders}+ reconstructable "
            f"folders containing {min_audio_files_per_folder}+ source audio files",
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
