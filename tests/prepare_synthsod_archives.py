#!/usr/bin/env python3
import os
import shutil
import sys
import zipfile
from pathlib import Path

import inspect_synthsod_dataset


AUDIO_ZIP_ENVS = ("MUSIC_ANALYZER_SYNTHSOD_AUDIO_ZIP", "SYNTHSOD_AUDIO_ZIP")
SCORES_ZIP_ENVS = ("MUSIC_ANALYZER_SYNTHSOD_SCORES_ZIP", "SYNTHSOD_SCORES_ZIP")
ZIP_SUFFIX = ".zip"


def first_env_path(names):
    for name in names:
        value = os.environ.get(name, "")
        if value:
            return Path(value)
    return None


def validate_zip(path, label):
    if not path:
        raise ValueError(f"set {' or '.join(AUDIO_ZIP_ENVS if label == 'audio' else SCORES_ZIP_ENVS)}")
    if path.suffix.lower() != ZIP_SUFFIX:
        raise ValueError(f"{label} archive must be a .zip file: {path}")
    if not path.is_file():
        raise ValueError(f"{label} archive not found: {path}")


def safe_member_path(output_root, member_name):
    normalized = member_name.replace("\\", "/")
    if normalized.startswith("/"):
        raise ValueError(f"unsafe absolute archive member: {member_name}")

    parts = [part for part in normalized.split("/") if part]
    if not parts or any(part == ".." for part in parts):
        raise ValueError(f"unsafe archive member: {member_name}")
    if ":" in parts[0]:
        raise ValueError(f"unsafe archive member drive prefix: {member_name}")

    return output_root.joinpath(*parts)


def safe_extract(zip_path, output_root):
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = safe_member_path(output_root, member.filename)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, open(target, "wb") as destination:
                shutil.copyfileobj(source, destination)


def shallowest(paths, root):
    return sorted(paths, key=lambda path: (len(path.relative_to(root).parts), str(path)))[0] if paths else None


def named_dirs(root, names):
    matches = []
    wanted = set(names)
    if root.name in wanted:
        matches.append(root)
    for dirpath, dirnames, _filenames in os.walk(root):
        path = Path(dirpath)
        if path != root and path.name in wanted:
            matches.append(path)
        if len(path.relative_to(root).parts) >= 5:
            dirnames[:] = []
    return sorted(set(matches), key=lambda path: (len(path.relative_to(root).parts), str(path)))


def contains_audio(path):
    lower = path.name.lower()
    return lower.endswith(inspect_synthsod_dataset.AUDIO_EXTENSIONS)


def source_audio_count(piece_dir):
    return len(inspect_synthsod_dataset.source_audio_files(str(piece_dir)))


def looks_like_audio_root(path):
    pieces = inspect_synthsod_dataset.candidate_piece_dirs(str(path))
    return any(source_audio_count(Path(piece)) >= 2 for piece in pieces[:5])


def find_audio_root(output_root):
    for candidate in named_dirs(output_root, inspect_synthsod_dataset.SYNTHSOD_CHILD_NAMES):
        if looks_like_audio_root(candidate):
            return candidate

    possible_roots = {}
    source_names = {name.lower() for name in inspect_synthsod_dataset.SOURCE_DIR_NAMES}
    for dirpath, _dirnames, filenames in os.walk(output_root):
        path = Path(dirpath)
        if path.name.lower() not in source_names:
            continue
        if any(contains_audio(Path(name)) for name in filenames):
            possible_roots[path.parent.parent] = possible_roots.get(path.parent.parent, 0) + 1
    if possible_roots:
        return sorted(possible_roots, key=lambda item: (-possible_roots[item], str(item)))[0]
    return None


def find_scores_root(output_root):
    named = named_dirs(output_root, inspect_synthsod_dataset.SYNTHSOD_SCORE_CHILD_NAMES)
    for wanted_name in inspect_synthsod_dataset.SYNTHSOD_SCORE_CHILD_NAMES:
        for candidate in named:
            if candidate.name == wanted_name and inspect_synthsod_dataset.score_files(str(candidate)):
                return candidate

    score_counts = {}
    for dirpath, _dirnames, filenames in os.walk(output_root):
        count = sum(
            1
            for name in filenames
            if name.lower().endswith(inspect_synthsod_dataset.SCORE_EXTENSIONS)
        )
        if count:
            score_counts[Path(dirpath)] = count
    if score_counts:
        return sorted(score_counts, key=lambda item: (-score_counts[item], str(item)))[0]
    return shallowest(named, output_root)


def extract_archives(output_root, audio_zip, scores_zip):
    validate_zip(audio_zip, "audio")
    validate_zip(scores_zip, "scores")
    output_root.mkdir(parents=True, exist_ok=True)
    safe_extract(audio_zip, output_root)
    safe_extract(scores_zip, output_root)

    audio_root = find_audio_root(output_root)
    scores_root = find_scores_root(output_root)
    if not audio_root:
        raise ValueError("extracted archives did not contain a SynthSOD audio root with close-mic source audio")
    if not scores_root:
        raise ValueError("extracted archives did not contain SynthSOD aligned score text")
    return audio_root, scores_root


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_synthsod_archives.py OUT_DIR", file=sys.stderr)
        return 2

    output_root = Path(argv[1])
    audio_zip = first_env_path(AUDIO_ZIP_ENVS)
    scores_zip = first_env_path(SCORES_ZIP_ENVS)
    try:
        audio_root, scores_root = extract_archives(output_root, audio_zip, scores_zip)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"prepare_synthsod_archives: {exc}", file=sys.stderr)
        return 1

    print(f"prepare_synthsod_archives: audio_root={audio_root}")
    print(f"prepare_synthsod_archives: scores_root={scores_root}")
    print(
        "prepare_synthsod_archives: run "
        f"MUSIC_ANALYZER_SYNTHSOD_ROOT={audio_root} "
        f"MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT={scores_root} "
        "make inspect-real-synthsod"
    )
    print(
        "prepare_synthsod_archives: run "
        f"MUSIC_ANALYZER_SYNTHSOD_ROOT={audio_root} "
        f"MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT={scores_root} "
        "make test-real-synthsod-20"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
