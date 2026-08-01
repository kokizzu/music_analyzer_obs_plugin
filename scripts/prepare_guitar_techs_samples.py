#!/usr/bin/env python3

import argparse
import hashlib
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import wave
import zipfile


FIXTURE_VERSION = "guitar-techs-v2"
DEFAULT_PERSPECTIVES = ("directinput", "micamp")
GUITAR_MIDI_RANGE = (40, 88)


def run(command):
    subprocess.run(command, check=True)


def find_command(name):
    path = shutil.which(name) if os.path.sep not in name else name
    if not path:
        raise SystemExit(f"prepare_guitar_techs_samples: missing required tool `{name}`")
    return path


def read_be_u16(data, offset):
    return (data[offset] << 8) | data[offset + 1]


def read_be_u32(data, offset):
    return (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]


def read_var_len(data, pos, end):
    value = 0
    for _ in range(4):
        if pos >= end:
            raise ValueError("truncated MIDI variable-length value")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if byte & 0x80 == 0:
            return value, pos
    raise ValueError("invalid MIDI variable-length value")


def midi_event_data_length(status):
    event_type = status & 0xF0
    if event_type in (0xC0, 0xD0):
        return 1
    if event_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
        return 2
    return -1


def build_tempo_points(tempo_events, division):
    points = [(0, 0.0, 500000)]
    current_tick = 0
    current_seconds = 0.0
    current_tempo = 500000
    for tick, tempo in sorted(tempo_events):
        if tick < current_tick:
            continue
        current_seconds += (tick - current_tick) * current_tempo / (division * 1000000.0)
        current_tick = tick
        current_tempo = tempo
        if points[-1][0] == current_tick:
            points[-1] = (current_tick, current_seconds, current_tempo)
        else:
            points.append((current_tick, current_seconds, current_tempo))
    return points


def tick_to_seconds(points, tick, division):
    point = points[0]
    for candidate in points:
        if candidate[0] > tick:
            break
        point = candidate
    point_tick, point_seconds, tempo = point
    return point_seconds + (tick - point_tick) * tempo / (division * 1000000.0)


def parse_midi_notes(path):
    data = Path(path).read_bytes()
    if len(data) < 14 or data[:4] != b"MThd":
        raise ValueError("not a MIDI file")
    header_len = read_be_u32(data, 4)
    if header_len < 6 or 8 + header_len > len(data):
        raise ValueError("invalid MIDI header")
    track_count = read_be_u16(data, 10)
    division = read_be_u16(data, 12)
    if division & 0x8000:
        raise ValueError("SMPTE MIDI timing is not supported")
    if division <= 0:
        raise ValueError("invalid MIDI division")

    pos = 8 + header_len
    parsed_tracks = 0
    raw_notes = []
    tempo_events = []

    while pos + 8 <= len(data) and parsed_tracks < track_count:
        is_track = data[pos:pos + 4] == b"MTrk"
        chunk_len = read_be_u32(data, pos + 4)
        pos += 8
        if pos + chunk_len > len(data):
            raise ValueError("truncated MIDI chunk")
        chunk_end = pos + chunk_len
        if not is_track:
            pos = chunk_end
            continue

        parsed_tracks += 1
        tick = 0
        running_status = 0
        active_notes = {}

        while pos < chunk_end:
            delta, pos = read_var_len(data, pos, chunk_end)
            tick += delta
            if pos >= chunk_end:
                raise ValueError("truncated MIDI event")

            status = data[pos]
            if status & 0x80:
                pos += 1
                if status < 0xF0:
                    running_status = status
            else:
                if not running_status:
                    raise ValueError("MIDI running status without previous status")
                status = running_status

            if status == 0xFF:
                if pos >= chunk_end:
                    raise ValueError("truncated MIDI meta event")
                meta_type = data[pos]
                pos += 1
                length, pos = read_var_len(data, pos, chunk_end)
                if pos + length > chunk_end:
                    raise ValueError("truncated MIDI meta payload")
                if meta_type == 0x51 and length == 3:
                    tempo = (data[pos] << 16) | (data[pos + 1] << 8) | data[pos + 2]
                    tempo_events.append((tick, tempo))
                pos += length
                continue

            if status in (0xF0, 0xF7):
                length, pos = read_var_len(data, pos, chunk_end)
                if pos + length > chunk_end:
                    raise ValueError("truncated MIDI sysex payload")
                pos += length
                continue

            data_len = midi_event_data_length(status)
            if data_len < 0 or pos + data_len > chunk_end:
                raise ValueError("truncated or unsupported MIDI channel event")
            first = data[pos]
            second = data[pos + 1] if data_len > 1 else 0
            pos += data_len

            key = ((status & 0x0F) << 8) | first
            event_type = status & 0xF0
            if event_type == 0x90 and second > 0:
                active_notes[key] = tick
            elif event_type == 0x80 or (event_type == 0x90 and second == 0):
                start_tick = active_notes.pop(key, None)
                if start_tick is not None and tick > start_tick:
                    raw_notes.append((start_tick, tick, first))
        pos = chunk_end

    points = build_tempo_points(tempo_events, division)
    notes = []
    for start_tick, end_tick, midi in raw_notes:
        start = tick_to_seconds(points, start_tick, division)
        end = tick_to_seconds(points, end_tick, division)
        if end - start >= 0.060 and GUITAR_MIDI_RANGE[0] <= midi <= GUITAR_MIDI_RANGE[1]:
            notes.append({"start": start, "end": end, "midi": midi})
    notes.sort(key=lambda item: (item["start"], item["midi"], item["end"]))
    return notes


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def sanitize(text, limit=90):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def archive_id(path):
    return sanitize(Path(path).stem)


def member_token(member):
    stem = Path(member).stem.lower()
    for prefix in ("midi_", "directinput_", "micamp_", "ego_", "exo_"):
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
    return stem


def discover_pairs(zip_path, perspectives):
    with zipfile.ZipFile(zip_path) as archive:
        members = [member for member in archive.namelist() if not member.endswith("/")]

    midi_members = sorted(
        member for member in members if member.lower().endswith((".mid", ".midi")) and "/midi/" in member.lower()
    )
    if not midi_members:
        raise SystemExit(f"prepare_guitar_techs_samples: no MIDI files in {zip_path}")

    audio_by_perspective = {}
    for perspective in perspectives:
        needle = f"/audio/{perspective.lower()}/"
        audio_by_perspective[perspective] = sorted(
            member for member in members if member.lower().endswith(".wav") and needle in member.lower()
        )

    pairs = []
    for midi_member in midi_members:
        token = member_token(midi_member)
        for perspective in perspectives:
            candidates = audio_by_perspective.get(perspective, [])
            matched = [member for member in candidates if member_token(member) == token]
            if not matched and len(midi_members) == 1 and len(candidates) == 1:
                matched = candidates
            for audio_member in matched:
                pairs.append({
                    "midi_member": midi_member,
                    "audio_member": audio_member,
                    "perspective": perspective,
                    "token": token,
                })
    if not pairs:
        wanted = ", ".join(perspectives)
        raise SystemExit(f"prepare_guitar_techs_samples: no matching audio/MIDI pairs for {wanted} in {zip_path}")
    return pairs


def cache_member(zip_path, member, cache_dir):
    digest = hashlib.sha256(f"{zip_path}:{member}".encode("utf-8")).hexdigest()[:12]
    suffix = Path(member).suffix or ".bin"
    output = cache_dir / archive_id(zip_path) / f"{sanitize(member, 120)}-{digest}{suffix}"
    if output.is_file() and output.stat().st_size > 0:
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open(member) as source:
            tmp.write_bytes(source.read())
    tmp.replace(output)
    return output


def clip_bounds(notes, index, clip_seconds):
    note = notes[index]
    clip_start = max(0.0, note["start"] - 0.030)
    clip_end = min(note["end"] + 0.080, clip_start + clip_seconds)
    if index + 1 < len(notes):
        clip_end = min(clip_end, max(clip_start + 0.220, notes[index + 1]["start"] - 0.050))
    duration = max(0.220, clip_end - clip_start)
    return clip_start, duration


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
            "-f",
            "wav",
            str(tmp),
        ])
        tmp.replace(output_path)
    finally:
        if tmp.exists():
            tmp.unlink()


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
    for index, sample in enumerate(samples):
        window = 0.5 - 0.5 * math.cos(2.0 * math.pi * index / max(1, count - 1))
        x = (sample - mean) * window
        s0 = x + coeff * s1 - s2
        s2 = s1
        s1 = s0
    return math.sqrt(max(0.0, s1 * s1 + s2 * s2 - coeff * s1 * s2))


def read_wav_probe(path):
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        sample_width = wav.getsampwidth()
        frame_count = wav.getnframes()
        if sample_width != 2:
            return sample_rate, []
        start = min(frame_count, int(sample_rate * 0.16))
        count = min(frame_count - start, int(sample_rate * 0.28))
        if count <= 0:
            return sample_rate, []
        wav.setpos(start)
        data = wav.readframes(count)

    samples = []
    step = sample_width * channels
    for offset in range(0, len(data), step):
        total = 0.0
        for channel in range(channels):
            sample_offset = offset + channel * sample_width
            value = int.from_bytes(data[sample_offset:sample_offset + sample_width], byteorder="little", signed=True)
            total += value / 32768.0
        samples.append(total / channels)
    return sample_rate, samples


def pitch_reference_ok(path, midi):
    sample_rate, samples = read_wav_probe(path)
    if not samples:
        return False
    expected = goertzel_level(samples, sample_rate, midi_frequency(midi))
    adjacent = 0.0
    if midi > GUITAR_MIDI_RANGE[0]:
        adjacent = max(adjacent, goertzel_level(samples, sample_rate, midi_frequency(midi - 1)))
    if midi < GUITAR_MIDI_RANGE[1]:
        adjacent = max(adjacent, goertzel_level(samples, sample_rate, midi_frequency(midi + 1)))
    octave = 0.0
    if midi >= 52:
        octave = max(octave, goertzel_level(samples, sample_rate, midi_frequency(midi - 12)))
    if midi <= 76:
        octave = max(octave, goertzel_level(samples, sample_rate, midi_frequency(midi + 12)))
    if expected <= 1.0e-6:
        return False
    if adjacent > 1.0e-6 and expected < adjacent * 0.70:
        return False
    if octave > 1.0e-6 and expected < octave * 0.25:
        return False
    return True


def signature_text(archives, perspectives, limit, clip_seconds, skip_pitch_check):
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
        f"limit={limit}",
        f"clip={clip_seconds:.3f}",
        f"pitch={0 if skip_pitch_check else 1}",
        ",".join(perspectives),
        "|".join(archive_bits),
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def manifest_complete(path, expected_signature, min_rows):
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
            if len(fields) != 8 or fields[7] != expected_signature:
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
                    row.get("nsynth_family", "guitar_techs"),
                    row["source"],
                    str(row["midi"]),
                    row["note"],
                    row["path"],
                    signature,
                ]) + "\n"
            )


def parse_perspectives(text):
    values = [item.strip().lower() for item in text.split(",") if item.strip()]
    if not values:
        return list(DEFAULT_PERSPECTIVES)
    return values


def prepare_archives(args):
    ffmpeg = find_command(args.ffmpeg)
    output_dir = Path(args.output)
    cache_dir = Path(args.cache_dir) if args.cache_dir else output_dir / "_cache"
    archives = [Path(path) for path in args.archive]
    for archive in archives:
        if not archive.is_file():
            raise SystemExit(f"prepare_guitar_techs_samples: missing archive {archive}")

    perspectives = parse_perspectives(args.perspectives)
    signature = signature_text(archives, perspectives, args.limit, args.clip_seconds, args.skip_pitch_check)
    manifest_path = output_dir / "manifest.tsv"
    min_samples = max(0, args.min_samples)
    if not args.refresh and manifest_complete(manifest_path, signature, min_samples):
        print(f"prepare_guitar_techs_samples: keeping existing {manifest_path}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    skipped_pitch_reference = 0
    skipped_short = 0
    skipped_errors = []

    for archive in archives:
        pairs = discover_pairs(archive, perspectives)
        midi_cache = {}
        audio_cache = {}
        for pair in pairs:
            midi_member = pair["midi_member"]
            audio_member = pair["audio_member"]
            if midi_member not in midi_cache:
                midi_cache[midi_member] = cache_member(archive, midi_member, cache_dir)
            if audio_member not in audio_cache:
                audio_cache[audio_member] = cache_member(archive, audio_member, cache_dir)

            notes = parse_midi_notes(midi_cache[midi_member])
            if not notes:
                skipped_errors.append((midi_member, "no usable MIDI notes"))
                continue

            for index, note in enumerate(notes):
                if args.limit > 0 and len(rows) >= args.limit:
                    break
                start, duration = clip_bounds(notes, index, args.clip_seconds)
                if duration < 0.220:
                    skipped_short += 1
                    continue
                label = note_name(note["midi"])
                row_id = sanitize(
                    f"guitar_techs_{archive_id(archive)}_{pair['perspective']}_{index:04d}_{label}"
                )
                rel_path = Path("audio") / f"{row_id}.wav"
                output_path = output_dir / rel_path
                try:
                    convert_clip(ffmpeg, audio_cache[audio_member], output_path, start, duration)
                    if not args.skip_pitch_check and not pitch_reference_ok(output_path, note["midi"]):
                        skipped_pitch_reference += 1
                        continue
                except (subprocess.CalledProcessError, wave.Error, OSError) as exc:
                    skipped_errors.append((row_id, str(exc)))
                    continue

                rows.append({
                    "id": row_id,
                    "nsynth_family": f"guitar_techs:{pair['perspective']}",
                    "source": "electronic",
                    "midi": note["midi"],
                    "note": label,
                    "path": str(rel_path),
                })
            if args.limit > 0 and len(rows) >= args.limit:
                break
        if args.limit > 0 and len(rows) >= args.limit:
            break

    required_prepared = max(1, min_samples)
    if len(rows) < required_prepared:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, rows, signature)
        raise SystemExit(
            f"prepare_guitar_techs_samples: expected at least {required_prepared} prepared samples, "
            f"got {len(rows)}; wrote partial manifest {partial_path}"
        )

    write_manifest(manifest_path, rows, signature)
    print(
        f"prepare_guitar_techs_samples: wrote {len(rows)} rows to {manifest_path} "
        f"(skipped_short {skipped_short}; skipped_pitch_reference {skipped_pitch_reference}; "
        f"skipped_errors {len(skipped_errors)})"
    )
    for sample_id, reason in skipped_errors[:12]:
        print(f"prepare_guitar_techs_samples: skipped {sample_id}: {reason}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare Guitar-TECHS single-note ZIPs as analyzer real-note samples."
    )
    parser.add_argument("--archive", action="append", default=[])
    parser.add_argument("--output", default=os.environ.get("GUITAR_TECHS_SAMPLE_DIR",
                                                           "build/guitar_techs_samples"))
    parser.add_argument("--cache-dir", default=os.environ.get("GUITAR_TECHS_CACHE_DIR", ""))
    parser.add_argument("--perspectives", default=os.environ.get("GUITAR_TECHS_PERSPECTIVES",
                                                                 ",".join(DEFAULT_PERSPECTIVES)))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("GUITAR_TECHS_SAMPLE_LIMIT", "0")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("GUITAR_TECHS_MIN_SAMPLES", "1")))
    parser.add_argument("--clip-seconds", type=float, default=float(os.environ.get("GUITAR_TECHS_CLIP_SECONDS",
                                                                                   "1.20")))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    parser.add_argument("--skip-pitch-check", action="store_true",
                        default=os.environ.get("GUITAR_TECHS_SKIP_PITCH_CHECK") == "1")
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("GUITAR_TECHS_REFRESH") == "1")
    args = parser.parse_args(argv)

    if not args.archive:
        raise SystemExit("prepare_guitar_techs_samples: at least one --archive is required")
    prepare_archives(args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"prepare_guitar_techs_samples: command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(exc.returncode)
