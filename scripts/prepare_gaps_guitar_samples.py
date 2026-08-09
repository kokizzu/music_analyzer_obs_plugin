#!/usr/bin/env python3

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request


FIXTURE_VERSION = "gaps-guitar-v2"
GAPS_METADATA_URL = "https://huggingface.co/datasets/xavriley/GAPS/raw/main/gaps_metadata_with_splits.csv"
GAPS_RESOLVE_BASE_URL = "https://huggingface.co/datasets/xavriley/GAPS/resolve/main"
GAPS_MATCH_TREE_URL = (
    "https://huggingface.co/api/datasets/xavriley/GAPS/tree/main/match?recursive=false&expand=false"
)
GUITAR_MIDI_RANGE = (40, 88)


def sanitize(text, limit=100):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def is_url(text):
    lowered = str(text).lower()
    return lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("file://")


def is_http_url(text):
    lowered = str(text).lower()
    return lowered.startswith("http://") or lowered.startswith("https://")


def read_json_resource(resource, timeout):
    if is_url(resource):
        request = urllib.request.Request(
            resource,
            headers={"User-Agent": "music-analyzer-obs-plugin-sample-prep/1.0"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(resource).read_text(encoding="utf-8"))


def resource_url(base_url, path):
    return base_url.rstrip("/") + "/" + urllib.parse.quote(str(path).lstrip("/"), safe="/")


def download_file(url, output_path, retries, timeout, offline=False):
    output_path = Path(output_path)
    if output_path.is_file() and output_path.stat().st_size > 0:
        return

    if offline:
        raise OSError(f"offline cache miss: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".part")
    last_error = None
    for attempt in range(max(1, retries)):
        try:
            if is_url(url):
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "music-analyzer-obs-plugin-sample-prep/1.0"},
                )
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    with tmp.open("wb") as file:
                        shutil.copyfileobj(response, file, length=1024 * 1024)
            else:
                shutil.copyfile(url, tmp)
            if tmp.stat().st_size <= 0:
                raise OSError("empty download")
            tmp.replace(output_path)
            return
        except (OSError, TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            if tmp.exists():
                tmp.unlink()
            if attempt + 1 < max(1, retries):
                time.sleep(min(2.0, 0.25 * (attempt + 1)))
    raise OSError(f"download failed for {url}: {last_error}")


def ensure_metadata(args):
    if args.metadata:
        return Path(args.metadata)

    source_dir = Path(args.source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)
    path = source_dir / "gaps_metadata_with_splits.csv"
    download_file(args.metadata_url, path, args.retries, args.timeout, args.offline)
    return path


def split_filter(text):
    values = [item.strip().lower() for item in text.split(",") if item.strip()]
    if not values or "all" in values:
        return None
    return set(values)


def read_metadata_rows(path, splits):
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            sample_id = str(row.get("id", "")).strip()
            audio_path = str(row.get("audio_path", "")).strip()
            if not sample_id or not audio_path:
                continue
            split = str(row.get("split", "")).strip().lower()
            if splits is not None and split not in splits:
                continue
            rows.append(row)
    rows.sort(key=lambda item: (str(item.get("split", "")), str(item.get("id", ""))))
    return rows


def spread_rows(rows, limit):
    if limit <= 0 or len(rows) <= limit:
        return rows

    groups = {}
    for row in rows:
        split = str(row.get("split", "")).strip().lower() or "unknown"
        groups.setdefault(split, []).append(row)

    selected = []
    splits = sorted(groups)
    index = 0
    while len(selected) < limit:
        added = False
        for split in splits:
            bucket = groups[split]
            if index < len(bucket):
                selected.append(bucket[index])
                added = True
                if len(selected) >= limit:
                    break
        if not added:
            break
        index += 1
    selected.sort(key=lambda item: str(item.get("id", "")))
    return selected


def parse_match_notes(path, min_duration):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    units_match = re.search(r"info\(midiClockUnits,([0-9.]+)\)", text)
    rate_match = re.search(r"info\(midiClockRate,([0-9.]+)\)", text)
    ticks_per_quarter = float(units_match.group(1)) if units_match else 480.0
    micros_per_quarter = float(rate_match.group(1)) if rate_match else 500000.0
    seconds_per_tick = micros_per_quarter / 1000000.0 / max(ticks_per_quarter, 1.0)

    notes = []
    seen = set()
    note_pattern = re.compile(r"(?<!s)note\([^,]+,([0-9]+),([0-9]+),([0-9]+),([0-9]+),")
    for match in note_pattern.finditer(text):
        midi = int(match.group(1))
        if midi < GUITAR_MIDI_RANGE[0] or midi > GUITAR_MIDI_RANGE[1]:
            continue
        start_tick = int(match.group(2))
        end_tick = int(match.group(3))
        if end_tick <= start_tick:
            continue
        start = start_tick * seconds_per_tick
        end = end_tick * seconds_per_tick
        if end - start < min_duration:
            continue
        key = (round(start, 6), round(end, 6), midi)
        if key in seen:
            continue
        seen.add(key)
        notes.append((start, end, midi))

    notes.sort(key=lambda item: (item[0], item[2], item[1]))
    return notes


def match_path_for_row(row):
    if row.get("match_path"):
        return str(row["match_path"]).strip()
    sample_id = str(row.get("id", "")).strip()
    midi_path = str(row.get("midi_path", "")).strip()
    stem = Path(midi_path).stem if midi_path else sample_id
    return f"match/{stem}.match"


def normalize_repo_path(path):
    return str(path).strip().replace("\\", "/").lstrip("/")


def fetch_available_match_paths(args):
    if args.no_match_tree:
        return None
    if not args.match_tree_json and not is_http_url(args.base_url):
        return None

    resource = args.match_tree_json or GAPS_MATCH_TREE_URL
    try:
        payload = read_json_resource(resource, args.timeout)
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"prepare_gaps_guitar_samples: match-tree prefilter unavailable: {exc}", file=sys.stderr)
        return None

    if not isinstance(payload, list):
        print("prepare_gaps_guitar_samples: match-tree prefilter unavailable: expected list JSON",
              file=sys.stderr)
        return None

    available = set()
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") not in (None, "file"):
            continue
        path = normalize_repo_path(entry.get("path", ""))
        if path.lower().endswith(".match"):
            available.add(path)

    if not available:
        print("prepare_gaps_guitar_samples: match-tree prefilter unavailable: no .match files",
              file=sys.stderr)
        return None
    return available


def signature_text(args):
    payload = "|".join([
        FIXTURE_VERSION,
        f"metadata={args.metadata or args.metadata_url}",
        f"base={args.base_url}",
        f"splits={args.splits}",
        f"limit={args.limit}",
        f"min_note_duration={args.min_note_duration}",
        f"match_tree={args.match_tree_json or ('off' if args.no_match_tree else 'auto')}",
        f"offline={args.offline}",
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def manifest_complete(path, signature, min_samples):
    if not path.is_file():
        return False
    audio_rows = 0
    note_rows = 0
    saw_signature = False
    audio_paths = []
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
                    if len(fields) < 3:
                        return False
                    audio_rows += 1
                    audio_paths.append(fields[2])
                elif line.startswith("NOTE\t"):
                    note_rows += 1
        return (
            saw_signature
            and audio_rows >= max(1, min_samples)
            and note_rows > 0
            and all(Path(item).is_file() for item in audio_paths)
        )
    except OSError:
        return False


def write_manifest(path, rows, signature):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        output.write("# GAPS guitar analyzer manifest v1\n")
        output.write(f"# signature\t{signature}\n")
        output.write("# source\thttps://huggingface.co/datasets/xavriley/GAPS\n")
        for row in rows:
            output.write(f"AUDIO\t{row['id']}\t{row['audio_path']}\n")
            for start, end, midi in row["notes"]:
                output.write(f"NOTE\t{row['id']}\t{start:.6f}\t{end:.6f}\t{midi}\n")


def prepare(args):
    output = Path(args.output)
    audio_dir = output / "audio"
    match_dir = output / "match"
    manifest = output / "manifest.tsv"
    signature = signature_text(args)

    if manifest_complete(manifest, signature, args.min_samples):
        print(f"prepare_gaps_guitar_samples: keeping existing {manifest}")
        return args.min_samples

    metadata = ensure_metadata(args)
    rows = spread_rows(read_metadata_rows(metadata, split_filter(args.splits)), 0)
    if not rows:
        raise SystemExit("prepare_gaps_guitar_samples: no metadata rows selected")

    available_matches = None if args.offline else fetch_available_match_paths(args)
    if args.offline:
        rows = [
            row for row in rows
            if (audio_dir / Path(str(row.get("audio_path", "")).strip()).name).is_file()
            and (match_dir / Path(match_path_for_row(row)).name).is_file()
        ]
        if not rows:
            raise SystemExit(
                "prepare_gaps_guitar_samples: offline cache has no complete audio/match pairs"
            )
    skipped_unavailable_match = 0
    prepared = []
    for index, row in enumerate(rows, start=1):
        sample_id = sanitize(str(row.get("id", "")).strip())
        audio_rel = str(row.get("audio_path", "")).strip()
        match_rel = match_path_for_row(row)
        if available_matches is not None and normalize_repo_path(match_rel) not in available_matches:
            skipped_unavailable_match += 1
            continue
        audio_path = audio_dir / Path(audio_rel).name
        match_path = match_dir / Path(match_rel).name

        try:
            download_file(resource_url(args.base_url, match_rel), match_path, args.retries,
                          args.timeout, args.offline)
            download_file(resource_url(args.base_url, audio_rel), audio_path, args.retries,
                          args.timeout, args.offline)
        except OSError as exc:
            print(f"prepare_gaps_guitar_samples: skipping {sample_id}: {exc}", file=sys.stderr)
            continue
        notes = parse_match_notes(match_path, args.min_note_duration)
        if len(notes) < args.min_notes:
            continue

        prepared.append({
            "id": sample_id,
            "audio_path": str(audio_path.resolve()),
            "notes": notes,
        })
        if args.progress_every > 0 and len(prepared) % args.progress_every == 0:
            print(f"prepare_gaps_guitar_samples: prepared {len(prepared)} clips...")
        if args.limit > 0 and len(prepared) >= args.limit:
            break

    target = manifest if len(prepared) >= args.min_samples else output / "manifest.tsv.partial"
    write_manifest(target, prepared, signature)
    if len(prepared) < args.min_samples:
        raise SystemExit(
            f"prepare_gaps_guitar_samples: expected at least {args.min_samples} clips, got {len(prepared)}"
        )

    print(
        f"prepare_gaps_guitar_samples: wrote {len(prepared)} clips and "
        f"{sum(len(row['notes']) for row in prepared)} notes to {manifest}"
        + (f" (prefilter skipped unavailable matches={skipped_unavailable_match})"
           if available_matches is not None else "")
    )
    return len(prepared)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare a bounded GAPS real-guitar AUDIO/NOTE manifest for analyzer_guitarset."
    )
    parser.add_argument("--metadata", default=os.environ.get("GAPS_GUITAR_METADATA", ""))
    parser.add_argument("--metadata-url", default=os.environ.get("GAPS_GUITAR_METADATA_URL", GAPS_METADATA_URL))
    parser.add_argument("--base-url", default=os.environ.get("GAPS_GUITAR_BASE_URL", GAPS_RESOLVE_BASE_URL))
    parser.add_argument("--match-tree-json", default=os.environ.get("GAPS_GUITAR_MATCH_TREE_JSON", ""))
    parser.add_argument("--no-match-tree", action="store_true",
                        default=os.environ.get("GAPS_GUITAR_NO_MATCH_TREE", "") not in ("", "0", "false", "FALSE"))
    parser.add_argument("--offline", action="store_true",
                        default=os.environ.get("GAPS_GUITAR_OFFLINE", "") not in ("", "0", "false", "FALSE"),
                        help="Use only cached audio and match files; never fetch missing inputs.")
    parser.add_argument("--source-dir", default=os.environ.get("GAPS_GUITAR_SOURCE_DIR",
                                                              "build/real_sample_sources/gaps"))
    parser.add_argument("--output", default=os.environ.get("GAPS_GUITAR_SAMPLE_DIR",
                                                          "build/gaps_guitar_samples"))
    parser.add_argument("--splits", default=os.environ.get("GAPS_GUITAR_SPLITS", "all"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("GAPS_GUITAR_SAMPLE_LIMIT", "4")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("GAPS_GUITAR_MIN_EXCERPTS", "4")))
    parser.add_argument("--min-notes", type=int, default=int(os.environ.get("GAPS_GUITAR_MIN_NOTES", "12")))
    parser.add_argument("--min-note-duration", type=float,
                        default=float(os.environ.get("GAPS_GUITAR_MIN_NOTE_DURATION", "0.04")))
    parser.add_argument("--retries", type=int, default=int(os.environ.get("GAPS_GUITAR_RETRIES", "3")))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("GAPS_GUITAR_TIMEOUT", "120")))
    parser.add_argument("--progress-every", type=int,
                        default=int(os.environ.get("GAPS_GUITAR_PROGRESS_EVERY", "2")))
    args = parser.parse_args(argv)

    prepare(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
