#!/usr/bin/env python3

import argparse
import csv
import errno
import json
import os
from pathlib import Path
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request


DATASET = "CarlSouthall/MDBDrums"
TREE_URL = f"https://api.github.com/repos/{DATASET}/git/trees/master?recursive=1"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{DATASET}/master"
FIXTURE_VERSION = "mdb-drums-egmd-shaped-v2"
DIVISION = 480
TEMPO_US_PER_QUARTER = 500000

SUBCLASS_TO_GM = {
    "KD": 36,
    "SD": 38,
    "SDG": 38,
    "SDB": 38,
    "SDF": 38,
    "SDD": 38,
    "SDNS": 38,
    "SST": 37,
    "CHH": 42,
    "PHH": 44,
    "OHH": 46,
    "CRC": 49,
    "CHC": 49,
    "SPC": 49,
    "RDC": 51,
    "RDB": 53,
    "LFT": 41,
    "HFT": 43,
    "MHT": 47,
    "HIT": 50,
}

CLASS_TO_GM = {
    "KD": 36,
    "SD": 38,
    "HH": 42,
    "CY": 49,
    "TT": 47,
    "OT": 51,
}


def sanitize(text, limit=100):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def is_url(text):
    lowered = str(text).lower()
    return lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("file://")


def read_json_resource(resource, timeout):
    if is_url(resource):
        with urllib.request.urlopen(resource, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(resource).read_text(encoding="utf-8"))


def read_text_resource(resource, timeout):
    if is_url(resource):
        with urllib.request.urlopen(resource, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    return Path(resource).read_text(encoding="utf-8", errors="replace")


def resource_url(base_url, path):
    return base_url.rstrip("/") + "/" + urllib.parse.quote(path, safe="/")


def download_file(url, path, retries, timeout):
    if not is_url(url):
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(url, path)
        return

    if path.is_file() and path.stat().st_size > 0:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    last_error = None
    for attempt in range(max(1, retries)):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "music-analyzer-obs-plugin-sample-prep/1.0"},
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                with tmp.open("wb") as file:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        file.write(chunk)
            if tmp.stat().st_size <= 0:
                raise OSError("empty download")
            tmp.replace(path)
            return
        except (OSError, TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            if tmp.exists():
                tmp.unlink()
            if attempt + 1 < max(1, retries):
                time.sleep(min(2.0, 0.25 * (attempt + 1)))
    raise OSError(f"download failed for {url}: {last_error}")


def tree_entries(source_root, tree_json, timeout):
    if source_root:
        root = Path(source_root)
        prefix = root.name if root.name == "MDB Drums" else "MDB Drums"
        entries = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            entries.append({"path": str(Path(prefix) / relative).replace(os.sep, "/")})
        return entries

    payload = read_json_resource(tree_json or TREE_URL, timeout)
    return payload.get("tree", [])


def file_resource(path, source_root):
    if source_root:
        local_root = Path(source_root)
        relative = Path(path)
        if relative.parts and relative.parts[0] == "MDB Drums":
            relative = Path(*relative.parts[1:])
        return str(local_root / relative)
    return resource_url(RAW_BASE_URL, path)


def track_id_from_audio_path(path):
    name = Path(path).name
    stem = Path(name).stem
    for suffix in ("_Drum", "_FullMix", "_Full_Mix", "_MIX", "_Mix"):
        if stem.endswith(suffix):
            return stem[:-len(suffix)]
    return stem


def track_id_from_annotation_path(path, suffix):
    name = Path(path).name
    return name[:-len(suffix)] if name.endswith(suffix) else Path(path).stem


def discover_tracks(entries, audio_flavor="drum_only"):
    audio_prefix = f"MDB Drums/audio/{audio_flavor}/"
    audio_by_track = {}
    subclass_by_track = {}
    class_by_track = {}
    for entry in entries:
        path = entry.get("path", "")
        if path.startswith(audio_prefix) and path.lower().endswith(".wav"):
            audio_by_track[track_id_from_audio_path(path)] = path
        elif path.startswith("MDB Drums/annotations/subclass/") and path.endswith("_subclass.txt"):
            subclass_by_track[track_id_from_annotation_path(path, "_subclass.txt")] = path
        elif path.startswith("MDB Drums/annotations/class/") and path.endswith("_class.txt"):
            class_by_track[track_id_from_annotation_path(path, "_class.txt")] = path

    tracks = []
    for track_id in sorted(audio_by_track):
        annotation = subclass_by_track.get(track_id) or class_by_track.get(track_id)
        if not annotation:
            continue
        tracks.append({
            "id": track_id,
            "audio": audio_by_track[track_id],
            "annotation": annotation,
            "subclass": track_id in subclass_by_track,
        })
    return tracks


def parse_annotation(text, subclass=True):
    mapping = SUBCLASS_TO_GM if subclass else CLASS_TO_GM
    hits = []
    skipped = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            seconds = float(parts[0])
        except ValueError:
            continue
        label = parts[1].strip().upper()
        midi = mapping.get(label)
        if midi is None:
            skipped[label] = skipped.get(label, 0) + 1
            continue
        hits.append((seconds, midi, 96))
    hits.sort(key=lambda item: (item[0], item[1]))
    return hits, skipped


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
    return "|".join([
        FIXTURE_VERSION,
        f"source={args.source_root or RAW_BASE_URL}",
        f"audio_flavor={args.audio_flavor}",
        f"limit={args.limit}",
    ])


def cached_manifest_ok(output, signature, min_recordings):
    signature_path = output / ".mdb_drums_signature"
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
    """Clear a normal directory or an external sample-store symlink safely."""
    root = output.resolve(strict=True) if output.is_symlink() else output
    if output.is_symlink() and not root.is_dir():
        raise SystemExit(
            f"prepare_mdb_drums_samples: output symlink target is not a directory: {root}"
        )
    if not root.exists():
        return
    for attempt in range(4):
        try:
            for child in list(root.iterdir()):
                if child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                else:
                    child.unlink()
            if not any(root.iterdir()):
                return
        except OSError as exc:
            if exc.errno != errno.ENOTEMPTY:
                raise
        if attempt < 3:
            time.sleep(0.25 * (attempt + 1))
    remaining = ", ".join(child.name for child in root.iterdir()) or "(none)"
    raise OSError(
        f"prepare_mdb_drums_samples: could not clear {root} after retries; remaining: {remaining}"
    )


def prepare(args):
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    signature = signature_text(args)
    if not args.refresh and cached_manifest_ok(output, signature, max(1, args.min_recordings)):
        rows = list(csv.DictReader((output / "e-gmd-v1.0.0.csv").open("r", encoding="utf-8")))
        print(f"prepare_mdb_drums_samples: reused {output / 'e-gmd-v1.0.0.csv'} ({len(rows)} recordings)")
        return len(rows)

    entries = tree_entries(args.source_root, args.tree_json, args.timeout)
    tracks = discover_tracks(entries, args.audio_flavor)
    if args.limit > 0:
        tracks = tracks[:args.limit]
    if len(tracks) < args.min_recordings:
        raise SystemExit(
            f"prepare_mdb_drums_samples: expected at least {args.min_recordings} tracks, got {len(tracks)}"
        )

    reset_output(output)
    (output / "audio").mkdir(parents=True, exist_ok=True)
    (output / "midi").mkdir(parents=True, exist_ok=True)

    rows = []
    skipped_labels = {}
    for index, track in enumerate(tracks, 1):
        track_id = sanitize(track["id"])
        audio_relative = Path("audio") / f"{track_id}.wav"
        midi_relative = Path("midi") / f"{track_id}.mid"
        download_file(file_resource(track["audio"], args.source_root), output / audio_relative,
                      args.retries, args.timeout)
        annotation_text = read_text_resource(file_resource(track["annotation"], args.source_root), args.timeout)
        hits, skipped = parse_annotation(annotation_text, subclass=track["subclass"])
        if not hits:
            raise SystemExit(f"prepare_mdb_drums_samples: no supported drum hits in {track['annotation']}")
        for label, count in skipped.items():
            skipped_labels[label] = skipped_labels.get(label, 0) + count
        write_midi(output / midi_relative, hits)
        rows.append({
            "id": track_id,
            "audio_filename": str(audio_relative),
            "midi_filename": str(midi_relative),
        })
        if index % 5 == 0:
            print(f"prepare_mdb_drums_samples: prepared {index}/{len(tracks)} tracks...", flush=True)

    metadata = write_metadata(output, rows)
    (output / ".mdb_drums_signature").write_text(signature, encoding="utf-8")
    skipped_text = " ".join(f"{label}={count}" for label, count in sorted(skipped_labels.items()))
    print(
        f"prepare_mdb_drums_samples: wrote {metadata} ({len(rows)} recordings; "
        f"skipped {skipped_text or 'none'})",
        flush=True,
    )
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Prepare MDB Drums as an E-GMD-shaped drum fixture.")
    parser.add_argument("--output", default=os.environ.get("MDB_DRUMS_SAMPLE_DIR", "build/mdb_drums_samples"))
    parser.add_argument("--source-root", default=os.environ.get("MDB_DRUMS_SOURCE_ROOT", ""))
    parser.add_argument("--tree-json", default=os.environ.get("MDB_DRUMS_TREE_JSON", ""))
    parser.add_argument("--audio-flavor", choices=("drum_only", "full_mix"),
                        default=os.environ.get("MDB_DRUMS_AUDIO_FLAVOR", "full_mix"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("MDB_DRUMS_RECORDING_LIMIT", "0")))
    parser.add_argument("--min-recordings", type=int,
                        default=int(os.environ.get("MDB_DRUMS_MIN_RECORDINGS", "20")))
    parser.add_argument("--retries", type=int, default=int(os.environ.get("MDB_DRUMS_DOWNLOAD_RETRIES", "3")))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("MDB_DRUMS_TIMEOUT", "90")))
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("MDB_DRUMS_REFRESH") == "1")
    args = parser.parse_args()
    args.limit = max(0, args.limit)
    args.min_recordings = max(1, args.min_recordings)
    args.retries = max(1, args.retries)
    prepare(args)


if __name__ == "__main__":
    main()
