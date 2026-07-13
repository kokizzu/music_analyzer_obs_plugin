#!/usr/bin/env python3
import csv
import json
import os
import sys
import wave


AUDIO_EXTENSIONS = (".wav", ".wave", ".flac", ".mp3", ".m4a", ".ogg")
F0_EXTENSIONS = (".csv", ".txt", ".jams", ".json")
POLYVOCAL_CHILD_NAMES = (
    "polyvocal",
    "PolyVocal",
    "vocal_ensemble_f0",
    "vocal-ensemble-f0",
    "multif0-estimation-vocals-data",
    "multif0-estimation-vocals",
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


def truthy_env(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def join_path(lhs, *children):
    path = lhs
    for child in children:
        path = os.path.join(path, child)
    return path


def lower_name(path):
    return os.path.basename(path).lower()


def is_audio(path):
    return lower_name(path).endswith(AUDIO_EXTENSIONS)


def is_f0_annotation(path):
    return lower_name(path).endswith(F0_EXTENSIONS)


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_POLYVOCAL_ROOT") or os.environ.get("POLYVOCAL_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in POLYVOCAL_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def resolve_existing_path(root, base, path):
    if not path:
        return ""
    if os.path.isabs(path) and os.path.exists(path):
        return path
    candidates = []
    if os.path.isabs(path):
        candidates.append(path)
    else:
        candidates.append(join_path(base, path))
        candidates.append(join_path(root, path))
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[0] if candidates else ""


def walk_files(path):
    for current, _, files in os.walk(path):
        for filename in files:
            yield join_path(current, filename)


def read_wav_summary(path):
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


def read_flac_summary(path):
    try:
        with open(path, "rb") as audio:
            if audio.read(4) != b"fLaC":
                return None
            while True:
                header = audio.read(4)
                if len(header) != 4:
                    return None
                block_type = header[0] & 0x7F
                length = int.from_bytes(header[1:4], "big")
                data = audio.read(length)
                if len(data) != length:
                    return None
                if block_type == 0:
                    if length < 34:
                        return None
                    packed = int.from_bytes(data[10:18], "big")
                    sample_rate = (packed >> 44) & 0xFFFFF
                    channels = ((packed >> 41) & 0x7) + 1
                    total_samples = packed & 0xFFFFFFFFF
                    if sample_rate <= 0 or total_samples <= 0:
                        return None
                    return {
                        "channels": channels,
                        "sample_rate": sample_rate,
                        "frames": total_samples,
                        "duration": total_samples / float(sample_rate),
                    }
    except OSError:
        return None


def audio_summary(path):
    name = lower_name(path)
    if name.endswith(".flac"):
        return read_flac_summary(path)
    if name.endswith((".wav", ".wave")):
        return read_wav_summary(path)
    return None


def mtracks_info_candidates(root):
    direct = [
        join_path(root, "mtracks_info.json"),
        join_path(root, "metadata", "mtracks_info.json"),
        join_path(root, "audiomixtures", "mtracks_info.json"),
        join_path(root, "features", "mtracks_info.json"),
    ]
    for candidate in direct:
        if os.path.isfile(candidate):
            return [candidate]

    matches = []
    for current, dirs, files in os.walk(root):
        depth = os.path.relpath(current, root).count(os.sep)
        if depth > 2:
            dirs[:] = []
            continue
        if "mtracks_info.json" in files:
            matches.append(join_path(current, "mtracks_info.json"))
    return sorted(matches)


def load_mtracks_info(root):
    candidates = mtracks_info_candidates(root)
    if not candidates:
        return "", {}
    path = candidates[0]
    with open(path, "r", encoding="utf-8") as info_file:
        info = json.load(info_file)
    return path, info if isinstance(info, dict) else {}


def read_numeric_csv_points(path, max_points=8):
    points = []
    with open(path, newline="", encoding="utf-8") as annotation_file:
        reader = csv.reader(annotation_file)
        header = None
        for row in reader:
            if not row:
                continue
            stripped = [cell.strip() for cell in row]
            numeric = []
            for cell in stripped:
                try:
                    numeric.append(float(cell))
                except ValueError:
                    pass
            if len(numeric) < 2:
                if header is None:
                    header = [cell.lower() for cell in stripped]
                continue
            time_value = numeric[0]
            freq_value = None
            if header:
                for name in ("frequency", "freq", "f0", "hz", "pitch"):
                    if name in header:
                        index = header.index(name)
                        if index < len(stripped):
                            try:
                                freq_value = float(stripped[index])
                            except ValueError:
                                freq_value = None
                        break
            if freq_value is None:
                freq_value = numeric[1]
            if time_value >= 0.0 and freq_value > 0.0:
                points.append((time_value, freq_value))
                if len(points) >= max_points:
                    break
    return points


def iter_jams_values(value):
    if isinstance(value, dict):
        for key in ("frequency", "freq", "f0", "hz", "pitch", "value"):
            raw = value.get(key)
            if isinstance(raw, (int, float)):
                yield float(raw)
    elif isinstance(value, (int, float)):
        yield float(value)


def read_json_f0_points(path, max_points=8):
    with open(path, "r", encoding="utf-8") as annotation_file:
        document = json.load(annotation_file)
    annotations = document.get("annotations", []) if isinstance(document, dict) else []
    points = []
    for annotation in annotations:
        data = annotation.get("data", []) if isinstance(annotation, dict) else []
        for item in data:
            if not isinstance(item, dict):
                continue
            time_value = item.get("time")
            if not isinstance(time_value, (int, float)) or time_value < 0.0:
                continue
            for freq_value in iter_jams_values(item.get("value")):
                if freq_value > 0.0:
                    points.append((float(time_value), freq_value))
                    break
            if len(points) >= max_points:
                return points
    return points


def f0_preview_points(path, max_points=8):
    name = lower_name(path)
    try:
        if name.endswith((".jams", ".json")):
            return read_json_f0_points(path, max_points)
        return read_numeric_csv_points(path, max_points)
    except (OSError, csv.Error, json.JSONDecodeError, UnicodeDecodeError):
        return []


def annotation_paths(root, base, entry):
    annot_files = entry.get("annot_files") or entry.get("annotation_files") or entry.get("f0_files") or []
    if not isinstance(annot_files, list):
        annot_files = []

    annot_folder = entry.get("annot_folder") or entry.get("annotation_folder") or entry.get("f0_folder") or ""
    annot_base = resolve_existing_path(root, base, annot_folder) if annot_folder else base

    resolved = []
    for item in annot_files:
        if not isinstance(item, str):
            continue
        resolved.append(resolve_existing_path(root, annot_base, item))
    return resolved


def list_entry_paths(entry, names):
    for name in names:
        value = entry.get(name)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return list(value.values())
    return []


def source_audio_paths(root, base, entry):
    source_files = list_entry_paths(
        entry,
        (
            "source_audio_files",
            "source_files",
            "stem_files",
            "voice_files",
            "audio_sources",
            "sources",
        ),
    )
    source_folder = (
        entry.get("source_audio_folder")
        or entry.get("source_folder")
        or entry.get("stem_folder")
        or entry.get("voice_folder")
        or ""
    )
    source_base = resolve_existing_path(root, base, source_folder) if source_folder else base

    resolved = []
    for item in source_files:
        path = ""
        if isinstance(item, str):
            path = item
        elif isinstance(item, dict):
            for key in ("audio_file", "audio", "path", "file"):
                value = item.get(key)
                if isinstance(value, str) and value:
                    path = value
                    break
        if path:
            resolved.append(resolve_existing_path(root, source_base, path))
    return resolved


def audio_path_for_entry(root, base, audio_name, entry):
    explicit = entry.get("audio_file") or entry.get("audio") or entry.get("mix_audio")
    if isinstance(explicit, str) and explicit:
        return resolve_existing_path(root, base, explicit)

    audio_folder = entry.get("audiopath") or entry.get("audio_folder") or entry.get("mix_folder") or ""
    audio_base = resolve_existing_path(root, base, audio_folder) if audio_folder else base
    return resolve_existing_path(root, audio_base, audio_name)


def inspect_entry(root, info_path, audio_name, entry, min_voices, min_audio_seconds, min_f0_points):
    base = os.path.dirname(info_path)
    if not isinstance(entry, dict):
        entry = {}
    audio_path = audio_path_for_entry(root, base, audio_name, entry)
    annotations = annotation_paths(root, base, entry)
    source_paths = source_audio_paths(root, base, entry)
    audio_readable = os.path.isfile(audio_path) and is_audio(audio_path)
    summary = audio_summary(audio_path) if audio_readable else None
    compressed_audio = audio_readable and summary is None and lower_name(audio_path).endswith((".mp3", ".m4a", ".ogg"))
    source_audio_count = sum(
        1
        for path in source_paths
        if os.path.isfile(path)
        and is_audio(path)
        and (audio_summary(path) is not None or lower_name(path).endswith((".mp3", ".m4a", ".ogg")))
    )
    require_source_audio = truthy_env("MUSIC_ANALYZER_POLYVOCAL_REQUIRE_SOURCE_AUDIO")
    previews = [f0_preview_points(path, min_f0_points) for path in annotations if os.path.isfile(path)]
    usable_annotations = sum(1 for preview in previews if len(preview) >= min_f0_points)
    complete = (
        audio_readable
        and (summary is not None or compressed_audio)
        and (summary is None or summary["duration"] >= min_audio_seconds)
        and len(annotations) >= min_voices
        and usable_annotations >= min_voices
        and (not require_source_audio or source_audio_count >= min_voices)
    )

    return {
        "audio_name": audio_name,
        "audio_path": audio_path,
        "complete": complete,
        "audio_summary": summary,
        "compressed_audio": compressed_audio,
        "annotations": annotations,
        "source_audio_paths": source_paths,
        "source_audio_count": source_audio_count,
        "usable_annotations": usable_annotations,
        "preview_points": [len(preview) for preview in previews],
    }


def complete_entries(root, min_voices, min_audio_seconds, min_f0_points):
    info_path, info = load_mtracks_info(root)
    if not info_path:
        return "", []
    entries = []
    for audio_name, entry in sorted(info.items()):
        if not isinstance(audio_name, str):
            continue
        entries.append(inspect_entry(root, info_path, audio_name, entry, min_voices, min_audio_seconds, min_f0_points))
    return info_path, entries


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
            "inspect_polyvocal_dataset: set MUSIC_ANALYZER_POLYVOCAL_ROOT, POLYVOCAL_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_polyvocal_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_pieces = positive_int_env("MUSIC_ANALYZER_POLYVOCAL_REQUIRED_PIECES", 20)
    min_voices = positive_int_env("MUSIC_ANALYZER_POLYVOCAL_MIN_VOICES", 4)
    min_audio_seconds = positive_float_env("MUSIC_ANALYZER_POLYVOCAL_MIN_AUDIO_SECONDS", 1.0)
    min_f0_points = positive_int_env("MUSIC_ANALYZER_POLYVOCAL_MIN_F0_POINTS", 4)

    try:
        info_path, inspected = complete_entries(root, min_voices, min_audio_seconds, min_f0_points)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"inspect_polyvocal_dataset: {exc}", file=sys.stderr)
        return 1

    if not info_path:
        print(f"inspect_polyvocal_dataset: no mtracks_info.json found under `{root}`", file=sys.stderr)
        return 1

    complete = [entry for entry in inspected if entry["complete"]]
    durations = [
        entry["audio_summary"]["duration"]
        for entry in complete
        if entry["audio_summary"] is not None
    ]
    voice_counts = [len(entry["annotations"]) for entry in complete]
    source_counts = [entry["source_audio_count"] for entry in complete]
    usable_counts = [entry["usable_annotations"] for entry in complete]
    compressed = sum(1 for entry in complete if entry["compressed_audio"])

    if len(complete) < required_pieces:
        print(
            f"inspect_polyvocal_dataset: expected at least {required_pieces} complete vocal ensemble mixes, "
            f"got {len(complete)} from {len(inspected)} entries in {info_path}",
            file=sys.stderr,
        )
        return 1

    print(
        "inspect_polyvocal_dataset: "
        f"complete={len(complete)}/{len(inspected)} mtracks={info_path} compressed_audio={compressed}, "
        f"{range_summary(voice_counts, 'voices per mix')}, "
        f"{range_summary(source_counts, 'source audio tracks per mix')}, "
        f"{range_summary(usable_counts, 'usable F0 annotations per mix')}, "
        f"{float_range_summary(durations, 'audio seconds')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
