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


FIXTURE_VERSION = "vocadito-v1"
DEFAULT_ANNOTATOR = "A1"
SUPPORTED_ANNOTATORS = {"A1", "A2", "both"}
NOTE_RE = re.compile(r"^Annotations/Notes/vocadito_(\d+)_notes(A[12])\.csv$")
AUDIO_RE = re.compile(r"^Audio/vocadito_(\d+)\.wav$")
MIDI_RANGE = (40, 84)


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def midi_frequency(midi):
    return 440.0 * math.pow(2.0, (midi - 69) / 12.0)


def frequency_to_midi(freq):
    midi = int(round(69.0 + 12.0 * math.log2(freq / 440.0)))
    cents = 1200.0 * math.log2(freq / midi_frequency(midi))
    return midi, cents


def sanitize_id(text):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")


def read_metadata(archive):
    metadata = {}
    try:
        with archive.open("vocadito_metadata.csv") as source:
            wrapper = io.TextIOWrapper(source, encoding="utf-8", newline="")
            for row in csv.DictReader(wrapper):
                metadata[str(row.get("track_id", "")).strip()] = {
                    "singer": str(row.get("singer_id", "")).strip(),
                    "average_pitch": str(row.get("average_pitch", "")).strip(),
                    "language": str(row.get("language", "")).strip(),
                }
    except KeyError:
        pass
    return metadata


def read_note_rows(archive, member):
    rows = []
    with archive.open(member) as source:
        wrapper = io.TextIOWrapper(source, encoding="utf-8", newline="")
        for index, row in enumerate(csv.reader(wrapper), start=1):
            if len(row) < 3:
                continue
            try:
                start = float(row[0])
                freq = float(row[1])
                duration = float(row[2])
            except ValueError as exc:
                raise SystemExit(f"prepare_vocadito_samples: bad note row {member}:{index}: {row}") from exc
            if freq > 0.0 and duration > 0.0:
                rows.append({
                    "start": start,
                    "freq": freq,
                    "duration": duration,
                })
    return rows


def scan_archive(archive, annotator):
    audio_by_track = {}
    notes_by_track = {}
    for member in archive.namelist():
        if member.startswith("__MACOSX/") or "/._" in member:
            continue
        audio_match = AUDIO_RE.match(member)
        if audio_match:
            audio_by_track[audio_match.group(1)] = member
            continue
        note_match = NOTE_RE.match(member)
        if note_match:
            track_id, note_annotator = note_match.groups()
            if annotator == "both" or annotator == note_annotator:
                notes_by_track.setdefault(track_id, {})[note_annotator] = member
    return audio_by_track, notes_by_track


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


def candidate_clip_window(note, audio_seconds, min_duration, attack_margin, release_margin, clip_seconds):
    stable_start = note["start"] + attack_margin
    stable_end = note["start"] + note["duration"] - release_margin
    if stable_end - stable_start < min_duration:
        return None

    available = stable_end - stable_start
    duration = min(clip_seconds, available)
    start = stable_start + max(0.0, (available - duration) * 0.5)
    start = max(0.0, min(start, max(0.0, audio_seconds - duration)))
    if duration <= 0.0 or start >= audio_seconds:
        return None
    return start, duration


def collect_candidates(archive, annotator, min_note_duration, max_cents, attack_margin,
                       release_margin, clip_seconds):
    metadata = read_metadata(archive)
    audio_by_track, notes_by_track = scan_archive(archive, annotator)
    candidates = []
    skipped = {}

    def skip(reason):
        skipped[reason] = skipped.get(reason, 0) + 1

    for track_id in sorted(notes_by_track, key=lambda value: int(value)):
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
        track_metadata = metadata.get(track_id, {})
        annotator_members = notes_by_track[track_id]
        for note_annotator in sorted(annotator_members):
            note_rows = read_note_rows(archive, annotator_members[note_annotator])
            for note_index, note in enumerate(note_rows, start=1):
                if note["duration"] < min_note_duration:
                    skip("short_note")
                    continue
                try:
                    midi, cents = frequency_to_midi(note["freq"])
                except ValueError:
                    skip("bad_frequency")
                    continue
                if midi < MIDI_RANGE[0] or midi > MIDI_RANGE[1]:
                    skip("outside_vocal_range")
                    continue
                if abs(cents) > max_cents:
                    skip("off_chromatic")
                    continue
                window = candidate_clip_window(
                    note,
                    audio_seconds,
                    min_note_duration,
                    attack_margin,
                    release_margin,
                    clip_seconds,
                )
                if not window:
                    skip("no_stable_window")
                    continue
                start, duration = window
                source = (
                    f"vocadito-{track_metadata.get('singer', 'unknown')}-"
                    f"{track_metadata.get('language', 'unknown')}-{note_annotator}"
                )
                candidate_id = (
                    f"vocadito_{int(track_id):02d}_{note_annotator}_"
                    f"{note_index:03d}_{note_name(midi)}"
                )
                candidates.append({
                    "id": sanitize_id(candidate_id),
                    "track_id": track_id,
                    "annotator": note_annotator,
                    "family": "vocals",
                    "nsynth_family": "vocal",
                    "source": sanitize_id(source.lower()),
                    "midi": midi,
                    "note": note_name(midi),
                    "path": str(Path("audio") / f"{sanitize_id(candidate_id)}.wav"),
                    "qualities": (
                        f"singer={track_metadata.get('singer', '')},"
                        f"language={track_metadata.get('language', '')},"
                        f"annotator={note_annotator},"
                        f"freq={note['freq']:.3f},cents={cents:.2f},"
                        f"duration={note['duration']:.3f},{FIXTURE_VERSION}"
                    ),
                    "audio_member": audio_member,
                    "clip_start": start,
                    "clip_duration": duration,
                })
    candidates.sort(key=lambda row: (
        row["midi"],
        row["track_id"],
        row["annotator"],
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
        rows.sort(key=lambda row: (row["track_id"], row["annotator"], row["clip_start"], row["id"]))

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
    selected.sort(key=lambda row: (row["track_id"], row["annotator"], row["clip_start"], row["id"]))
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


def prepare_samples(archive_path, output_dir, annotator=DEFAULT_ANNOTATOR, limit=0, min_samples=80,
                    min_note_duration=0.22, max_cents=25.0, attack_margin=0.04,
                    release_margin=0.03, clip_seconds=0.72, refresh=False):
    output_dir = Path(output_dir)
    manifest_path = output_dir / "manifest.tsv"
    min_samples = max(0, int(min_samples))
    if not refresh and manifest_complete(manifest_path, min_samples):
        print(f"prepare_vocadito_samples: keeping existing {manifest_path}")
        return

    if annotator not in SUPPORTED_ANNOTATORS:
        raise SystemExit(f"prepare_vocadito_samples: unsupported annotator `{annotator}`")
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise SystemExit(f"prepare_vocadito_samples: missing archive: {archive_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        candidates, skipped = collect_candidates(
            archive,
            annotator,
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
                    audio_cache[row["audio_member"]] = audio_data
                if not extract_clip(audio_data, output_path, row["clip_start"], row["clip_duration"]):
                    skipped["clip_failed"] = skipped.get("clip_failed", 0) + 1
                    continue
            prepared.append(row)

    required_prepared = max(1, min_samples)
    if len(prepared) < required_prepared:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, prepared)
        print(f"prepare_vocadito_samples: wrote {len(prepared)} rows to {partial_path}", file=sys.stderr)
        raise SystemExit(
            f"prepare_vocadito_samples: expected at least {required_prepared} prepared samples, "
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
        f"prepare_vocadito_samples: wrote {len(prepared)} rows to {manifest_path} "
        f"(vocals={len(prepared)}{note_span}, unique_notes={len(midi_counts)}, skipped {skipped_text})"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare Vocadito real vocal note fixtures.")
    parser.add_argument("--archive", default=os.environ.get(
        "VOCADITO_ARCHIVE",
        "build/real_sample_sources/vocadito/vocadito.zip"))
    parser.add_argument("--output", default=os.environ.get(
        "VOCADITO_SAMPLE_DIR",
        "build/vocadito_samples"))
    parser.add_argument("--annotator", default=os.environ.get(
        "VOCADITO_ANNOTATOR",
        DEFAULT_ANNOTATOR))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("VOCADITO_SAMPLE_LIMIT", "0")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("VOCADITO_MIN_VOCALS", "80")))
    parser.add_argument("--min-note-duration", type=float, default=float(os.environ.get(
        "VOCADITO_MIN_NOTE_DURATION", "0.22")))
    parser.add_argument("--max-cents", type=float, default=float(os.environ.get("VOCADITO_MAX_CENTS", "25")))
    parser.add_argument("--attack-margin", type=float, default=float(os.environ.get(
        "VOCADITO_ATTACK_MARGIN", "0.04")))
    parser.add_argument("--release-margin", type=float, default=float(os.environ.get(
        "VOCADITO_RELEASE_MARGIN", "0.03")))
    parser.add_argument("--clip-seconds", type=float, default=float(os.environ.get(
        "VOCADITO_CLIP_SECONDS", "0.72")))
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("VOCADITO_REFRESH") == "1")
    args = parser.parse_args(argv)

    prepare_samples(
        args.archive,
        args.output,
        annotator=args.annotator,
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
