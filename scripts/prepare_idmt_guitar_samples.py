#!/usr/bin/env python3

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import prepare_guitar_techs_samples as guitar_helpers


FIXTURE_VERSION = "idmt-smt-guitar-v1"
GUITAR_RANGE = (40, 88)
DEAD_EXPRESSIONS = {"DN", "DEAD", "DEADNOTE", "DEADNOTES", "DEAD-NOTES"}


def run(command):
    subprocess.run(command, check=True)


def find_command(name):
    path = shutil.which(name) if os.path.sep not in name else name
    if not path:
        raise SystemExit(f"prepare_idmt_guitar_samples: missing required tool `{name}`")
    return path


def normalize_tag(tag):
    if "}" in tag:
        tag = tag.rsplit("}", 1)[1]
    return re.sub(r"[^a-z0-9]+", "", tag.lower())


def child_text(element, *names):
    wanted = {normalize_tag(name) for name in names}
    for child in list(element):
        if normalize_tag(child.tag) in wanted:
            return (child.text or "").strip()
    return ""


def first_text(root, *names):
    wanted = {normalize_tag(name) for name in names}
    for element in root.iter():
        if normalize_tag(element.tag) in wanted:
            return (element.text or "").strip()
    return ""


def parse_float(text):
    try:
        return float(str(text).strip())
    except (TypeError, ValueError):
        return None


def parse_int(text):
    try:
        return int(round(float(str(text).strip())))
    except (TypeError, ValueError):
        return None


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def sanitize(text, limit=110):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def split_csv_set(text):
    return {item.strip().upper() for item in str(text).split(",") if item.strip()}


def archive_id(path):
    return sanitize(Path(path).stem)


def cache_member(zip_path, member, cache_dir):
    digest = hashlib.sha256(f"{zip_path}:{member}".encode("utf-8")).hexdigest()[:12]
    suffix = Path(member).suffix or ".bin"
    output = cache_dir / archive_id(zip_path) / f"{sanitize(member, 130)}-{digest}{suffix}"
    if output.is_file() and output.stat().st_size > 0:
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open(member) as source:
            tmp.write_bytes(source.read())
    tmp.replace(output)
    return output


def parse_xml_annotation(data):
    root = ET.fromstring(data)
    audio_file = first_text(root, "audioFileName", "audio_file_name", "audio")
    metadata = {
        "instrument": first_text(root, "instrument"),
        "model": first_text(root, "instrumentModel"),
        "pickup": first_text(root, "pickUpSetting"),
        "tuning": first_text(root, "instrumentTuning"),
    }
    notes = []
    for event in root.iter():
        if normalize_tag(event.tag) != "event":
            continue
        onset = parse_float(child_text(event, "onsetSec", "onset", "onset_seconds"))
        offset = parse_float(child_text(event, "offsetSec", "offset", "offset_seconds"))
        midi = parse_int(child_text(event, "pitch", "midi", "midiPitch"))
        if onset is None or offset is None or midi is None or offset <= onset:
            continue
        notes.append({
            "onset": onset,
            "offset": offset,
            "duration": offset - onset,
            "midi": midi,
            "pluck": child_text(event, "excitationStyle", "pluckingStyle", "pluck").upper() or "NA",
            "expression": child_text(event, "expressionStyle", "expression").upper() or "NA",
            "string": child_text(event, "stringNumber", "string") or "NA",
            "fret": child_text(event, "fretNumber", "fret") or "NA",
        })
    notes.sort(key=lambda note: (note["onset"], note["midi"], note["offset"]))
    return audio_file, metadata, notes


def scan_archive(zip_path):
    with zipfile.ZipFile(zip_path) as archive:
        members = [member for member in archive.namelist() if not member.endswith("/")]
    audio_members = [
        member for member in members
        if member.lower().endswith(".wav") and not member.startswith("__MACOSX/")
    ]
    xml_members = [
        member for member in members
        if member.lower().endswith(".xml") and not member.startswith("__MACOSX/")
    ]

    audio_by_name = {Path(member).name.lower(): member for member in audio_members}
    audio_by_stem = {Path(member).stem.lower(): member for member in audio_members}
    pairs = []
    with zipfile.ZipFile(zip_path) as archive:
        for xml_member in sorted(xml_members):
            try:
                audio_file, metadata, notes = parse_xml_annotation(archive.read(xml_member))
            except ET.ParseError as exc:
                pairs.append({"xml_member": xml_member, "error": f"bad XML: {exc}"})
                continue
            if not notes:
                pairs.append({"xml_member": xml_member, "error": "no usable note events"})
                continue
            audio_member = ""
            if audio_file:
                audio_member = audio_by_name.get(Path(audio_file).name.lower(), "")
            if not audio_member:
                audio_member = audio_by_stem.get(Path(xml_member).stem.lower(), "")
            if not audio_member:
                pairs.append({"xml_member": xml_member, "error": "missing matching WAV"})
                continue
            pairs.append({
                "xml_member": xml_member,
                "audio_member": audio_member,
                "metadata": metadata,
                "notes": notes,
            })
    return pairs


def active_note_count(notes, time_seconds):
    count = 0
    for note in notes:
        if note["onset"] <= time_seconds <= note["offset"]:
            count += 1
    return count


def stable_clip_window(note, min_stable_seconds, attack_margin, release_margin, clip_seconds):
    stable_start = note["onset"] + attack_margin
    stable_end = note["offset"] - release_margin
    if stable_end - stable_start < min_stable_seconds:
        return None
    available = stable_end - stable_start
    duration = min(clip_seconds, available)
    start = stable_start + max(0.0, (available - duration) * 0.5)
    return start, duration


def convert_clip(ffmpeg, audio_path, output_path, start, duration):
    if output_path.is_file() and output_path.stat().st_size > 0:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        run([
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
            "-sample_fmt",
            "s16",
            "-f",
            "wav",
            str(tmp),
        ])
        tmp.replace(output_path)
    finally:
        if tmp.exists():
            tmp.unlink()


def balanced_limit(candidates, limit):
    if limit <= 0 or len(candidates) <= limit:
        return candidates
    buckets = {}
    for row in candidates:
        key = (row["midi"], row["expression"], row["pluck"])
        buckets.setdefault(key, []).append(row)
    for rows in buckets.values():
        rows.sort(key=lambda row: (row["xml_member"], row["note_index"], row["id"]))
    selected = []
    keys = sorted(buckets)
    index = 0
    while len(selected) < limit:
        progressed = False
        for key in keys:
            rows = buckets[key]
            if index < len(rows):
                selected.append(rows[index])
                progressed = True
                if len(selected) >= limit:
                    break
        if not progressed:
            break
        index += 1
    selected.sort(key=lambda row: (row["xml_member"], row["note_index"], row["id"]))
    return selected


def signature_text(archive_path, args):
    path = Path(archive_path)
    stat = path.stat() if path.is_file() else None
    archive_bits = f"{path.name}:{stat.st_size}:{int(stat.st_mtime)}" if stat else str(path)
    payload = "|".join([
        FIXTURE_VERSION,
        archive_bits,
        f"limit={args.limit}",
        f"expressions={args.expressions}",
        f"min_note_duration={args.min_note_duration:.3f}",
        f"min_stable={args.min_stable_seconds:.3f}",
        f"attack={args.attack_margin:.3f}",
        f"release={args.release_margin:.3f}",
        f"clip={args.clip_seconds:.3f}",
        f"pitch={0 if args.skip_pitch_check else 1}",
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def manifest_complete(path, signature, min_rows):
    if not path.is_file():
        return False
    root = path.parent
    rows = 0
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header != ["id", "family", "nsynth_family", "source", "midi", "note", "path", "signature"]:
            return False
        for line in file:
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 8 or fields[7] != signature:
                return False
            if not (root / fields[6]).is_file():
                return False
            rows += 1
    return rows >= max(1, min_rows)


def write_manifest(path, rows, signature):
    with path.open("w", encoding="utf-8") as file:
        file.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tsignature\n")
        for row in rows:
            file.write(
                "\t".join([
                    row["id"],
                    "guitar",
                    "idmt_smt_guitar",
                    row["source"],
                    str(row["midi"]),
                    row["note"],
                    row["path"],
                    signature,
                ]) + "\n"
            )


def collect_candidates(zip_path, args):
    allowed_expressions = split_csv_set(args.expressions)
    candidates = []
    skipped = {}

    def skip(reason):
        skipped[reason] = skipped.get(reason, 0) + 1

    for pair in scan_archive(zip_path):
        if pair.get("error"):
            skip(pair["error"])
            continue
        for note_index, note in enumerate(pair["notes"], start=1):
            if note["midi"] < GUITAR_RANGE[0] or note["midi"] > GUITAR_RANGE[1]:
                skip("outside_guitar_range")
                continue
            expression = note["expression"]
            if expression in DEAD_EXPRESSIONS:
                skip("dead_note")
                continue
            if allowed_expressions and expression not in allowed_expressions:
                skip("expression")
                continue
            if note["duration"] < args.min_note_duration:
                skip("short_note")
                continue
            center = note["onset"] + note["duration"] * 0.5
            if active_note_count(pair["notes"], center) != 1:
                skip("polyphonic_overlap")
                continue
            window = stable_clip_window(
                note,
                args.min_stable_seconds,
                args.attack_margin,
                args.release_margin,
                args.clip_seconds,
            )
            if not window:
                skip("no_stable_window")
                continue
            label = note_name(note["midi"])
            xml_stem = sanitize(Path(pair["xml_member"]).stem)
            row_id = sanitize(
                f"idmt_guitar_{xml_stem}_{note_index:04d}_{label}_{note['pluck']}_{expression}"
            )
            source = sanitize(
                f"idmt-smt-guitar-{note['pluck'].lower()}-{expression.lower()}",
                limit=70,
            )
            candidates.append({
                "id": row_id,
                "source": source,
                "midi": note["midi"],
                "note": label,
                "path": str(Path("audio") / f"{row_id}.wav"),
                "audio_member": pair["audio_member"],
                "xml_member": pair["xml_member"],
                "clip_start": window[0],
                "clip_duration": window[1],
                "note_index": note_index,
                "expression": expression,
                "pluck": note["pluck"],
                "metadata": pair["metadata"],
            })
    candidates.sort(key=lambda row: (row["midi"], row["expression"], row["xml_member"], row["note_index"]))
    return candidates, skipped


def prepare(args):
    ffmpeg = find_command(args.ffmpeg)
    archive_path = Path(args.archive)
    if not archive_path.is_file():
        raise SystemExit(f"prepare_idmt_guitar_samples: missing archive {archive_path}")
    output_dir = Path(args.output)
    cache_dir = Path(args.cache_dir) if args.cache_dir else output_dir / "_cache"
    signature = signature_text(archive_path, args)
    manifest_path = output_dir / "manifest.tsv"
    min_samples = max(0, args.min_samples)
    if not args.refresh and manifest_complete(manifest_path, signature, min_samples):
        print(f"prepare_idmt_guitar_samples: keeping existing {manifest_path}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    candidates, skipped = collect_candidates(archive_path, args)
    selected = balanced_limit(candidates, args.limit)

    rows = []
    skipped_errors = []
    audio_cache = {}
    for row in selected:
        try:
            audio_member = row["audio_member"]
            if audio_member not in audio_cache:
                audio_cache[audio_member] = cache_member(archive_path, audio_member, cache_dir)
            output_path = output_dir / row["path"]
            convert_clip(ffmpeg, audio_cache[audio_member], output_path, row["clip_start"], row["clip_duration"])
            if not args.skip_pitch_check and not guitar_helpers.pitch_reference_ok(output_path, row["midi"]):
                skipped["pitch_reference"] = skipped.get("pitch_reference", 0) + 1
                continue
        except (OSError, subprocess.CalledProcessError) as exc:
            skipped_errors.append((row["id"], str(exc)))
            continue
        rows.append(row)

    required = max(1, min_samples)
    if len(rows) < required:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, rows, signature)
        raise SystemExit(
            f"prepare_idmt_guitar_samples: expected at least {required} prepared samples, "
            f"got {len(rows)}; wrote partial manifest {partial_path}"
        )

    write_manifest(manifest_path, rows, signature)
    if rows:
        low_midi = min(row["midi"] for row in rows)
        high_midi = max(row["midi"] for row in rows)
        range_text = f"{note_name(low_midi)}-{note_name(high_midi)}"
    else:
        range_text = "--"
    print(
        f"prepare_idmt_guitar_samples: wrote {len(rows)} rows to {manifest_path} "
        f"(candidates {len(candidates)}, range {range_text}, skipped "
        + " ".join(f"{key}={value}" for key, value in sorted(skipped.items()))
        + f", errors {len(skipped_errors)})"
    )
    for sample_id, reason in skipped_errors[:12]:
        print(f"prepare_idmt_guitar_samples: skipped {sample_id}: {reason}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare IDMT-SMT-Guitar XML/WAV notes as analyzer real-note samples."
    )
    parser.add_argument("--archive", default=os.environ.get("IDMT_GUITAR_ARCHIVE",
                                                           "build/real_sample_sources/idmt_guitar/IDMT-SMT-GUITAR_V2.zip"))
    parser.add_argument("--output", default=os.environ.get("IDMT_GUITAR_SAMPLE_DIR",
                                                          "build/idmt_guitar_samples"))
    parser.add_argument("--cache-dir", default=os.environ.get("IDMT_GUITAR_CACHE_DIR", ""))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("IDMT_GUITAR_SAMPLE_LIMIT", "0")))
    parser.add_argument("--min-samples", type=int,
                        default=int(os.environ.get("IDMT_GUITAR_MIN_GUITAR", "200")))
    parser.add_argument("--expressions", default=os.environ.get("IDMT_GUITAR_EXPRESSIONS", ""))
    parser.add_argument("--min-note-duration", type=float,
                        default=float(os.environ.get("IDMT_GUITAR_MIN_NOTE_DURATION", "0.18")))
    parser.add_argument("--min-stable-seconds", type=float,
                        default=float(os.environ.get("IDMT_GUITAR_MIN_STABLE_SECONDS", "0.12")))
    parser.add_argument("--attack-margin", type=float,
                        default=float(os.environ.get("IDMT_GUITAR_ATTACK_MARGIN", "0.04")))
    parser.add_argument("--release-margin", type=float,
                        default=float(os.environ.get("IDMT_GUITAR_RELEASE_MARGIN", "0.03")))
    parser.add_argument("--clip-seconds", type=float,
                        default=float(os.environ.get("IDMT_GUITAR_CLIP_SECONDS", "0.80")))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    parser.add_argument("--skip-pitch-check", action="store_true",
                        default=os.environ.get("IDMT_GUITAR_SKIP_PITCH_CHECK") == "1")
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("IDMT_GUITAR_REFRESH") == "1")
    args = parser.parse_args(argv)
    prepare(args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"prepare_idmt_guitar_samples: command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(exc.returncode)
