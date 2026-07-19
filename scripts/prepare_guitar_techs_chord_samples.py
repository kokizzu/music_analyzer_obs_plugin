#!/usr/bin/env python3

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys

import prepare_guitar_techs_samples as single_notes


FIXTURE_VERSION = "guitar-techs-chords-v1"
GUITAR_TECHS_SOURCE = "https://zenodo.org/records/14963133"


def signature_text(archives, perspectives, args):
    archive_bits = []
    for archive in archives:
        path = Path(archive)
        if path.is_file():
            stat = path.stat()
            archive_bits.append(f"{path.name}:{stat.st_size}:{int(stat.st_mtime)}")
        else:
            archive_bits.append(str(path))

    payload = "|".join([
        FIXTURE_VERSION,
        f"limit={args.limit}",
        f"min_notes={args.min_notes}",
        f"min_pitch_classes={args.min_pitch_classes}",
        f"padding={args.padding_seconds:.3f}",
        f"min_clip={args.min_clip_seconds:.3f}",
        f"max_clip={args.max_clip_seconds:.3f}",
        f"min_sep={args.min_separation_seconds:.3f}",
        ",".join(perspectives),
        "|".join(archive_bits),
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def active_notes_at(notes, time_seconds):
    active = []
    for note in notes:
        duration = note["end"] - note["start"]
        edge = min(0.035, duration / 5.0)
        if note["start"] + edge <= time_seconds <= note["end"] - edge:
            active.append(note)
    return active


def pitch_class_signature(notes):
    return ".".join(str(item) for item in sorted({note["midi"] % 12 for note in notes}))


def note_signature(notes):
    return ".".join(str(item["midi"]) for item in sorted(notes, key=lambda note: note["midi"]))


def candidate_windows(notes, args):
    candidates = []
    for note in notes:
        center = note["start"] + (note["end"] - note["start"]) * 0.5
        active = active_notes_at(notes, center)
        pitch_classes = {item["midi"] % 12 for item in active}
        if len(active) < args.min_notes or len(pitch_classes) < args.min_pitch_classes:
            continue

        duplicate = False
        signature = note_signature(active)
        for existing in candidates:
            if abs(existing["center"] - center) < args.min_separation_seconds and existing["signature"] == signature:
                duplicate = True
                break
        if duplicate:
            continue

        chord_start = min(item["start"] for item in active)
        chord_end = max(item["end"] for item in active)
        wanted_duration = max(args.min_clip_seconds, chord_end - chord_start + args.padding_seconds * 2.0)
        duration = min(args.max_clip_seconds, wanted_duration)
        clip_center = (chord_start + chord_end) * 0.5
        clip_start = max(0.0, clip_center - duration * 0.5)
        clip_end = clip_start + duration

        adjusted_notes = []
        for candidate_note in active:
            start = max(candidate_note["start"], clip_start)
            end = min(candidate_note["end"], clip_end)
            if end - start < 0.050:
                continue
            adjusted_notes.append((start - clip_start, end - clip_start, candidate_note["midi"]))

        adjusted_pitch_classes = {midi % 12 for _, _, midi in adjusted_notes}
        if len(adjusted_notes) < args.min_notes or len(adjusted_pitch_classes) < args.min_pitch_classes:
            continue

        candidates.append({
            "center": center,
            "start": clip_start,
            "duration": duration,
            "notes": adjusted_notes,
            "pitch_signature": pitch_class_signature(active),
            "signature": signature,
            "score": len(active) * 100 + len(pitch_classes) * 30 + (chord_end - chord_start),
        })
    return candidates


def spread_candidates(candidates, limit):
    if limit <= 0 or len(candidates) <= limit:
        return candidates

    groups = {}
    for candidate in candidates:
        groups.setdefault(candidate["window"]["pitch_signature"], []).append(candidate)

    selected = []
    keys = sorted(groups)
    index = 0
    while len(selected) < limit:
        added = False
        for key in keys:
            bucket = groups[key]
            if index < len(bucket):
                selected.append(bucket[index])
                added = True
                if len(selected) >= limit:
                    break
        if not added:
            break
        index += 1
    return selected


def convert_clip(ffmpeg, audio_path, output_path, start, duration):
    if output_path.is_file() and output_path.stat().st_size > 0:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        single_notes.run([
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.6f}",
            "-t",
            f"{duration:.6f}",
            "-i",
            str(audio_path),
            "-ac",
            "1",
            "-ar",
            "48000",
            "-f",
            "wav",
            str(tmp),
        ])
        tmp.replace(output_path)
    finally:
        if tmp.exists():
            tmp.unlink()


def manifest_complete(path, signature, min_samples):
    if not path.is_file():
        return False

    rows = 0
    saw_signature = False
    try:
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.rstrip("\n")
                if not line:
                    continue
                if line.startswith("# signature\t"):
                    saw_signature = line.split("\t", 1)[1] == signature
                elif line.startswith("AUDIO\t"):
                    fields = line.split("\t")
                    if len(fields) < 3 or not Path(fields[2]).is_file():
                        return False
                    rows += 1
        return saw_signature and rows >= max(1, min_samples)
    except OSError:
        return False


def write_manifest(path, rows, signature):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        output.write("# Guitar-TECHS chord analyzer manifest v1\n")
        output.write(f"# signature\t{signature}\n")
        output.write(f"# source\t{GUITAR_TECHS_SOURCE}\n")
        for row in rows:
            output.write(f"AUDIO\t{row['id']}\t{row['audio_path']}\n")
            for start, end, midi in row["notes"]:
                output.write(f"NOTE\t{row['id']}\t{start:.6f}\t{end:.6f}\t{midi}\n")


def prepare(args):
    ffmpeg = single_notes.find_command(args.ffmpeg)
    output_dir = Path(args.output)
    cache_dir = Path(args.cache_dir) if args.cache_dir else output_dir / "_cache"
    archives = [Path(path) for path in args.archive]
    for archive in archives:
        if not archive.is_file():
            raise SystemExit(f"prepare_guitar_techs_chord_samples: missing archive {archive}")

    perspectives = single_notes.parse_perspectives(args.perspectives)
    signature = signature_text(archives, perspectives, args)
    manifest_path = output_dir / "manifest.tsv"
    min_samples = max(0, args.min_samples)
    if not args.refresh and manifest_complete(manifest_path, signature, min_samples):
        print(f"prepare_guitar_techs_chord_samples: keeping existing {manifest_path}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    candidate_rows = []
    skipped_sparse = 0
    skipped_errors = []

    for archive in archives:
        try:
            pairs = single_notes.discover_pairs(archive, perspectives)
        except SystemExit as exc:
            skipped_errors.append((str(archive), str(exc)))
            continue

        midi_cache = {}
        for pair in pairs:
            midi_member = pair["midi_member"]
            try:
                if midi_member not in midi_cache:
                    midi_cache[midi_member] = single_notes.cache_member(archive, midi_member, cache_dir)
                notes = single_notes.parse_midi_notes(midi_cache[midi_member])
                windows = candidate_windows(notes, args)
            except (OSError, ValueError) as exc:
                skipped_errors.append((midi_member, str(exc)))
                continue

            if not windows:
                skipped_sparse += 1
                continue
            for index, window in enumerate(windows):
                candidate_rows.append({
                    "archive": archive,
                    "pair": pair,
                    "candidate_index": index,
                    "window": window,
                })

    selected = spread_candidates(candidate_rows, args.limit)
    rows = []
    audio_cache = {}
    for selected_index, item in enumerate(selected, start=1):
        archive = item["archive"]
        pair = item["pair"]
        window = item["window"]
        audio_member = pair["audio_member"]
        try:
            cache_key = (archive, audio_member)
            if cache_key not in audio_cache:
                audio_cache[cache_key] = single_notes.cache_member(archive, audio_member, cache_dir)
            row_id = single_notes.sanitize(
                f"guitar_techs_chords_{single_notes.archive_id(archive)}_{pair['perspective']}_"
                f"{pair['token']}_{item['candidate_index']:04d}_{selected_index:04d}"
            )
            output_path = output_dir / "audio" / f"{row_id}.wav"
            convert_clip(ffmpeg, audio_cache[cache_key], output_path, window["start"], window["duration"])
        except (subprocess.CalledProcessError, OSError) as exc:
            skipped_errors.append((audio_member, str(exc)))
            continue

        rows.append({
            "id": row_id,
            "audio_path": str(output_path.resolve()),
            "notes": window["notes"],
            "source": f"{single_notes.archive_id(archive)}:{pair['perspective']}:{pair['token']}",
        })
        if args.progress_every > 0 and len(rows) % args.progress_every == 0:
            print(
                f"prepare_guitar_techs_chord_samples: prepared {len(rows)} clips "
                f"({selected_index}/{len(selected)} selected)",
                flush=True,
            )

    required = max(1, min_samples)
    if len(rows) < required:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, rows, signature)
        raise SystemExit(
            f"prepare_guitar_techs_chord_samples: expected at least {required} prepared clips, "
            f"got {len(rows)}; wrote partial manifest {partial_path}"
        )

    write_manifest(manifest_path, rows, signature)
    note_count = sum(len(row["notes"]) for row in rows)
    print(
        f"prepare_guitar_techs_chord_samples: wrote {len(rows)} clips and {note_count} notes "
        f"to {manifest_path} (candidate_windows {len(candidate_rows)}; skipped_sparse {skipped_sparse}; "
        f"skipped_errors {len(skipped_errors)})"
    )
    for sample_id, reason in skipped_errors[:12]:
        print(f"prepare_guitar_techs_chord_samples: skipped {sample_id}: {reason}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare Guitar-TECHS chord ZIPs as analyzer_guitarset note/chord fixtures."
    )
    parser.add_argument("--archive", action="append", default=[])
    parser.add_argument("--output", default=os.environ.get("GUITAR_TECHS_CHORD_SAMPLE_DIR",
                                                           "build/guitar_techs_chord_samples"))
    parser.add_argument("--cache-dir", default=os.environ.get("GUITAR_TECHS_CHORD_CACHE_DIR", ""))
    parser.add_argument("--perspectives", default=os.environ.get("GUITAR_TECHS_CHORD_PERSPECTIVES",
                                                                 ",".join(single_notes.DEFAULT_PERSPECTIVES)))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("GUITAR_TECHS_CHORD_SAMPLE_LIMIT", "0")))
    parser.add_argument("--min-samples", type=int,
                        default=int(os.environ.get("GUITAR_TECHS_CHORD_MIN_EXCERPTS", "7000")))
    parser.add_argument("--min-notes", type=int,
                        default=int(os.environ.get("GUITAR_TECHS_CHORD_MIN_NOTES", "3")))
    parser.add_argument("--min-pitch-classes", type=int,
                        default=int(os.environ.get("GUITAR_TECHS_CHORD_MIN_PITCH_CLASSES", "3")))
    parser.add_argument("--padding-seconds", type=float,
                        default=float(os.environ.get("GUITAR_TECHS_CHORD_PADDING_SECONDS", "0.15")))
    parser.add_argument("--min-clip-seconds", type=float,
                        default=float(os.environ.get("GUITAR_TECHS_CHORD_MIN_CLIP_SECONDS", "0.55")))
    parser.add_argument("--max-clip-seconds", type=float,
                        default=float(os.environ.get("GUITAR_TECHS_CHORD_MAX_CLIP_SECONDS", "1.50")))
    parser.add_argument("--min-separation-seconds", type=float,
                        default=float(os.environ.get("GUITAR_TECHS_CHORD_MIN_SEPARATION_SECONDS", "0.18")))
    parser.add_argument("--progress-every", type=int,
                        default=int(os.environ.get("GUITAR_TECHS_CHORD_PROGRESS_EVERY", "25")))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("GUITAR_TECHS_CHORD_REFRESH") == "1")
    args = parser.parse_args(argv)

    if not args.archive:
        raise SystemExit("prepare_guitar_techs_chord_samples: at least one --archive is required")
    prepare(args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"prepare_guitar_techs_chord_samples: command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(exc.returncode)
