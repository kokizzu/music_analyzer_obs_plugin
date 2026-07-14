#!/usr/bin/env python3
import csv
import os
import sys

from inspect_choralsynth_dataset import (
    AUDIO_EXTENSIONS,
    audio_summary,
    float_range_summary,
    join_path,
    lower_name,
    positive_float_env,
    positive_int_env,
    range_summary,
    walk_files,
)


SYNTHSOD_CHILD_NAMES = (
    "SynthSOD-data",
    "SynthSOD",
    "synthsod",
    "SynthSOD-v1",
)
SYNTHSOD_SCORE_CHILD_NAMES = (
    "SynthSOD-aligned-scores",
    "SynthSOD_aligned_scores",
    "aligned-scores",
    "aligned_scores",
    "scores",
)
SOURCE_DIR_NAMES = ("Close Mic", "Close_Mic", "close_mic", "CloseMic", "closemic")
SCORE_EXTENSIONS = (".txt", ".csv", ".tsv")
START_KEYS = ("start", "start_time", "onset", "onset_time", "begin")
END_KEYS = ("end", "end_time", "offset", "offset_time", "stop")
PITCH_KEYS = ("pitch", "note", "midi", "midi_pitch")
INSTRUMENT_KEYS = ("instrument", "program", "midi_instrument", "midi_program")


def is_audio(path):
    return lower_name(path).endswith(AUDIO_EXTENSIONS)


def is_score(path):
    return lower_name(path).endswith(SCORE_EXTENSIONS)


def resolve_audio_root():
    root = os.environ.get("MUSIC_ANALYZER_SYNTHSOD_ROOT") or os.environ.get("SYNTHSOD_PATH")
    if root:
        return normalize_audio_root(root)

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return ""

    for child in SYNTHSOD_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        normalized = normalize_audio_root(candidate)
        if normalized:
            return normalized
    return ""


def normalize_audio_root(root):
    if not root or not os.path.isdir(root):
        return ""
    direct = join_path(root, "SynthSOD-data")
    if os.path.isdir(direct):
        return direct
    return root


def resolve_scores_root(audio_root=""):
    root = os.environ.get("MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT") or os.environ.get("SYNTHSOD_SCORES_PATH")
    if root and os.path.isdir(root):
        return root

    search_roots = []
    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if dataset_root:
        search_roots.append(dataset_root)
    if audio_root:
        search_roots.append(os.path.dirname(audio_root))

    for base in search_roots:
        for child in SYNTHSOD_SCORE_CHILD_NAMES:
            candidate = join_path(base, child)
            if os.path.isdir(candidate):
                return candidate
    return ""


def direct_child_dirs(path):
    try:
        children = sorted(os.scandir(path), key=lambda item: item.name)
    except OSError:
        return []
    return [entry.path for entry in children if entry.is_dir()]


def source_audio_files(piece_dir):
    for source_dir in SOURCE_DIR_NAMES:
        candidate = join_path(piece_dir, source_dir)
        if os.path.isdir(candidate):
            return sorted(item for item in walk_files(candidate) if is_audio(item))

    audio = []
    for item in walk_files(piece_dir):
        rel_parts = [part.lower() for part in os.path.relpath(item, piece_dir).split(os.sep)]
        if "tree" in rel_parts:
            continue
        if is_audio(item):
            audio.append(item)
    return sorted(audio)


def candidate_piece_dirs(audio_root):
    pieces = []
    for child in direct_child_dirs(audio_root):
        if source_audio_files(child):
            pieces.append(child)
    return pieces


def split_cells(line):
    if "," in line:
        return [cell.strip() for cell in next(csv.reader([line]))]
    if "\t" in line:
        return [cell.strip() for cell in line.split("\t")]
    return line.split()


def normalized_header(cells):
    return [cell.strip().lower().replace("-", "_").replace(" ", "_") for cell in cells]


def first_present(row, keys, fallback=""):
    for key in keys:
        if key in row and row[key] != "":
            return row[key]
    return fallback


def numeric_cells(cells):
    values = []
    for cell in cells:
        try:
            values.append(float(cell))
        except ValueError:
            continue
    return values


def read_score_notes(path):
    notes = []
    header = []
    with open(path, "r", encoding="utf-8") as score_file:
        for raw_line in score_file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            cells = split_cells(line)
            if not cells:
                continue
            if not header and any(any(ch.isalpha() for ch in cell) for cell in cells):
                header = normalized_header(cells)
                continue
            try:
                if header:
                    row = {key: value for key, value in zip(header, cells)}
                    start = float(first_present(row, START_KEYS))
                    end = float(first_present(row, END_KEYS))
                    pitch = int(float(first_present(row, PITCH_KEYS)))
                    instrument = int(float(first_present(row, INSTRUMENT_KEYS, "0")))
                else:
                    values = numeric_cells(cells)
                    if len(values) < 4:
                        continue
                    start, end, pitch, instrument = values[:4]
                    pitch = int(pitch)
                    instrument = int(instrument)
            except (TypeError, ValueError):
                continue
            if end > start and end - start >= 0.035 and 21 <= pitch <= 108:
                notes.append((start, end, instrument, pitch))
    return notes


def score_files(scores_root):
    if not scores_root:
        return []
    return sorted(item for item in walk_files(scores_root) if is_score(item))


def find_score_file(piece_id, scores_root, all_scores=None):
    if not scores_root:
        return ""
    for extension in SCORE_EXTENSIONS:
        for candidate in (
            join_path(scores_root, f"{piece_id}{extension}"),
            join_path(scores_root, piece_id, f"{piece_id}{extension}"),
            join_path(scores_root, piece_id, f"score{extension}"),
        ):
            if os.path.isfile(candidate):
                return candidate

    if all_scores is None:
        all_scores = score_files(scores_root)
    lower_piece_id = piece_id.lower()
    matches = [path for path in all_scores if lower_piece_id in os.path.splitext(os.path.basename(path))[0].lower()]
    return matches[0] if matches else ""


def inspect_piece_dir(piece_dir, scores_root, all_scores, min_sources, min_audio_seconds, min_note_rows, min_pitch_classes):
    piece_id = os.path.basename(piece_dir.rstrip(os.sep))
    source_audio = source_audio_files(piece_dir)
    audio_summaries = []
    unreadable_audio = []
    for path in source_audio:
        summary = audio_summary(path)
        if summary:
            audio_summaries.append(summary)
        else:
            unreadable_audio.append(path)

    short_audio = [summary for summary in audio_summaries if summary["duration"] < min_audio_seconds]
    score_path = find_score_file(piece_id, scores_root, all_scores)
    notes = read_score_notes(score_path) if score_path else []
    pitch_classes = {note[3] % 12 for note in notes}
    complete = (
        len(source_audio) >= min_sources
        and len(audio_summaries) >= min_sources
        and not unreadable_audio
        and not short_audio
        and score_path
        and len(notes) >= min_note_rows
        and len(pitch_classes) >= min_pitch_classes
    )
    return {
        "path": piece_dir,
        "id": piece_id,
        "complete": complete,
        "source_audio": source_audio,
        "source_count": len(source_audio),
        "audio_summaries": audio_summaries,
        "unreadable_audio": unreadable_audio,
        "short_audio": short_audio,
        "score_path": score_path,
        "note_rows": len(notes),
        "pitch_classes": len(pitch_classes),
    }


def inspected_pieces(audio_root, scores_root, min_sources, min_audio_seconds, min_note_rows, min_pitch_classes):
    all_scores = score_files(scores_root)
    return [
        inspect_piece_dir(piece, scores_root, all_scores, min_sources, min_audio_seconds, min_note_rows, min_pitch_classes)
        for piece in candidate_piece_dirs(audio_root)
    ]


def main():
    audio_root = resolve_audio_root()
    if not audio_root:
        print(
            "inspect_synthsod_dataset: set MUSIC_ANALYZER_SYNTHSOD_ROOT, SYNTHSOD_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    scores_root = resolve_scores_root(audio_root)
    if not scores_root:
        print(
            "inspect_synthsod_dataset: set MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT, SYNTHSOD_SCORES_PATH, "
            "or place SynthSOD aligned scores near the audio root",
            file=sys.stderr,
        )
        return 1

    required_pieces = positive_int_env("MUSIC_ANALYZER_SYNTHSOD_REQUIRED_PIECES", 20)
    min_sources = positive_int_env("MUSIC_ANALYZER_SYNTHSOD_MIN_SOURCES", 4)
    min_audio_seconds = positive_float_env("MUSIC_ANALYZER_SYNTHSOD_MIN_AUDIO_SECONDS", 1.0)
    min_note_rows = positive_int_env("MUSIC_ANALYZER_SYNTHSOD_MIN_NOTE_ROWS", 4)
    min_pitch_classes = positive_int_env("MUSIC_ANALYZER_SYNTHSOD_MIN_PITCH_CLASSES", 3)

    try:
        inspected = inspected_pieces(
            audio_root, scores_root, min_sources, min_audio_seconds, min_note_rows, min_pitch_classes
        )
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        print(f"inspect_synthsod_dataset: {exc}", file=sys.stderr)
        return 1

    complete = [piece for piece in inspected if piece["complete"]]
    durations = [summary["duration"] for piece in complete for summary in piece["audio_summaries"]]
    channels = [summary["channels"] for piece in complete for summary in piece["audio_summaries"]]
    sample_rate_counts = [
        len({summary["sample_rate"] for summary in piece["audio_summaries"]}) for piece in complete
    ]
    print(
        "inspect_synthsod_dataset: "
        f"audio_root={audio_root} scores_root={scores_root} discovered_pieces={len(inspected)} "
        f"complete_pieces={len(complete)} "
        f"{range_summary([piece['source_count'] for piece in complete], 'source tracks per piece')} "
        f"{range_summary([piece['note_rows'] for piece in complete], 'score note rows per piece')} "
        f"{range_summary([piece['pitch_classes'] for piece in complete], 'pitch classes per piece')} "
        f"{range_summary(channels, 'channels')} "
        f"{range_summary(sample_rate_counts, 'sample-rate variants per piece')} "
        f"{float_range_summary(durations, 'audio seconds per source')}"
    )

    if len(complete) < required_pieces:
        print(
            f"inspect_synthsod_dataset: expected at least {required_pieces} complete SynthSOD pieces "
            f"with {min_sources}+ close-mic source tracks, aligned score text, and readable audio; "
            f"got {len(complete)}",
            file=sys.stderr,
        )
        for piece in inspected[:10]:
            if piece["complete"]:
                continue
            print(
                f"inspect_synthsod_dataset: incomplete {piece['path']} sources={piece['source_count']} "
                f"score={'yes' if piece['score_path'] else 'no'} notes={piece['note_rows']} "
                f"unreadable_audio={len(piece['unreadable_audio'])} short_audio={len(piece['short_audio'])}",
                file=sys.stderr,
            )
        return 1

    print(
        "inspect_synthsod_dataset: SynthSOD gives 20+ synthesized same-song orchestra/ensemble stems "
        "plus aligned score-note text; use it as a large note/chord stress add-on, not as a replacement "
        "for the real-recorded URMP gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
