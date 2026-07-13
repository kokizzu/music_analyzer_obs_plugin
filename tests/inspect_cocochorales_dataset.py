#!/usr/bin/env python3
import os
import sys

from inspect_choralsynth_dataset import (
    AUDIO_EXTENSIONS,
    MIDI_EXTENSIONS,
    audio_summary,
    float_range_summary,
    join_path,
    lower_name,
    midi_header_is_readable,
    positive_float_env,
    positive_int_env,
    range_summary,
    walk_files,
)


COCOCHORALES_CHILD_NAMES = (
    "CocoChorales",
    "cocochorales",
    "CocoChorales-v1",
    "coco_chorales",
    "ceg-cocochorales",
)
MIX_MARKERS = ("mix", "mixture", "master")
STEM_DIR_NAMES = ("stems", "stem", "sources", "source", "parts", "tracks")


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_COCOCHORALES_ROOT") or os.environ.get("COCOCHORALES_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in COCOCHORALES_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def is_audio(path):
    return lower_name(path).endswith(AUDIO_EXTENSIONS)


def is_midi(path):
    return lower_name(path).endswith(MIDI_EXTENSIONS)


def depth_from_root(root, path):
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    return 0 if rel == "." else rel.count(os.sep) + 1


def walk_dirs_limited(root, max_depth):
    root = os.path.abspath(root)
    for current, dirs, files in os.walk(root):
        depth = depth_from_root(root, current)
        if depth > max_depth:
            dirs[:] = []
            continue
        yield current, dirs, files


def find_audio_files(path):
    return sorted(item for item in walk_files(path) if is_audio(item))


def find_midi_files(path):
    return sorted(item for item in walk_files(path) if is_midi(item))


def find_score_midi(path):
    for name in ("score.mid", "score.midi", "all.mid", "all_src.mid", "midi.mid"):
        candidate = join_path(path, name)
        if os.path.isfile(candidate):
            return candidate
    midi_files = find_midi_files(path)
    return midi_files[0] if midi_files else ""


def find_mix_audio(audio_files):
    preferred = []
    for path in audio_files:
        name = lower_name(path)
        if any(marker in name for marker in MIX_MARKERS):
            preferred.append(path)
    return sorted(preferred)[0] if preferred else ""


def in_stem_dir(path):
    parts = [part.lower() for part in path.split(os.sep)]
    return any(part in STEM_DIR_NAMES for part in parts)


def find_stem_audio(path, audio_files, mix_audio):
    mix_abs = os.path.abspath(mix_audio) if mix_audio else ""
    explicit = [
        item
        for item in audio_files
        if os.path.abspath(item) != mix_abs and in_stem_dir(os.path.relpath(item, path))
    ]
    if explicit:
        return sorted(explicit)

    stems = []
    for item in audio_files:
        if os.path.abspath(item) == mix_abs:
            continue
        name = lower_name(item)
        if any(marker in name for marker in MIX_MARKERS):
            continue
        stems.append(item)
    return sorted(stems)


def candidate_piece_dirs(root, max_depth=7):
    candidates = set()
    root_abs = os.path.abspath(root)
    for current, _, files in walk_dirs_limited(root_abs, max_depth):
        if not any(is_midi(join_path(current, filename)) for filename in files):
            continue
        current_abs = os.path.abspath(current)
        path = current_abs
        for _ in range(3):
            if path == root_abs or path.startswith(root_abs + os.sep):
                candidates.add(path)
            parent = os.path.dirname(path)
            if parent == path:
                break
            path = parent

    accepted = []
    for candidate in sorted(candidates, key=lambda item: (-depth_from_root(root_abs, item), item)):
        if any(child.startswith(candidate + os.sep) for child in accepted):
            continue
        audio_files = find_audio_files(candidate)
        mix_audio = find_mix_audio(audio_files)
        stem_audio = find_stem_audio(candidate, audio_files, mix_audio)
        if find_score_midi(candidate) and mix_audio and stem_audio:
            accepted.append(candidate)
    return sorted(accepted)


def inspect_piece_dir(path, min_stems, min_audio_seconds):
    score_midi = find_score_midi(path)
    audio_files = find_audio_files(path)
    mix_audio = find_mix_audio(audio_files)
    stem_audio = find_stem_audio(path, audio_files, mix_audio)
    readable_midi = bool(score_midi) and midi_header_is_readable(score_midi)

    audio_summaries = []
    compressed_audio_count = 0
    unreadable_audio = []
    for audio in ([mix_audio] if mix_audio else []) + stem_audio:
        summary = audio_summary(audio)
        if summary:
            audio_summaries.append(summary)
        elif lower_name(audio).endswith((".mp3", ".m4a", ".ogg")):
            compressed_audio_count += 1
        else:
            unreadable_audio.append(audio)

    short_audio = [summary for summary in audio_summaries if summary["duration"] < min_audio_seconds]
    complete = (
        readable_midi
        and bool(mix_audio)
        and len(stem_audio) >= min_stems
        and not unreadable_audio
        and not short_audio
    )

    return {
        "path": path,
        "complete": complete,
        "score_midi": score_midi,
        "mix_audio": mix_audio,
        "stem_audio": stem_audio,
        "readable_midi": readable_midi,
        "stem_count": len(stem_audio),
        "compressed_audio_count": compressed_audio_count,
        "audio_summaries": audio_summaries,
        "unreadable_audio": unreadable_audio,
        "short_audio": short_audio,
    }


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_cocochorales_dataset: set MUSIC_ANALYZER_COCOCHORALES_ROOT, "
            "COCOCHORALES_PATH, or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_cocochorales_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_pieces = positive_int_env("MUSIC_ANALYZER_COCOCHORALES_REQUIRED_PIECES", 20)
    min_stems = positive_int_env("MUSIC_ANALYZER_COCOCHORALES_MIN_STEMS", 4)
    min_audio_seconds = positive_float_env("MUSIC_ANALYZER_COCOCHORALES_MIN_AUDIO_SECONDS", 1.0)
    max_depth = positive_int_env("MUSIC_ANALYZER_COCOCHORALES_MAX_DEPTH", 7)

    inspected = [
        inspect_piece_dir(path, min_stems, min_audio_seconds)
        for path in candidate_piece_dirs(root, max_depth=max_depth)
    ]
    complete = [piece for piece in inspected if piece["complete"]]
    stem_counts = [piece["stem_count"] for piece in complete]
    compressed_audio_counts = [piece["compressed_audio_count"] for piece in complete]
    durations = [summary["duration"] for piece in complete for summary in piece["audio_summaries"]]
    channels = [summary["channels"] for piece in complete for summary in piece["audio_summaries"]]
    sample_rate_counts = [
        len({summary["sample_rate"] for summary in piece["audio_summaries"]}) for piece in complete
    ]

    print(
        "inspect_cocochorales_dataset: "
        f"root={root} discovered_pieces={len(inspected)} complete_pieces={len(complete)} "
        f"{range_summary(stem_counts, 'stems per piece')} "
        f"{range_summary(compressed_audio_counts, 'compressed audio per piece')} "
        f"{range_summary(channels, 'channels')} "
        f"{range_summary(sample_rate_counts, 'sample-rate variants per piece')} "
        f"{float_range_summary(durations, 'readable audio seconds per file')}"
    )

    if len(complete) < required_pieces:
        print(
            f"inspect_cocochorales_dataset: expected at least {required_pieces} complete pieces with "
            f"readable score MIDI, mix audio, {min_stems}+ stem audio files, and readable WAV/FLAC "
            f"audio of at least {min_audio_seconds:.2f}s when duration is available; got {len(complete)}",
            file=sys.stderr,
        )
        for piece in inspected[:10]:
            if piece["complete"]:
                continue
            print(
                f"inspect_cocochorales_dataset: incomplete {piece['path']} "
                f"midi={'yes' if piece['readable_midi'] else 'no'} "
                f"mix={'yes' if piece['mix_audio'] else 'no'} "
                f"stems={piece['stem_count']} unreadable_audio={len(piece['unreadable_audio'])} "
                f"short_audio={len(piece['short_audio'])}",
                file=sys.stderr,
            )
        return 1

    print(
        "inspect_cocochorales_dataset: CocoChorales gives large synthetic same-song chamber-ensemble "
        "stems plus MIDI truth; use it as synthesized note/chord stress coverage, not as a replacement "
        "for the real-recorded URMP gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
