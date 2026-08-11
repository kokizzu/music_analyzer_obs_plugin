#!/usr/bin/env python3

import argparse
import csv
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tarfile
import wave


FIXTURE_VERSION = "bach10-mf0-synth-musicnet-v2"


def archive_signature(path):
    archive = Path(path)
    if not archive.is_file():
        return "missing"
    stat = archive.stat()
    return f"{stat.st_size}:{int(stat.st_mtime)}"


def root_signature(path):
    root = Path(path)
    if not root.is_dir():
        return "missing"
    newest = 0
    count = 0
    for item in root.rglob("*"):
        if item.is_file():
            stat = item.stat()
            newest = max(newest, int(stat.st_mtime))
            count += 1
    return f"{count}:{newest}"


def signature_text(args):
    source = args.source_root or args.archive
    source_sig = root_signature(args.source_root) if args.source_root else archive_signature(args.archive)
    return "|".join([
        FIXTURE_VERSION,
        f"source={Path(source)}:{source_sig}",
        f"limit={args.limit}",
    ])


def cache_ok(output, signature, min_recordings):
    signature_path = output / ".bach10_mf0_synth_signature"
    data_dir = output / "train_data"
    label_dir = output / "train_labels"
    if not signature_path.is_file() or signature_path.read_text(encoding="utf-8") != signature:
        return False
    if not data_dir.is_dir() or not label_dir.is_dir():
        return False
    wavs = sorted(data_dir.glob("*.wav"))
    labels = sorted(label_dir.glob("*.csv"))
    if len(wavs) < min_recordings or len(labels) < min_recordings:
        return False
    return all((label_dir / (wav.stem + ".csv")).is_file() for wav in wavs)


def safe_name(text, limit=80):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "piece"


def output_id_for_key(key):
    text = str(key)
    if re.fullmatch(r"\d+", text):
        return str(int(text))
    return safe_name(text)


def lower_path(path):
    return str(path).replace("\\", "/").lower()


def piece_key(path):
    stem = Path(path).stem
    match = re.match(r"^(\d+)", stem)
    if match:
        return match.group(1)
    return stem.split("_", 1)[0].split("-", 1)[0]


def is_audio_mix(path):
    lowered = lower_path(path)
    return "/audio_mix/" in lowered and lowered.endswith(".wav")


def is_stem_annotation(path):
    lowered = lower_path(path)
    return "/annotation_stems/" in lowered and lowered.endswith(".csv")


def instrument_id_from_path(path, index):
    lowered = Path(path).stem.lower()
    if "bassoon" in lowered or re.search(r"(^|[_-])bs($|[_-])", lowered):
        return 70
    if "sax" in lowered or re.search(r"(^|[_-])as($|[_-])", lowered):
        return 65
    if "clarinet" in lowered or re.search(r"(^|[_-])cl($|[_-])", lowered):
        return 71
    if "violin" in lowered or re.search(r"(^|[_-])vn($|[_-])", lowered):
        return 41
    return 80 + index


def hz_to_midi(freq):
    if freq <= 0.0:
        return -1
    midi = int(round(69.0 + 12.0 * math.log(freq / 440.0, 2.0)))
    return midi if 21 <= midi <= 108 else -1


def numeric_csv_columns(header):
    lowered = [item.strip().lower() for item in header]
    time_index = 0
    freq_index = 1
    for name in ("time", "timestamp", "seconds", "sec"):
        if name in lowered:
            time_index = lowered.index(name)
            break
    for name in ("frequency", "freq", "f0", "hz", "pitch"):
        if name in lowered:
            freq_index = lowered.index(name)
            break
    return time_index, freq_index


def read_f0_points(text):
    points = []
    header = None
    time_index = 0
    freq_index = 1
    for row in csv.reader(text.splitlines()):
        if not row:
            continue
        stripped = [cell.strip() for cell in row]
        try:
            time_value = float(stripped[time_index])
            freq_value = float(stripped[freq_index])
        except (IndexError, ValueError):
            if header is None:
                header = stripped
                time_index, freq_index = numeric_csv_columns(header)
            continue
        if time_value >= 0.0 and freq_value > 0.0:
            points.append((time_value, freq_value))
    return points


def median(values, fallback):
    if not values:
        return fallback
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def points_to_notes(points, instrument, min_duration=0.08, max_gap=0.12):
    ordered = sorted((time, hz_to_midi(freq)) for time, freq in points)
    ordered = [(time, midi) for time, midi in ordered if midi > 0]
    if not ordered:
        return []

    deltas = [
        ordered[index + 1][0] - ordered[index][0]
        for index in range(len(ordered) - 1)
        if 0.0 < ordered[index + 1][0] - ordered[index][0] <= 0.25
    ]
    frame_step = min(0.10, max(0.01, median(deltas, 0.05)))

    notes = []
    current_midi = ordered[0][1]
    start = ordered[0][0]
    previous_time = ordered[0][0]
    for time_value, midi in ordered[1:]:
        gap = time_value - previous_time
        if midi != current_midi or gap > max_gap:
            end = previous_time + frame_step
            if end - start >= min_duration:
                notes.append((start, end, instrument, current_midi))
            start = time_value
            current_midi = midi
        previous_time = time_value

    end = previous_time + frame_step
    if end - start >= min_duration:
        notes.append((start, end, instrument, current_midi))
    return notes


def read_wav_sample_rate(path):
    with wave.open(str(path), "rb") as audio:
        return audio.getframerate()


def write_labels(path, notes, sample_rate):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for start, end, instrument, midi in notes:
        rows.append({
            "start_time": max(0, int(round(start * sample_rate))),
            "end_time": max(0, int(round(end * sample_rate))),
            "instrument": int(instrument),
            "note": int(midi),
            "start_beat": 0.0,
            "end_beat": 0.0,
            "note_value": 0.0,
        })
    rows.sort(key=lambda row: (row["start_time"], row["instrument"], row["note"]))
    with path.open("w", newline="", encoding="utf-8") as label_file:
        writer = csv.DictWriter(
            label_file,
            fieldnames=["start_time", "end_time", "instrument", "note", "start_beat", "end_beat", "note_value"],
        )
        writer.writeheader()
        writer.writerows(rows)


def collect_from_root(root):
    entries = []
    root_path = Path(root)
    for path in sorted(root_path.rglob("*")):
        if path.is_file():
            rel = str(path.relative_to(root_path)).replace(os.sep, "/")
            entries.append({"name": rel, "path": path})
    return entries


def collect_from_archive(archive):
    entries = []
    with tarfile.open(archive, "r:*") as tar:
        for member in tar.getmembers():
            if member.isfile():
                entries.append({"name": member.name, "member": member.name})
    return entries


def group_pieces(entries):
    mixes = {}
    annotations = {}
    for entry in entries:
        name = entry["name"]
        key = piece_key(name)
        if is_audio_mix(name):
            mixes.setdefault(key, entry)
        elif is_stem_annotation(name):
            annotations.setdefault(key, []).append(entry)

    pieces = []
    for key in sorted(mixes):
        stem_annotations = sorted(annotations.get(key, []), key=lambda item: item["name"])
        if stem_annotations:
            pieces.append({"key": key, "mix": mixes[key], "annotations": stem_annotations})
    return pieces


def read_archive_text(tar, member_name):
    extracted = tar.extractfile(member_name)
    if extracted is None:
        raise OSError(f"cannot read archive member {member_name}")
    return extracted.read().decode("utf-8", errors="replace")


def copy_archive_member(tar, member_name, dest):
    extracted = tar.extractfile(member_name)
    if extracted is None:
        raise OSError(f"cannot read archive member {member_name}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as output:
        shutil.copyfileobj(extracted, output)


def prepare_piece_from_root(piece, output_root, output_id):
    audio_out = output_root / "train_data" / f"{output_id}.wav"
    label_out = output_root / "train_labels" / f"{output_id}.csv"
    audio_out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(piece["mix"]["path"], audio_out)
    sample_rate = read_wav_sample_rate(audio_out)

    notes = []
    for index, annotation in enumerate(piece["annotations"], start=1):
        text = annotation["path"].read_text(encoding="utf-8", errors="replace")
        instrument = instrument_id_from_path(annotation["name"], index)
        notes.extend(points_to_notes(read_f0_points(text), instrument))
    if not notes:
        raise ValueError(f"{piece['key']}: no usable F0-derived notes")
    write_labels(label_out, notes, sample_rate)


def prepare_piece_from_archive(tar, piece, output_root, output_id):
    audio_out = output_root / "train_data" / f"{output_id}.wav"
    label_out = output_root / "train_labels" / f"{output_id}.csv"
    copy_archive_member(tar, piece["mix"]["member"], audio_out)
    sample_rate = read_wav_sample_rate(audio_out)

    notes = []
    for index, annotation in enumerate(piece["annotations"], start=1):
        text = read_archive_text(tar, annotation["member"])
        instrument = instrument_id_from_path(annotation["name"], index)
        notes.extend(points_to_notes(read_f0_points(text), instrument))
    if not notes:
        raise ValueError(f"{piece['key']}: no usable F0-derived notes")
    write_labels(label_out, notes, sample_rate)


def prepare(args):
    if not args.source_root and not Path(args.archive).is_file():
        raise SystemExit(f"prepare_bach10_mf0_synth_musicnet_fixture: missing archive {args.archive}")
    if args.source_root and not Path(args.source_root).is_dir():
        raise SystemExit(f"prepare_bach10_mf0_synth_musicnet_fixture: `{args.source_root}` is not a directory")

    output = Path(args.output)
    # The build path can be a stable link into InstrumentSamples.  Do not
    # delete that link: clear its owned target so the generated audio remains
    # external and subsequent Make targets keep the same path.
    output_root = output.resolve() if output.is_symlink() else output
    signature = signature_text(args)
    min_recordings = max(1, args.min_recordings)
    if not args.refresh and cache_ok(output, signature, min_recordings):
        recordings = len(list((output / "train_data").glob("*.wav")))
        print(f"prepare_bach10_mf0_synth_musicnet_fixture: reused {output} ({recordings} recordings)")
        return recordings

    entries = collect_from_root(args.source_root) if args.source_root else collect_from_archive(args.archive)
    pieces = group_pieces(entries)
    if args.limit > 0:
        pieces = pieces[:args.limit]
    if len(pieces) < min_recordings:
        raise SystemExit(
            f"prepare_bach10_mf0_synth_musicnet_fixture: expected at least {min_recordings} "
            f"complete pieces, got {len(pieces)}"
        )

    if output_root.exists():
        shutil.rmtree(output_root)
    (output_root / "train_data").mkdir(parents=True, exist_ok=True)
    (output_root / "train_labels").mkdir(parents=True, exist_ok=True)

    failures = []
    prepared = 0
    if args.source_root:
        for piece in pieces:
            try:
                prepare_piece_from_root(piece, output_root, output_id_for_key(piece["key"]))
                prepared += 1
            except (OSError, ValueError, wave.Error) as exc:
                failures.append(f"{piece['key']}: {exc}")
    else:
        with tarfile.open(args.archive, "r:*") as tar:
            for piece in pieces:
                try:
                    prepare_piece_from_archive(tar, piece, output_root, output_id_for_key(piece["key"]))
                    prepared += 1
                except (OSError, ValueError, wave.Error, tarfile.TarError) as exc:
                    failures.append(f"{piece['key']}: {exc}")

    if prepared < min_recordings:
        for failure in failures[:10]:
            print(f"prepare_bach10_mf0_synth_musicnet_fixture: {failure}", file=sys.stderr)
        raise SystemExit(
            f"prepare_bach10_mf0_synth_musicnet_fixture: expected to prepare {min_recordings} "
            f"pieces, prepared {prepared}"
        )

    (output_root / ".bach10_mf0_synth_signature").write_text(signature, encoding="utf-8")
    print(f"prepare_bach10_mf0_synth_musicnet_fixture: wrote {prepared} recordings to {output}")
    return prepared


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare Bach10-mf0-synth as a MusicNet-shaped fixture.")
    parser.add_argument("--archive", default=os.environ.get(
        "BACH10_MF0_SYNTH_ARCHIVE",
        "build/real_sample_sources/bach10_mf0_synth/Bach10-mf0-syth.tar.gz",
    ))
    parser.add_argument("--source-root", default=os.environ.get("BACH10_MF0_SYNTH_SOURCE_ROOT", ""))
    parser.add_argument("--output", default=os.environ.get(
        "BACH10_MF0_SYNTH_SAMPLE_DIR",
        "build/bach10_mf0_synth_musicnet",
    ))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("BACH10_MF0_SYNTH_RECORDING_LIMIT", "0")))
    parser.add_argument("--min-recordings", type=int,
                        default=int(os.environ.get("BACH10_MF0_SYNTH_MIN_RECORDINGS", "10")))
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("BACH10_MF0_SYNTH_REFRESH") == "1")
    args = parser.parse_args(argv)
    args.limit = max(0, args.limit)
    args.min_recordings = max(1, args.min_recordings)
    prepare(args)


if __name__ == "__main__":
    raise SystemExit(main())
