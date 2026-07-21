#!/usr/bin/env python3

import argparse
import csv
import io
import math
import os
from pathlib import Path
import re
import sys
import wave
import zipfile


FIXTURE_VERSION = "vocalset-v1"
MIDI_RANGE = (40, 84)
DEFAULT_ALLOWED_TECHNIQUES = (
    "belt,breathy,fast_forte,fast_piano,forte,lip_trill,messa,slow_forte,"
    "slow_piano,straight,trill,trillo,vibrato"
)
ALL_FILES_RE = re.compile(r"(^|/)VocalSet/annotations/extended 4/all files\.csv$")
AUDIO_RE = re.compile(r"(^|/)VocalSet/FULL/([^/]+)/([^/]+)/([^/]+)/([^/]+)\.wav$")
EXTENDED_FILE_RE = re.compile(
    r"(^|/)VocalSet/annotations/extended 4/(?:with|without) file header/([^/]+)/([^/]+)\.csv$"
)


EXTENDED_WITHOUT_HEADER = [
    "sequence",
    "start_time",
    "end_time",
    "duration",
    "type",
    "average_f0",
    "median_f0",
    "min_f0",
    "max_f0",
    "std_f0",
    "average_f0_in_range_of_std",
    "estimated_midi_code",
    "ground_truth_note_name",
    "ground_truth_frequency",
    "ground_truth_midi_code",
    "lyric",
]


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def midi_frequency(midi):
    return 440.0 * math.pow(2.0, (midi - 69) / 12.0)


def frequency_to_midi(freq):
    midi = int(round(69.0 + 12.0 * math.log2(freq / 440.0)))
    cents = 1200.0 * math.log2(freq / midi_frequency(midi))
    return midi, cents


def cents_from_midi(freq, midi):
    return 1200.0 * math.log2(freq / midi_frequency(midi))


def sanitize_id(text):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")


def normalize_header(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).strip().lower()).strip("_")


def normalize_key(text):
    return sanitize_id(str(text).strip().lower())


def normalize_stem(text):
    name = str(text).replace("\\", "/").rsplit("/", 1)[-1].strip()
    if name.lower().endswith((".wav", ".csv", ".txt")):
        name = name.rsplit(".", 1)[0]
    return normalize_key(name)


def parse_allowed_techniques(text):
    if not str(text).strip():
        return set()
    return {normalize_key(part) for part in str(text).split(",") if normalize_key(part)}


def parse_float(value):
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none", "null", "na", "n/a", "-"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_int_like(value):
    parsed = parse_float(value)
    if parsed is None:
        return None
    rounded = int(round(parsed))
    if abs(parsed - rounded) > 0.05:
        return None
    return rounded


def first_value(row, names):
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip():
            return value
    return ""


def first_float(row, names):
    for name in names:
        value = parse_float(row.get(name))
        if value is not None:
            return value
    return None


def first_int(row, names):
    for name in names:
        value = parse_int_like(row.get(name))
        if value is not None:
            return value
    return None


def scan_audio_members(archive):
    audio_by_stem = {}
    for member in archive.namelist():
        if member.startswith("__MACOSX/") or "/._" in member:
            continue
        match = AUDIO_RE.match(member)
        if not match:
            continue
        singer, song_type, technique, filename = match.group(2), match.group(3), match.group(4), match.group(5)
        key = normalize_stem(filename)
        audio_by_stem[key] = {
            "member": member,
            "singer": singer,
            "song_type": song_type,
            "technique": technique,
            "filename": filename,
        }
    return audio_by_stem


def normalize_dict_row(header, row):
    normalized = {}
    for index, name in enumerate(header):
        if index < len(row):
            normalized[normalize_header(name)] = row[index]
    return normalized


def read_annotation_rows(archive, members):
    for member in members:
        with archive.open(member) as source:
            wrapper = io.TextIOWrapper(source, encoding="utf-8-sig", newline="")
            reader = csv.reader(wrapper)
            rows = [row for row in reader if any(str(value).strip() for value in row)]
        if not rows:
            continue

        derived_stem = normalize_stem(member)
        if ALL_FILES_RE.match(member):
            header = rows[0]
            for row in rows[1:]:
                normalized = normalize_dict_row(header, row)
                if "filename" not in normalized:
                    normalized["filename"] = derived_stem
                yield member, normalized
            continue

        header_index = None
        for index, row in enumerate(rows[:30]):
            normalized_headers = {normalize_header(value) for value in row}
            if "sequence" in normalized_headers and (
                "start_time" in normalized_headers or "start_time_seconds" in normalized_headers
            ):
                header_index = index
                break
        if header_index is not None:
            header = rows[header_index]
            data_rows = rows[header_index + 1:]
        else:
            header = EXTENDED_WITHOUT_HEADER
            data_rows = rows

        for row in data_rows:
            normalized = normalize_dict_row(header, row)
            normalized.setdefault("filename", derived_stem)
            yield member, normalized


def annotation_members(archive):
    all_files = []
    fallback = []
    for member in archive.namelist():
        if ALL_FILES_RE.match(member):
            all_files.append(member)
        elif EXTENDED_FILE_RE.match(member):
            fallback.append(member)
    return sorted(all_files) or sorted(fallback)


def wav_params_from_bytes(data):
    with wave.open(io.BytesIO(data), "rb") as source:
        return {
            "channels": source.getnchannels(),
            "sample_width": source.getsampwidth(),
            "sample_rate": source.getframerate(),
            "frames": source.getnframes(),
            "params": source.getparams(),
        }


def extract_clip(audio_data, output_path, start_seconds, duration_seconds):
    with wave.open(io.BytesIO(audio_data), "rb") as source:
        sample_rate = source.getframerate()
        start_frame = max(0, int(round(start_seconds * sample_rate)))
        frame_count = max(1, int(round(duration_seconds * sample_rate)))
        if start_frame >= source.getnframes():
            return False
        frame_count = min(frame_count, source.getnframes() - start_frame)
        source.setpos(start_frame)
        frames = source.readframes(frame_count)
        params = source.getparams()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with wave.open(str(temporary_path), "wb") as target:
        target.setparams(params)
        target.writeframes(frames)
    temporary_path.replace(output_path)
    return True


def candidate_clip_window(start, duration, min_duration, attack_margin, release_margin, clip_seconds):
    stable_start = start + attack_margin
    stable_end = start + duration - release_margin
    if stable_end - stable_start < min_duration:
        return None
    available = stable_end - stable_start
    clip_duration = min(clip_seconds, available)
    clip_start = stable_start + max(0.0, (available - clip_duration) * 0.5)
    if clip_duration <= 0.0:
        return None
    return clip_start, clip_duration


def row_to_candidate(row, audio_by_stem, allowed_techniques, min_note_duration, max_cents,
                     attack_margin, release_margin, clip_seconds, skipped):
    filename = first_value(row, ["filename", "file", "audio_file", "wav_file", "file_name"])
    stem = normalize_stem(filename)
    if not stem:
        skipped["missing_filename"] = skipped.get("missing_filename", 0) + 1
        return None
    audio_meta = audio_by_stem.get(stem)
    if not audio_meta:
        skipped["missing_audio"] = skipped.get("missing_audio", 0) + 1
        return None

    row_type = normalize_key(first_value(row, ["type", "event_type", "segment_type"]))
    if row_type and row_type not in {"sound", "note", "voiced", "singing"}:
        skipped["non_sound"] = skipped.get("non_sound", 0) + 1
        return None

    technique = first_value(row, ["the_technique", "technique"]) or audio_meta["technique"]
    if allowed_techniques and normalize_key(technique) not in allowed_techniques:
        skipped["filtered_technique"] = skipped.get("filtered_technique", 0) + 1
        return None

    start = first_float(row, ["start_time", "start_time_seconds", "start", "onset"])
    end = first_float(row, ["end_time", "end_time_seconds", "end", "offset"])
    duration = first_float(row, ["duration", "duration_seconds"])
    if start is None:
        skipped["missing_time"] = skipped.get("missing_time", 0) + 1
        return None
    if duration is None and end is not None:
        duration = end - start
    if duration is None or duration < min_note_duration:
        skipped["short_note"] = skipped.get("short_note", 0) + 1
        return None

    freq = first_float(row, [
        "median_f0",
        "average_f0_in_range_of_std",
        "average_f0",
        "ground_truth_frequency",
        "frequency",
        "freq",
        "f0",
    ])
    midi = first_int(row, [
        "estimated_midi_code",
        "estimated_midi",
        "midi",
        "midi_code",
        "ground_truth_midi_code",
        "ground_truth_midi",
    ])
    if freq is None or freq <= 0.0:
        skipped["missing_frequency"] = skipped.get("missing_frequency", 0) + 1
        return None
    if midi is None:
        try:
            midi, cents = frequency_to_midi(freq)
        except ValueError:
            skipped["bad_frequency"] = skipped.get("bad_frequency", 0) + 1
            return None
    else:
        cents = cents_from_midi(freq, midi)

    if midi < MIDI_RANGE[0] or midi > MIDI_RANGE[1]:
        skipped["outside_vocal_range"] = skipped.get("outside_vocal_range", 0) + 1
        return None
    if abs(cents) > max_cents:
        skipped["off_chromatic"] = skipped.get("off_chromatic", 0) + 1
        return None

    window = candidate_clip_window(
        start,
        duration,
        min_note_duration,
        attack_margin,
        release_margin,
        clip_seconds,
    )
    if not window:
        skipped["no_stable_window"] = skipped.get("no_stable_window", 0) + 1
        return None

    clip_start, clip_duration = window
    singer = first_value(row, ["singer_name", "singer"]) or audio_meta["singer"]
    song_type = first_value(row, ["type_of_music", "music_type", "category"]) or audio_meta["song_type"]
    sequence = first_value(row, ["sequence", "seq", "note_index"]) or f"{int(round(start * 1000)):06d}"
    candidate_base = f"vocalset_{stem}_{sanitize_id(sequence)}_{note_name(midi)}"
    source = f"vocalset-{singer}-{song_type}-{technique}"
    return {
        "id": sanitize_id(candidate_base),
        "family": "vocals",
        "nsynth_family": "vocal",
        "source": sanitize_id(source.lower()),
        "midi": midi,
        "note": note_name(midi),
        "path": str(Path("audio") / f"{sanitize_id(candidate_base)}.wav"),
        "qualities": (
            f"singer={singer},type={song_type},technique={technique},"
            f"filename={audio_meta['filename']},freq={freq:.3f},cents={cents:.2f},"
            f"duration={duration:.3f},start={start:.3f},{FIXTURE_VERSION}"
        ),
        "audio_member": audio_meta["member"],
        "clip_start": clip_start,
        "clip_duration": clip_duration,
    }


def collect_candidates(archive, allowed_techniques, min_note_duration, max_cents,
                       attack_margin, release_margin, clip_seconds):
    audio_by_stem = scan_audio_members(archive)
    members = annotation_members(archive)
    candidates = []
    skipped = {}

    if not members:
        raise SystemExit("prepare_vocalset_samples: no extended VocalSet annotation CSV found")
    if not audio_by_stem:
        raise SystemExit("prepare_vocalset_samples: no VocalSet/FULL WAV files found")

    for _, row in read_annotation_rows(archive, members):
        candidate = row_to_candidate(
            row,
            audio_by_stem,
            allowed_techniques,
            min_note_duration,
            max_cents,
            attack_margin,
            release_margin,
            clip_seconds,
            skipped,
        )
        if candidate is not None:
            candidates.append(candidate)

    candidates.sort(key=lambda row: (
        row["midi"],
        row["source"],
        row["audio_member"],
        row["clip_start"],
        row["id"],
    ))
    return candidates, skipped


def limit_balanced(candidates, limit):
    if limit <= 0 or len(candidates) <= limit:
        return candidates
    buckets = {}
    for row in candidates:
        buckets.setdefault(row["midi"], []).append(row)
    for rows in buckets.values():
        rows.sort(key=lambda row: (row["source"], row["audio_member"], row["clip_start"], row["id"]))

    selected = []
    while len(selected) < limit:
        progressed = False
        for midi in sorted(buckets):
            rows = buckets[midi]
            if rows:
                selected.append(rows.pop(0))
                progressed = True
                if len(selected) >= limit:
                    break
        if not progressed:
            break
    selected.sort(key=lambda row: (row["source"], row["audio_member"], row["clip_start"], row["id"]))
    return selected


def write_manifest(path, rows):
    with path.open("w", encoding="utf-8") as file:
        file.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities\n")
        for row in rows:
            file.write(
                "\t".join([
                    row["id"],
                    row["family"],
                    row["nsynth_family"],
                    row["source"],
                    str(row["midi"]),
                    row["note"],
                    row["path"],
                    row["qualities"],
                ]) + "\n"
            )


def manifest_complete(path, min_rows):
    if not path.is_file():
        return False
    rows = 0
    root = path.parent
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header[:7] != ["id", "family", "nsynth_family", "source", "midi", "note", "path"]:
            return False
        for line in file:
            if not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                return False
            if not (root / fields[6]).is_file():
                return False
            rows += 1
    return rows >= max(1, min_rows)


def prepare_samples(archive_path, output_dir, allowed_techniques=None, limit=0, min_samples=800,
                    min_note_duration=0.22, max_cents=25.0, attack_margin=0.04,
                    release_margin=0.03, clip_seconds=0.72, refresh=False):
    output_dir = Path(output_dir)
    manifest_path = output_dir / "manifest.tsv"
    min_samples = max(0, int(min_samples))
    if not refresh and manifest_complete(manifest_path, min_samples):
        print(f"prepare_vocalset_samples: keeping existing {manifest_path}")
        return

    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise SystemExit(f"prepare_vocalset_samples: missing archive: {archive_path}")

    allowed = parse_allowed_techniques(
        DEFAULT_ALLOWED_TECHNIQUES if allowed_techniques is None else allowed_techniques
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        candidates, skipped = collect_candidates(
            archive,
            allowed,
            min_note_duration,
            max_cents,
            attack_margin,
            release_margin,
            clip_seconds,
        )
        selected = limit_balanced(candidates, int(limit))
        prepared = []
        audio_cache = {}
        for row in selected:
            output_path = output_dir / row["path"]
            if not output_path.is_file():
                audio_data = audio_cache.get(row["audio_member"])
                if audio_data is None:
                    audio_data = archive.read(row["audio_member"])
                    params = wav_params_from_bytes(audio_data)
                    if params["sample_width"] not in (2, 3, 4) or params["frames"] <= 0:
                        skipped["unsupported_wav"] = skipped.get("unsupported_wav", 0) + 1
                        continue
                    audio_cache[row["audio_member"]] = audio_data
                if not extract_clip(audio_data, output_path, row["clip_start"], row["clip_duration"]):
                    skipped["clip_failed"] = skipped.get("clip_failed", 0) + 1
                    continue
            prepared.append(row)

    required_prepared = max(1, min_samples)
    if len(prepared) < required_prepared:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, prepared)
        print(f"prepare_vocalset_samples: wrote {len(prepared)} rows to {partial_path}", file=sys.stderr)
        raise SystemExit(
            f"prepare_vocalset_samples: expected at least {required_prepared} prepared samples, "
            f"got {len(prepared)}"
        )

    write_manifest(manifest_path, prepared)
    midi_counts = {}
    for row in prepared:
        midi_counts[row["midi"]] = midi_counts.get(row["midi"], 0) + 1
    note_span = ""
    if midi_counts:
        note_span = f", range {note_name(min(midi_counts))}-{note_name(max(midi_counts))}"
    skipped_text = " ".join(f"{name}={skipped[name]}" for name in sorted(skipped))
    print(
        f"prepare_vocalset_samples: wrote {len(prepared)} rows to {manifest_path} "
        f"(vocals={len(prepared)}{note_span}, unique_notes={len(midi_counts)}, skipped {skipped_text})"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare VocalSet real vocal note fixtures.")
    parser.add_argument("--archive", default=os.environ.get(
        "VOCALSET_ARCHIVE",
        "build/real_sample_sources/vocalset/VocalSet.zip"))
    parser.add_argument("--output", default=os.environ.get(
        "VOCALSET_SAMPLE_DIR",
        "build/vocalset_samples"))
    parser.add_argument("--allowed-techniques", default=os.environ.get(
        "VOCALSET_ALLOWED_TECHNIQUES",
        DEFAULT_ALLOWED_TECHNIQUES))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("VOCALSET_SAMPLE_LIMIT", "1200")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("VOCALSET_MIN_VOCALS", "800")))
    parser.add_argument("--min-note-duration", type=float, default=float(os.environ.get(
        "VOCALSET_MIN_NOTE_DURATION", "0.22")))
    parser.add_argument("--max-cents", type=float, default=float(os.environ.get("VOCALSET_MAX_CENTS", "25")))
    parser.add_argument("--attack-margin", type=float, default=float(os.environ.get(
        "VOCALSET_ATTACK_MARGIN", "0.04")))
    parser.add_argument("--release-margin", type=float, default=float(os.environ.get(
        "VOCALSET_RELEASE_MARGIN", "0.03")))
    parser.add_argument("--clip-seconds", type=float, default=float(os.environ.get(
        "VOCALSET_CLIP_SECONDS", "0.72")))
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("VOCALSET_REFRESH") == "1")
    args = parser.parse_args(argv)

    prepare_samples(
        args.archive,
        args.output,
        allowed_techniques=args.allowed_techniques,
        limit=args.limit,
        min_samples=args.min_samples,
        min_note_duration=args.min_note_duration,
        max_cents=args.max_cents,
        attack_margin=args.attack_margin,
        release_margin=args.release_margin,
        clip_seconds=args.clip_seconds,
        refresh=args.refresh,
    )


if __name__ == "__main__":
    main()
