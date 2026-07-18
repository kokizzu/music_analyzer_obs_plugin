#!/usr/bin/env python3

import argparse
import csv
import io
import os
from pathlib import Path
import re
import sys
import wave
import xml.etree.ElementTree as ET
import zipfile


FIXTURE_VERSION = "idmt-bass-lines-v1"
CSV_RE = re.compile(r"^misc/notes_csv/(\d{3})_note_parameters\.csv$")
AUDIO_RE = re.compile(r"^audio/(\d{3})\.wav$")
XML_RE = re.compile(r"^annotation/(\d{3})\.xml$")
BASS_RANGE = (28, 67)


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def sanitize_id(text):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")


def split_csv_set(text):
    values = {item.strip().upper() for item in str(text).split(",") if item.strip()}
    return values


def scan_archive(archive):
    audio = {}
    csvs = {}
    xmls = {}
    for member in archive.namelist():
        if member.startswith("__MACOSX/") or "/._" in member:
            continue
        audio_match = AUDIO_RE.match(member)
        if audio_match:
            audio[audio_match.group(1)] = member
            continue
        csv_match = CSV_RE.match(member)
        if csv_match:
            csvs[csv_match.group(1)] = member
            continue
        xml_match = XML_RE.match(member)
        if xml_match:
            xmls[xml_match.group(1)] = member
    return audio, csvs, xmls


def xml_metadata(archive, member):
    if not member:
        return {}
    try:
        root = ET.fromstring(archive.read(member))
    except ET.ParseError:
        return {}
    params = root.find("globalParameter")
    if params is None:
        return {}

    def text(name):
        node = params.find(name)
        return (node.text or "").strip() if node is not None else ""

    return {
        "instrument": text("instrument"),
        "model": text("instrumentModel"),
        "pickup": text("pickUpSetting"),
        "tuning": text("instrumentTuning"),
    }


def read_note_rows(archive, member):
    rows = []
    with archive.open(member) as source:
        wrapper = io.TextIOWrapper(source, encoding="utf-8", newline="")
        for index, row in enumerate(csv.reader(wrapper), start=1):
            if len(row) < 9:
                continue
            try:
                onset = float(row[0])
                offset = float(row[1])
                midi = int(row[2])
                string_number = int(row[3])
                fret_number = int(row[4])
            except ValueError as exc:
                raise SystemExit(
                    f"prepare_idmt_bass_lines_samples: bad note row {member}:{index}: {row}"
                ) from exc
            if offset <= onset:
                continue
            rows.append({
                "onset": onset,
                "offset": offset,
                "duration": offset - onset,
                "midi": midi,
                "string": string_number,
                "fret": fret_number,
                "pluck": row[5].strip().upper(),
                "expression": row[6].strip().upper(),
                "modulation_frequency": row[7].strip(),
                "modulation_range": row[8].strip(),
            })
    return rows


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


def clip_window(note, audio_seconds, min_stable_seconds, attack_margin, release_margin, clip_seconds):
    stable_start = note["onset"] + attack_margin
    stable_end = note["offset"] - release_margin
    if stable_end - stable_start < min_stable_seconds:
        return None
    available = stable_end - stable_start
    duration = min(clip_seconds, available)
    start = stable_start + max(0.0, (available - duration) * 0.5)
    start = max(0.0, min(start, max(0.0, audio_seconds - duration)))
    if duration <= 0.0:
        return None
    return start, duration


def collect_candidates(archive, allowed_expressions, min_note_duration, min_stable_seconds,
                       attack_margin, release_margin, clip_seconds):
    audio_by_track, csv_by_track, xml_by_track = scan_archive(archive)
    candidates = []
    skipped = {}

    def skip(reason):
        skipped[reason] = skipped.get(reason, 0) + 1

    for track_id in sorted(csv_by_track):
        audio_member = audio_by_track.get(track_id)
        if not audio_member:
            skip("missing_audio")
            continue
        audio_data = archive.read(audio_member)
        params = wav_params_from_bytes(audio_data)
        if params["sample_width"] not in (2, 3, 4) or params["frames"] <= 0:
            skip("unsupported_wav")
            continue
        audio_seconds = params["frames"] / float(params["sample_rate"])
        metadata = xml_metadata(archive, xml_by_track.get(track_id))

        for note_index, note in enumerate(read_note_rows(archive, csv_by_track[track_id]), start=1):
            if note["midi"] < BASS_RANGE[0] or note["midi"] > BASS_RANGE[1]:
                skip("outside_bass_range")
                continue
            if note["duration"] < min_note_duration:
                skip("short_note")
                continue
            if allowed_expressions and note["expression"] not in allowed_expressions:
                skip("expression")
                continue
            window = clip_window(
                note,
                audio_seconds,
                min_stable_seconds,
                attack_margin,
                release_margin,
                clip_seconds,
            )
            if not window:
                skip("no_stable_window")
                continue
            clip_start, clip_duration = window
            candidate_id = (
                f"idmt_bass_lines_{track_id}_{note_index:03d}_"
                f"{note_name(note['midi'])}_{note['pluck']}_{note['expression']}"
            )
            candidates.append({
                "id": sanitize_id(candidate_id),
                "family": "bass",
                "nsynth_family": "bass",
                "source": f"idmt-bass-lines-{note['pluck'].lower()}-{note['expression'].lower()}",
                "midi": note["midi"],
                "note": note_name(note["midi"]),
                "path": str(Path("audio") / f"{sanitize_id(candidate_id)}.wav"),
                "qualities": (
                    f"track={track_id},string={note['string']},fret={note['fret']},"
                    f"pluck={note['pluck']},expression={note['expression']},"
                    f"duration={note['duration']:.3f},model={metadata.get('model', '')},"
                    f"pickup={metadata.get('pickup', '')},{FIXTURE_VERSION}"
                ),
                "audio_member": audio_member,
                "clip_start": clip_start,
                "clip_duration": clip_duration,
                "track_id": track_id,
                "onset": note["onset"],
            })
    candidates.sort(key=lambda row: (row["midi"], row["track_id"], row["onset"], row["id"]))
    return candidates, skipped


def limit_balanced(candidates, limit):
    if limit <= 0 or len(candidates) <= limit:
        return candidates
    buckets = {}
    for row in candidates:
        buckets.setdefault(row["midi"], []).append(row)
    for rows in buckets.values():
        rows.sort(key=lambda row: (row["track_id"], row["onset"], row["id"]))

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
    selected.sort(key=lambda row: (row["track_id"], row["onset"], row["id"]))
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


def prepare_samples(archive_path, output_dir, limit=0, min_samples=120, allowed_expressions="NO",
                    min_note_duration=0.18, min_stable_seconds=0.12, attack_margin=0.03,
                    release_margin=0.02, clip_seconds=0.72, refresh=False):
    output_dir = Path(output_dir)
    manifest_path = output_dir / "manifest.tsv"
    min_samples = max(0, int(min_samples))
    if not refresh and manifest_complete(manifest_path, min_samples):
        print(f"prepare_idmt_bass_lines_samples: keeping existing {manifest_path}")
        return

    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise SystemExit(f"prepare_idmt_bass_lines_samples: missing archive: {archive_path}")

    expressions = split_csv_set(allowed_expressions or "")
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        candidates, skipped = collect_candidates(
            archive,
            expressions,
            min_note_duration,
            min_stable_seconds,
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
                    audio_cache[row["audio_member"]] = audio_data
                if not extract_clip(audio_data, output_path, row["clip_start"], row["clip_duration"]):
                    skipped["clip_failed"] = skipped.get("clip_failed", 0) + 1
                    continue
            prepared.append(row)

    required_prepared = max(1, min_samples)
    if len(prepared) < required_prepared:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, prepared)
        print(f"prepare_idmt_bass_lines_samples: wrote {len(prepared)} rows to {partial_path}", file=sys.stderr)
        raise SystemExit(
            f"prepare_idmt_bass_lines_samples: expected at least {required_prepared} prepared samples, "
            f"got {len(prepared)}"
        )

    write_manifest(manifest_path, prepared)
    midi_counts = {}
    pluck_counts = {}
    for row in prepared:
        midi_counts[row["midi"]] = midi_counts.get(row["midi"], 0) + 1
        source = row["source"].split("-")[-2]
        pluck_counts[source] = pluck_counts.get(source, 0) + 1
    note_span = ""
    if midi_counts:
        note_span = f", range {note_name(min(midi_counts))}-{note_name(max(midi_counts))}"
    pluck_text = " ".join(f"{name}={pluck_counts[name]}" for name in sorted(pluck_counts))
    skipped_text = " ".join(f"{name}={skipped[name]}" for name in sorted(skipped))
    print(
        f"prepare_idmt_bass_lines_samples: wrote {len(prepared)} rows to {manifest_path} "
        f"(bass={len(prepared)}{note_span}, unique_notes={len(midi_counts)}, "
        f"{pluck_text}, skipped {skipped_text})"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare IDMT-SMT-Bass-Single-Track note fixtures.")
    parser.add_argument("--archive", default=os.environ.get(
        "IDMT_BASS_LINES_ARCHIVE",
        "build/real_sample_sources/idmt_bass_lines/IDMT-SMT-BASS-SINGLE-TRACKS.zip"))
    parser.add_argument("--output", default=os.environ.get(
        "IDMT_BASS_LINES_SAMPLE_DIR",
        "build/idmt_bass_lines_samples"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("IDMT_BASS_LINES_SAMPLE_LIMIT", "0")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("IDMT_BASS_LINES_MIN_BASS", "120")))
    parser.add_argument("--expressions", default=os.environ.get("IDMT_BASS_LINES_EXPRESSIONS", "NO"))
    parser.add_argument("--min-note-duration", type=float, default=float(os.environ.get(
        "IDMT_BASS_LINES_MIN_NOTE_DURATION", "0.18")))
    parser.add_argument("--min-stable-seconds", type=float, default=float(os.environ.get(
        "IDMT_BASS_LINES_MIN_STABLE_SECONDS", "0.12")))
    parser.add_argument("--attack-margin", type=float, default=float(os.environ.get(
        "IDMT_BASS_LINES_ATTACK_MARGIN", "0.03")))
    parser.add_argument("--release-margin", type=float, default=float(os.environ.get(
        "IDMT_BASS_LINES_RELEASE_MARGIN", "0.02")))
    parser.add_argument("--clip-seconds", type=float, default=float(os.environ.get(
        "IDMT_BASS_LINES_CLIP_SECONDS", "0.72")))
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("IDMT_BASS_LINES_REFRESH") == "1")
    args = parser.parse_args(argv)

    prepare_samples(
        args.archive,
        args.output,
        limit=args.limit,
        min_samples=args.min_samples,
        allowed_expressions=args.expressions,
        min_note_duration=args.min_note_duration,
        min_stable_seconds=args.min_stable_seconds,
        attack_margin=args.attack_margin,
        release_margin=args.release_margin,
        clip_seconds=args.clip_seconds,
        refresh=args.refresh,
    )


if __name__ == "__main__":
    main()
