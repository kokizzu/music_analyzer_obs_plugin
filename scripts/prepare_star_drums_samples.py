#!/usr/bin/env python3

import argparse
import csv
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile


FIXTURE_VERSION = "star-drums-preview-egmd-shaped-v1"
DIVISION = 480
TEMPO_US_PER_QUARTER = 500000

CLASS_TO_GM = {
    "BD": 36,
    "SD": 38,
    "SS": 37,
    "CHH": 42,
    "PHH": 44,
    "OHH": 46,
    "CRC": 49,
    "SPC": 49,
    "CHC": 49,
    "RD": 51,
    "HT": 50,
    "MT": 47,
    "LT": 43,
}


def sanitize(text, limit=120):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def var_len(value):
    value = max(0, int(value))
    buffer = [value & 0x7F]
    value >>= 7
    while value:
        buffer.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(buffer)


def write_midi(path, hits):
    events = [(0, 0, bytes([0xFF, 0x51, 0x03, 0x07, 0xA1, 0x20]))]
    for seconds, midi, velocity in hits:
        tick = int(round(seconds * 1000000.0 / TEMPO_US_PER_QUARTER * DIVISION))
        events.append((tick, 1, bytes([0x99, midi, max(1, min(127, velocity))])))
        events.append((tick + 24, 2, bytes([0x89, midi, 0])))
    events.sort(key=lambda item: (item[0], item[1], item[2]))

    track = bytearray()
    previous_tick = 0
    for tick, _order, payload in events:
        track.extend(var_len(tick - previous_tick))
        track.extend(payload)
        previous_tick = tick
    track.extend(var_len(0))
    track.extend(b"\xFF\x2F\x00")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as file:
        file.write(b"MThd")
        file.write((6).to_bytes(4, "big"))
        file.write((0).to_bytes(2, "big"))
        file.write((1).to_bytes(2, "big"))
        file.write(DIVISION.to_bytes(2, "big"))
        file.write(b"MTrk")
        file.write(len(track).to_bytes(4, "big"))
        file.write(track)


def parse_annotation(text):
    hits = []
    skipped = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            seconds = float(parts[0])
            velocity = int(round(float(parts[2])))
        except ValueError:
            continue
        label = parts[1].strip().upper()
        midi = CLASS_TO_GM.get(label)
        if midi is None:
            skipped[label] = skipped.get(label, 0) + 1
            continue
        hits.append((seconds, midi, velocity))
    hits.sort(key=lambda item: (item[0], item[1]))
    return hits, skipped


def annotation_members(names):
    return sorted(
        name for name in names
        if "/annotation/" in name and name.endswith(".txt")
    )


def split_root_and_stem(annotation_member):
    marker = "/annotation/"
    before, after = annotation_member.rsplit(marker, 1)
    return before, Path(after).stem


def audio_stem_for(annotation_stem, flavor):
    if flavor == "mix":
        return annotation_stem
    if "_mix_" in annotation_stem:
        prefix, kit = annotation_stem.split("_mix_", 1)
        if flavor == "re_synthesized_drum":
            return prefix + "_re_synth_drum_" + kit
        if flavor == "original_drum":
            return prefix + "_original_drum"
    return annotation_stem


def find_audio_member(names, annotation_member, flavor):
    split_root, annotation_stem = split_root_and_stem(annotation_member)
    stem = audio_stem_for(annotation_stem, flavor)
    audio_root = split_root + "/audio/" + flavor + "/"
    candidates = [
        audio_root + stem + ".flac",
        audio_root + stem + ".wav",
    ]
    name_set = set(names)
    for candidate in candidates:
        if candidate in name_set:
            return candidate
    return ""


def extract_member(zip_file, member, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zip_file.open(member) as source, path.open("wb") as dest:
        shutil.copyfileobj(source, dest)


def write_wav_from_audio(zip_file, member, path, ffmpeg):
    if member.lower().endswith(".wav"):
        extract_member(zip_file, member, path)
        return

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / Path(member).name
        extract_member(zip_file, member, source)
        path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            ffmpeg,
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            str(path),
        ]
        subprocess.run(command, check=True)


def write_metadata(output, rows):
    metadata = output / "e-gmd-v1.0.0.csv"
    tmp = metadata.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=("id", "audio_filename", "midi_filename"))
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(metadata)
    return metadata


def signature_text(args):
    archive = Path(args.archive)
    stamp = ""
    if archive.is_file():
        stat = archive.stat()
        stamp = f"{stat.st_size}:{int(stat.st_mtime)}"
    return "|".join([
        FIXTURE_VERSION,
        f"archive={archive}",
        f"stamp={stamp}",
        f"flavor={args.audio_flavor}",
        f"limit={args.limit}",
    ])


def cached_manifest_ok(output, signature, min_recordings):
    signature_path = output / ".star_drums_signature"
    metadata = output / "e-gmd-v1.0.0.csv"
    if not signature_path.is_file() or not metadata.is_file():
        return False
    if signature_path.read_text(encoding="utf-8") != signature:
        return False
    rows = list(csv.DictReader(metadata.open("r", encoding="utf-8")))
    if len(rows) < min_recordings:
        return False
    for row in rows:
        if not (output / row["audio_filename"]).is_file():
            return False
        if not (output / row["midi_filename"]).is_file():
            return False
    return True


def reset_output(output):
    """Clear generated fixture contents while preserving a build-store symlink."""
    if output.is_symlink():
        target = output.resolve(strict=True)
        if not target.is_dir():
            raise SystemExit(
                f"prepare_star_drums_samples: output symlink target is not a directory: {target}"
            )
        for child in target.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
        return
    if output.exists():
        shutil.rmtree(output)


def prepare(args):
    archive = Path(args.archive)
    if not archive.is_file():
        raise SystemExit(f"prepare_star_drums_samples: missing archive {archive}")

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    signature = signature_text(args)
    if not args.refresh and cached_manifest_ok(output, signature, max(1, args.min_recordings)):
        rows = list(csv.DictReader((output / "e-gmd-v1.0.0.csv").open("r", encoding="utf-8")))
        print(f"prepare_star_drums_samples: reused {output / 'e-gmd-v1.0.0.csv'} ({len(rows)} recordings)")
        return len(rows)

    reset_output(output)
    (output / "audio").mkdir(parents=True, exist_ok=True)
    (output / "midi").mkdir(parents=True, exist_ok=True)

    rows = []
    skipped_labels = {}
    missing_audio = 0
    with zipfile.ZipFile(archive) as zip_file:
        names = zip_file.namelist()
        members = annotation_members(names)
        if args.limit > 0:
            members = members[:args.limit]
        for member in members:
            audio_member = find_audio_member(names, member, args.audio_flavor)
            if not audio_member:
                missing_audio += 1
                continue
            annotation_text = zip_file.read(member).decode("utf-8", errors="replace")
            hits, skipped = parse_annotation(annotation_text)
            if not hits:
                continue
            for label, count in skipped.items():
                skipped_labels[label] = skipped_labels.get(label, 0) + count

            split_root, annotation_stem = split_root_and_stem(member)
            split_name = split_root.split("/data/", 1)[-1].replace("/", "_")
            track_id = sanitize(f"{split_name}_{annotation_stem}_{args.audio_flavor}")
            audio_relative = Path("audio") / f"{track_id}.wav"
            midi_relative = Path("midi") / f"{track_id}.mid"
            write_wav_from_audio(zip_file, audio_member, output / audio_relative, args.ffmpeg)
            write_midi(output / midi_relative, hits)
            rows.append({
                "id": track_id,
                "audio_filename": str(audio_relative),
                "midi_filename": str(midi_relative),
            })

    if len(rows) < args.min_recordings:
        raise SystemExit(
            f"prepare_star_drums_samples: expected at least {args.min_recordings} recordings, got {len(rows)}"
        )

    metadata = write_metadata(output, rows)
    (output / ".star_drums_signature").write_text(signature, encoding="utf-8")
    skipped_text = " ".join(f"{label}={count}" for label, count in sorted(skipped_labels.items()))
    print(
        f"prepare_star_drums_samples: wrote {metadata} ({len(rows)} recordings; "
        f"missing_audio {missing_audio}; skipped {skipped_text or 'none'})",
        flush=True,
    )
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Prepare STAR Drums preview as an E-GMD-shaped fixture.")
    parser.add_argument("--archive", default=os.environ.get("STAR_DRUMS_ARCHIVE",
                                                           "build/real_sample_sources/star_drums/STAR_Drums_preview.zip"))
    parser.add_argument("--output", default=os.environ.get("STAR_DRUMS_SAMPLE_DIR",
                                                          "build/star_drums_preview_samples"))
    parser.add_argument("--audio-flavor", choices=("mix", "re_synthesized_drum", "original_drum"),
                        default=os.environ.get("STAR_DRUMS_AUDIO_FLAVOR", "mix"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("STAR_DRUMS_RECORDING_LIMIT", "0")))
    parser.add_argument("--min-recordings", type=int,
                        default=int(os.environ.get("STAR_DRUMS_MIN_RECORDINGS", "4")))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("STAR_DRUMS_REFRESH") == "1")
    args = parser.parse_args()
    args.limit = max(0, args.limit)
    args.min_recordings = max(1, args.min_recordings)
    prepare(args)


if __name__ == "__main__":
    main()
