#!/usr/bin/env python3

import argparse
import hashlib
import io
import os
from pathlib import Path
import re
import struct
import sys
import wave
import xml.etree.ElementTree as ET
import zipfile


FIXTURE_VERSION = "idmt-smt-drums-v1"
LABEL_MAP = {
    "KD": "kick",
    "SD": "snare",
    "HH": "hihat",
}
MANIFEST_HEADER = ["category", "path", "duration_seconds", "source", "signature"]


def sanitize(text, limit=120):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def normalize_tag(tag):
    if "}" in tag:
        tag = tag.rsplit("}", 1)[1]
    return re.sub(r"[^a-z0-9]+", "", tag.lower())


def parse_svl_points(data):
    root = ET.fromstring(data)
    sample_rate = None
    points = []
    for element in root.iter():
        tag = normalize_tag(element.tag)
        if tag == "model" and element.get("sampleRate"):
            try:
                sample_rate = int(round(float(element.get("sampleRate"))))
            except (TypeError, ValueError):
                sample_rate = None
        elif tag == "point" and element.get("frame") is not None:
            try:
                frame = int(round(float(element.get("frame"))))
            except (TypeError, ValueError):
                continue
            if frame >= 0:
                points.append(frame)
    points.sort()
    return sample_rate, points


def decode_sample(frame_bytes, sample_width):
    if sample_width == 1:
        return (frame_bytes[0] - 128) / 128.0
    if sample_width == 2:
        return struct.unpack_from("<h", frame_bytes)[0] / 32768.0
    if sample_width == 3:
        value = frame_bytes[0] | (frame_bytes[1] << 8) | (frame_bytes[2] << 16)
        if value & 0x800000:
            value |= ~0xFFFFFF
        return value / 8388608.0
    if sample_width == 4:
        return struct.unpack_from("<i", frame_bytes)[0] / 2147483648.0
    return 0.0


def mono_peak_and_rms(frames, channels, sample_width):
    if not frames:
        return 0.0, 0.0
    stride = channels * sample_width
    if stride <= 0:
        return 0.0, 0.0
    peak = 0.0
    energy = 0.0
    count = 0
    for offset in range(0, len(frames) - stride + 1, stride):
        value = 0.0
        for channel in range(channels):
            start = offset + channel * sample_width
            value += decode_sample(frames[start:start + sample_width], sample_width)
        value /= channels
        abs_value = abs(value)
        peak = max(peak, abs_value)
        energy += value * value
        count += 1
    if count == 0:
        return 0.0, 0.0
    return peak, (energy / count) ** 0.5


def read_wave_member(archive, member):
    with archive.open(member) as source:
        data = source.read()
    with wave.open(io.BytesIO(data), "rb") as wav:
        params = wav.getparams()
        frames = wav.readframes(params.nframes)
    return {
        "sample_rate": params.framerate,
        "channels": params.nchannels,
        "sample_width": params.sampwidth,
        "frame_count": params.nframes,
        "frames": frames,
    }


def write_wave_clip(path, source, start_frame, frame_count):
    start_byte = start_frame * source["channels"] * source["sample_width"]
    byte_count = frame_count * source["channels"] * source["sample_width"]
    clip = source["frames"][start_byte:start_byte + byte_count]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with wave.open(str(tmp), "wb") as wav:
        wav.setnchannels(source["channels"])
        wav.setsampwidth(source["sample_width"])
        wav.setframerate(source["sample_rate"])
        wav.writeframes(clip)
    tmp.replace(path)


def scan_archive(zip_path):
    with zipfile.ZipFile(zip_path) as archive:
        members = [member for member in archive.namelist() if not member.endswith("/")]
    audio_regex = re.compile(r"^audio/(.+)#(KD|SD|HH)#train\.wav$")
    svl_members = set(member for member in members if member.startswith("annotation_svl/"))
    pairs = []
    for member in sorted(members):
        match = audio_regex.match(member)
        if not match:
            continue
        track, code = match.groups()
        svl_member = f"annotation_svl/{track}#{code}.svl"
        if svl_member not in svl_members:
            pairs.append({"audio_member": member, "code": code, "track": track, "error": "missing SVL"})
            continue
        pairs.append({
            "audio_member": member,
            "svl_member": svl_member,
            "code": code,
            "category": LABEL_MAP[code],
            "track": track,
        })
    return pairs


def signature_text(archive_path, args):
    path = Path(archive_path)
    stat = path.stat() if path.is_file() else None
    archive_bits = f"{path.name}:{stat.st_size}:{int(stat.st_mtime)}" if stat else str(path)
    payload = "|".join([
        FIXTURE_VERSION,
        archive_bits,
        f"limit={args.limit_per_category}",
        f"min={args.min_per_category}",
        f"clip={args.clip_seconds:.3f}",
        f"pre={args.pre_roll_seconds:.3f}",
        f"peak={args.min_peak:.6f}",
        f"rms={args.min_rms:.6f}",
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def read_manifest_counts(path, signature):
    if not path.is_file():
        return {}
    counts = {category: 0 for category in LABEL_MAP.values()}
    root = path.parent
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header != MANIFEST_HEADER:
            return {}
        for line in file:
            fields = line.rstrip("\n").split("\t")
            if len(fields) != len(MANIFEST_HEADER) or fields[-1] != signature:
                return {}
            category, relative_path = fields[0], fields[1]
            if category not in counts:
                return {}
            if not (root / relative_path).is_file():
                return {}
            counts[category] += 1
    return counts


def manifest_complete(path, signature, required_per_category):
    counts = read_manifest_counts(path, signature)
    if not counts:
        return False
    return all(counts.get(category, 0) >= required_per_category for category in LABEL_MAP.values())


def balanced_limit(candidates, limit_per_category):
    if limit_per_category <= 0:
        return candidates
    selected = []
    for category in sorted(LABEL_MAP.values()):
        rows = [row for row in candidates if row["category"] == category]
        if len(rows) <= limit_per_category:
            selected.extend(rows)
            continue
        buckets = {}
        for row in rows:
            buckets.setdefault(row["track"], []).append(row)
        for bucket_rows in buckets.values():
            bucket_rows.sort(key=lambda row: (row["frame"], row["id"]))
        keys = sorted(buckets)
        bucket_index = 0
        category_selected = 0
        while category_selected < limit_per_category:
            progressed = False
            for key in keys:
                bucket = buckets[key]
                if bucket_index < len(bucket):
                    selected.append(bucket[bucket_index])
                    category_selected += 1
                    progressed = True
                    if category_selected >= limit_per_category:
                        break
            if not progressed:
                break
            bucket_index += 1
    selected.sort(key=lambda row: (row["category"], row["track"], row["frame"], row["id"]))
    return selected


def collect_candidates(zip_path, args):
    candidates = []
    skipped = {}

    def skip(reason, count=1):
        skipped[reason] = skipped.get(reason, 0) + count

    with zipfile.ZipFile(zip_path) as archive:
        for pair in scan_archive(zip_path):
            if pair.get("error"):
                skip(pair["error"])
                continue
            try:
                annotation_sample_rate, points = parse_svl_points(archive.read(pair["svl_member"]))
            except ET.ParseError:
                skip("bad_svl")
                continue
            if not points:
                skip("no_points")
                continue
            try:
                source = read_wave_member(archive, pair["audio_member"])
            except (wave.Error, OSError, EOFError):
                skip("bad_wav")
                continue
            if source["sample_width"] not in (1, 2, 3, 4) or source["channels"] <= 0:
                skip("unsupported_wav")
                continue
            if annotation_sample_rate and abs(annotation_sample_rate - source["sample_rate"]) > 1:
                skip("sample_rate_mismatch")
                continue

            pre_roll_frames = max(0, int(round(args.pre_roll_seconds * source["sample_rate"])))
            clip_frames = max(1, int(round(args.clip_seconds * source["sample_rate"])))
            for point_index, frame in enumerate(points, start=1):
                start_frame = max(0, frame - pre_roll_frames)
                end_frame = min(source["frame_count"], start_frame + clip_frames)
                if end_frame <= start_frame:
                    skip("empty_clip")
                    continue
                frame_count = end_frame - start_frame
                if frame_count < max(1, int(round(args.min_clip_seconds * source["sample_rate"]))):
                    skip("short_clip")
                    continue
                start_byte = start_frame * source["channels"] * source["sample_width"]
                byte_count = frame_count * source["channels"] * source["sample_width"]
                clip_frames_bytes = source["frames"][start_byte:start_byte + byte_count]
                peak, rms = mono_peak_and_rms(clip_frames_bytes, source["channels"], source["sample_width"])
                if peak < args.min_peak:
                    skip("quiet_peak")
                    continue
                if rms < args.min_rms:
                    skip("quiet_rms")
                    continue
                row_id = sanitize(f"{pair['track']}_{pair['code']}_{point_index:04d}_{frame}")
                candidates.append({
                    "id": row_id,
                    "category": pair["category"],
                    "track": pair["track"],
                    "code": pair["code"],
                    "audio_member": pair["audio_member"],
                    "start_frame": start_frame,
                    "frame_count": frame_count,
                    "sample_rate": source["sample_rate"],
                    "duration": frame_count / source["sample_rate"],
                    "path": str(Path(pair["category"]) / f"{row_id}.wav"),
                    "source": f"idmt-smt-drums:{pair['track']}:{pair['code']}",
                    "_source": source,
                    "frame": frame,
                })
    candidates.sort(key=lambda row: (row["category"], row["track"], row["frame"], row["id"]))
    return candidates, skipped


def write_manifest(path, rows, signature):
    with path.open("w", encoding="utf-8") as file:
        file.write("\t".join(MANIFEST_HEADER) + "\n")
        for row in rows:
            file.write(
                "\t".join([
                    row["category"],
                    row["path"],
                    f"{row['duration']:.6f}",
                    row["source"],
                    signature,
                ]) + "\n"
            )


def counts_text(rows):
    counts = {category: 0 for category in LABEL_MAP.values()}
    for row in rows:
        counts[row["category"]] += 1
    return " ".join(f"{category}={counts[category]}" for category in sorted(counts))


def prepare(args):
    archive_path = Path(args.archive)
    if not archive_path.is_file():
        raise SystemExit(f"prepare_idmt_drums_samples: missing archive {archive_path}")
    output_dir = Path(args.output)
    signature = signature_text(archive_path, args)
    manifest_path = output_dir / "manifest.tsv"
    cache_requirement = args.limit_per_category if args.limit_per_category > 0 else args.min_per_category
    if not args.refresh and manifest_complete(manifest_path, signature, max(1, cache_requirement)):
        print(f"prepare_idmt_drums_samples: keeping existing {manifest_path}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    for category in LABEL_MAP.values():
        (output_dir / category).mkdir(parents=True, exist_ok=True)

    candidates, skipped = collect_candidates(archive_path, args)
    selected = balanced_limit(candidates, args.limit_per_category)
    rows = []
    errors = []
    for row in selected:
        try:
            write_wave_clip(output_dir / row["path"], row["_source"], row["start_frame"], row["frame_count"])
        except (OSError, wave.Error) as exc:
            errors.append((row["id"], str(exc)))
            continue
        rows.append(row)

    required = max(1, args.min_per_category)
    short = [
        f"{category}={sum(1 for row in rows if row['category'] == category)}"
        for category in sorted(LABEL_MAP.values())
        if sum(1 for row in rows if row["category"] == category) < required
    ]
    if short:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, rows, signature)
        raise SystemExit(
            "prepare_idmt_drums_samples: expected at least "
            f"{required} prepared clips per category, got {' '.join(short)}; "
            f"wrote partial manifest {partial_path}"
        )

    write_manifest(manifest_path, rows, signature)
    skipped_text = " ".join(f"{key}={value}" for key, value in sorted(skipped.items()))
    print(
        f"prepare_idmt_drums_samples: wrote {len(rows)} rows to {manifest_path} "
        f"({counts_text(rows)}, candidates {len(candidates)}, skipped {skipped_text or 'none'}, errors {len(errors)})"
    )
    for sample_id, reason in errors[:12]:
        print(f"prepare_idmt_drums_samples: skipped {sample_id}: {reason}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare IDMT-SMT-Drums SVL/WAV hit windows as analyzer drum samples."
    )
    parser.add_argument("--archive", default=os.environ.get(
        "IDMT_DRUMS_ARCHIVE",
        "build/real_sample_sources/idmt_drums/IDMT-SMT-DRUMS-V2.zip",
    ))
    parser.add_argument("--output", default=os.environ.get("IDMT_DRUMS_SAMPLE_DIR",
                                                          "build/idmt_drums_samples"))
    parser.add_argument("--limit-per-category", type=int,
                        default=int(os.environ.get("IDMT_DRUMS_LIMIT_PER_CATEGORY", "0")))
    parser.add_argument("--min-per-category", type=int,
                        default=int(os.environ.get("IDMT_DRUMS_MIN_PER_CATEGORY", "300")))
    parser.add_argument("--clip-seconds", type=float,
                        default=float(os.environ.get("IDMT_DRUMS_CLIP_SECONDS", "0.18")))
    parser.add_argument("--min-clip-seconds", type=float,
                        default=float(os.environ.get("IDMT_DRUMS_MIN_CLIP_SECONDS", "0.05")))
    parser.add_argument("--pre-roll-seconds", type=float,
                        default=float(os.environ.get("IDMT_DRUMS_PRE_ROLL_SECONDS", "0.005")))
    parser.add_argument("--min-peak", type=float,
                        default=float(os.environ.get("IDMT_DRUMS_MIN_PEAK", "0.002")))
    parser.add_argument("--min-rms", type=float,
                        default=float(os.environ.get("IDMT_DRUMS_MIN_RMS", "0.0002")))
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("IDMT_DRUMS_REFRESH") == "1")
    args = parser.parse_args(argv)
    args.limit_per_category = max(0, args.limit_per_category)
    args.min_per_category = max(1, args.min_per_category)
    args.clip_seconds = max(0.01, args.clip_seconds)
    args.min_clip_seconds = max(0.001, min(args.min_clip_seconds, args.clip_seconds))
    args.pre_roll_seconds = max(0.0, args.pre_roll_seconds)
    args.min_peak = max(0.0, args.min_peak)
    args.min_rms = max(0.0, args.min_rms)
    prepare(args)


if __name__ == "__main__":
    main()
