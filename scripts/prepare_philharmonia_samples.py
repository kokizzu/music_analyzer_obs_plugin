#!/usr/bin/env python3

import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
import zipfile
from collections import defaultdict
from pathlib import Path


NOTE_RE = re.compile(r"_([A-G](?:s)?[0-8])_")
NOTE_PITCH_CLASS = {
    "C": 0,
    "Cs": 1,
    "D": 2,
    "Ds": 3,
    "E": 4,
    "F": 5,
    "Fs": 6,
    "G": 7,
    "Gs": 8,
    "A": 9,
    "As": 10,
    "B": 11,
}
DISPLAY_NOTE = {
    "C": "C",
    "Cs": "C#",
    "D": "D",
    "Ds": "D#",
    "E": "E",
    "F": "F",
    "Fs": "F#",
    "G": "G",
    "Gs": "G#",
    "A": "A",
    "As": "A#",
    "B": "B",
}
BANNED_TOKENS = {
    "phrase",
    "major-trill",
    "minor-trill",
    "glissando",
    "harmonic",
    "cresc-decresc",
    "scale",
    "run",
}
ARCHIVES = ("Woodwind.zip", "Brass.zip", "Strings.zip")


def note_to_midi(note):
    if note[:2] in NOTE_PITCH_CLASS:
        name = note[:2]
        octave = int(note[2:])
    else:
        name = note[:1]
        octave = int(note[1:])
    return (octave + 1) * 12 + NOTE_PITCH_CLASS[name]


def note_label(note):
    if note[:2] in NOTE_PITCH_CLASS:
        name = note[:2]
        octave = int(note[2:])
    else:
        name = note[:1]
        octave = int(note[1:])
    return f"{DISPLAY_NOTE[name]}{octave}"


def family_for_instrument(instrument):
    normalized = instrument.replace("_", "-").lower()
    if normalized == "double-bass":
        return "bass"
    if normalized in {"banjo", "guitar"}:
        return "guitar"
    return "other"


def parse_candidate(archive_name, member):
    if not member.lower().endswith(".mp3"):
        return None
    if member.lower().endswith(".zip"):
        return None

    basename = Path(member).name
    match = NOTE_RE.search(basename)
    if not match:
        return None

    stem = basename[:-4]
    note = match.group(1)
    prefix = stem[: match.start()]
    rest = stem[match.end() :]
    tokens = rest.split("_")
    if not tokens:
        return None
    if any(token in BANNED_TOKENS for token in tokens):
        return None
    if "phrase" in tokens:
        return None
    if not any(token in {"normal", "staccato", "pizzicato", "arco-normal", "mute"} for token in tokens):
        return None

    parts = member.split("/")
    collection = parts[0] if parts else archive_name.replace(".zip", "")
    folder_instrument = parts[1] if len(parts) > 2 else prefix.replace("-", " ")
    instrument = folder_instrument.replace(" ", "-").lower()
    midi = note_to_midi(note)
    if midi < 21 or midi > 108:
        return None
    if instrument == "banjo" and midi > 84:
        return None

    return {
        "archive": archive_name,
        "member": member,
        "collection": collection,
        "instrument": instrument,
        "family": family_for_instrument(instrument),
        "midi": midi,
        "note": note_label(note),
        "qualities": ",".join(tokens),
    }


def collect_candidates(source_dir):
    grouped = defaultdict(list)
    for archive_name in ARCHIVES:
        archive_path = source_dir / archive_name
        if not archive_path.is_file():
            raise SystemExit(f"missing Philharmonia archive: {archive_path}")
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.namelist():
                candidate = parse_candidate(archive_name, member)
                if not candidate:
                    continue
                grouped[candidate["instrument"]].append(candidate)

    for items in grouped.values():
        items.sort(key=lambda item: (item["midi"], item["qualities"], item["member"]))
    return grouped


def balanced_selection(grouped, limit):
    keys = sorted(grouped)
    selected = []
    index = 0
    while keys and (limit <= 0 or len(selected) < limit):
        next_keys = []
        for key in keys:
            items = grouped[key]
            if index < len(items):
                selected.append(items[index])
                next_keys.append(key)
                if limit > 0 and len(selected) >= limit:
                    break
        keys = next_keys
        index += 1
    return selected


def sanitize_id(candidate):
    name = Path(candidate["member"]).stem
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
    return f"philharmonia_{candidate['collection'].lower()}_{safe}"


def convert_candidate(candidate, source_dir, output_dir, ffmpeg):
    archive_path = source_dir / candidate["archive"]
    rel_path = Path("audio") / f"{sanitize_id(candidate)}.wav"
    output_path = output_dir / rel_path
    if output_path.is_file():
        return rel_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        with archive.open(candidate["member"]) as mp3_file:
            data = mp3_file.read()

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                tmp_path,
                "-ac",
                "1",
                "-ar",
                "48000",
                str(output_path),
            ],
            check=True,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    return rel_path


def midi_frequency(midi):
    return 440.0 * math.pow(2.0, (midi - 69) / 12.0)


def goertzel_level(samples, sample_rate, freq):
    if not samples:
        return 0.0
    coeff = 2.0 * math.cos(2.0 * math.pi * freq / sample_rate)
    s1 = 0.0
    s2 = 0.0
    count = len(samples)
    mean = sum(samples) / count
    for i, sample in enumerate(samples):
        window = 0.5 - 0.5 * math.cos(2.0 * math.pi * i / max(1, count - 1))
        x = (sample - mean) * window
        s0 = x + coeff * s1 - s2
        s2 = s1
        s1 = s0
    return math.sqrt(max(0.0, s1 * s1 + s2 * s2 - coeff * s1 * s2))


def read_probe_window(path):
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        sample_width = wav.getsampwidth()
        frame_count = wav.getnframes()
        if sample_width != 2:
            return sample_rate, []
        start = min(frame_count, int(sample_rate * 0.18))
        count = min(frame_count - start, int(sample_rate * 0.25))
        if count <= 0:
            return sample_rate, []
        wav.setpos(start)
        data = wav.readframes(count)

    samples = []
    step = sample_width * channels
    for offset in range(0, len(data), step):
        total = 0.0
        for channel in range(channels):
            lo = data[offset + channel * sample_width]
            hi = data[offset + channel * sample_width + 1]
            value = int.from_bytes(bytes((lo, hi)), byteorder="little", signed=True)
            total += value / 32768.0
        samples.append(total / channels)
    return sample_rate, samples


def pitch_reference_ok(path, midi):
    sample_rate, samples = read_probe_window(path)
    if not samples:
        return False
    expected = goertzel_level(samples, sample_rate, midi_frequency(midi))
    lower = goertzel_level(samples, sample_rate, midi_frequency(midi - 1)) if midi > 21 else 0.0
    upper = goertzel_level(samples, sample_rate, midi_frequency(midi + 1)) if midi < 108 else 0.0
    adjacent = max(lower, upper)
    if adjacent <= 1.0e-6:
        return True
    return expected >= adjacent * 0.90


def write_manifest(rows, output_dir):
    manifest = output_dir / "manifest.tsv"
    with manifest.open("w", encoding="utf-8") as file:
        file.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities\n")
        for row in rows:
            file.write(
                "\t".join(
                    [
                        row["id"],
                        row["family"],
                        row["collection"].lower(),
                        row["instrument"],
                        str(row["midi"]),
                        row["note"],
                        row["path"],
                        row["qualities"],
                    ]
                )
                + "\n"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=1500)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()

    ffmpeg = shutil.which(args.ffmpeg) if os.path.sep not in args.ffmpeg else args.ffmpeg
    if not ffmpeg:
        raise SystemExit(f"ffmpeg not found: {args.ffmpeg}")

    source_dir = Path(args.source)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    grouped = collect_candidates(source_dir)
    selected = balanced_selection(grouped, args.limit)
    if len(selected) < 1000:
        raise SystemExit(f"only found {len(selected)} usable Philharmonia one-note samples")

    rows = []
    counts = defaultdict(int)
    skipped = 0
    skipped_pitch_reference = 0
    for candidate in selected:
        try:
            rel_path = convert_candidate(candidate, source_dir, output_dir, ffmpeg)
        except subprocess.CalledProcessError:
            skipped += 1
            print(
                f"prepare_philharmonia_samples: skipped undecodable {candidate['member']}",
                file=sys.stderr,
            )
            continue
        if not pitch_reference_ok(output_dir / rel_path, candidate["midi"]):
            skipped_pitch_reference += 1
            continue
        row = dict(candidate)
        row["id"] = sanitize_id(candidate)
        row["path"] = str(rel_path)
        rows.append(row)
        counts[row["instrument"]] += 1

    if len(rows) < 1000:
        raise SystemExit(f"only prepared {len(rows)} decodable Philharmonia one-note samples")

    write_manifest(rows, output_dir)
    summary = " ".join(f"{name}={counts[name]}" for name in sorted(counts))
    print(
        f"prepare_philharmonia_samples: wrote {len(rows)} rows to {output_dir / 'manifest.tsv'} "
        f"(skipped {skipped}; skipped_pitch_reference {skipped_pitch_reference}; {summary})"
    )


if __name__ == "__main__":
    main()
