#!/usr/bin/env python3

import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request
import wave


FIXTURE_VERSION = "hf-guitar-chord-mix-v1"
DEFAULT_SOURCES = ("isolated-chords",)
HF_TREE_URL = (
    "https://huggingface.co/api/datasets/ryangowe/guitar-chord-mix/"
    "tree/main/clips/{source}?recursive=true&expand=false"
)
HF_RESOLVE_BASE_URL = "https://huggingface.co/datasets/ryangowe/guitar-chord-mix/resolve/main"
GUITAR_MIDI_RANGE = (40, 88)


def sanitize(text, limit=120):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def split_sources(text):
    values = [item.strip().strip("/") for item in text.split(",") if item.strip()]
    return values or list(DEFAULT_SOURCES)


def is_url(text):
    lowered = str(text).lower()
    return lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("file://")


def read_json_resource(resource, timeout):
    if is_url(resource):
        with urllib.request.urlopen(resource, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(resource).read_text(encoding="utf-8"))


def fetch_tree_entries(sources, tree_json, timeout):
    if tree_json:
        payload = read_json_resource(tree_json, timeout)
        if not isinstance(payload, list):
            raise SystemExit("prepare_hf_guitar_chord_mix: tree JSON must be a list")
        return payload

    entries = []
    for source in sources:
        url = HF_TREE_URL.format(source=urllib.parse.quote(source, safe="/"))
        payload = read_json_resource(url, timeout)
        if not isinstance(payload, list):
            raise SystemExit(f"prepare_hf_guitar_chord_mix: unexpected tree payload for {source}")
        entries.extend(payload)
    return entries


def chord_label_from_path(path):
    stem = Path(path).stem
    if "_" in stem:
        return stem.split("_", 1)[0]
    return stem


def pair_entries(entries, sources):
    source_prefixes = tuple(f"clips/{source}/" for source in sources)
    wav_by_stem = {}
    jams_by_stem = {}
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("type") != "file":
            continue
        path = str(entry.get("path", ""))
        if not path.startswith(source_prefixes):
            continue
        lowered = path.lower()
        if lowered.endswith(".wav"):
            wav_by_stem[path[:-4]] = path
        elif lowered.endswith(".jams"):
            jams_by_stem[path[:-5]] = path

    pairs = []
    for stem in sorted(set(wav_by_stem) & set(jams_by_stem)):
        label = chord_label_from_path(stem)
        pairs.append({
            "id": sanitize(stem.replace("/", "_")),
            "stem": stem,
            "label": label,
            "wav": wav_by_stem[stem],
            "jams": jams_by_stem[stem],
        })
    return pairs


def spread_pairs(pairs, limit):
    if limit <= 0 or len(pairs) <= limit:
        return pairs

    groups = {}
    for pair in pairs:
        groups.setdefault(pair["label"], []).append(pair)

    selected = []
    labels = sorted(groups)
    index = 0
    while len(selected) < limit:
        added = False
        for label in labels:
            bucket = groups[label]
            if index < len(bucket):
                selected.append(bucket[index])
                added = True
                if len(selected) >= limit:
                    break
        if not added:
            break
        index += 1
    return selected


def resource_url(base_url, path):
    return base_url.rstrip("/") + "/" + urllib.parse.quote(path, safe="/")


def download_file(url, output_path, retries, timeout):
    if output_path.is_file() and output_path.stat().st_size > 0:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".part")
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
            tmp.replace(output_path)
            return
        except (OSError, TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            if tmp.exists():
                tmp.unlink()
            if attempt + 1 < max(1, retries):
                time.sleep(min(2.0, 0.25 * (attempt + 1)))
    raise OSError(f"download failed for {url}: {last_error}")


def value_to_midi(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(round(value))
    if isinstance(value, dict):
        for key in ("midi_note", "note", "pitch", "value"):
            candidate = value.get(key)
            if isinstance(candidate, (int, float)) and not isinstance(candidate, bool):
                return int(round(candidate))
    return None


def parse_jams_notes(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    notes = []
    for annotation in payload.get("annotations", []):
        if not isinstance(annotation, dict):
            continue
        namespace = str(annotation.get("namespace", "")).lower().strip()
        if namespace not in ("note_midi", "midi_note"):
            continue
        rows = annotation.get("data", [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            midi = value_to_midi(row.get("value"))
            if midi is None or midi < GUITAR_MIDI_RANGE[0] or midi > GUITAR_MIDI_RANGE[1]:
                continue
            start = float(row.get("time", 0.0))
            duration = float(row.get("duration", 0.0))
            if duration <= 0.0:
                continue
            notes.append((start, start + duration, midi))
    notes.sort(key=lambda item: (item[0], item[2], item[1]))
    return notes


def valid_wav(path):
    try:
        with wave.open(str(path), "rb") as wav:
            return wav.getnframes() > 0 and wav.getframerate() > 0 and wav.getnchannels() > 0
    except (OSError, EOFError, wave.Error):
        return False


def signature_text(args, sources):
    payload = "|".join([
        FIXTURE_VERSION,
        f"sources={','.join(sources)}",
        f"limit={args.limit}",
        f"min_notes={args.min_notes}",
        f"min_pitch_classes={args.min_pitch_classes}",
        f"base={args.base_url}",
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def manifest_complete(path, signature, min_samples):
    if not path.is_file():
        return False
    rows = 0
    audio_paths = []
    saw_signature = False
    try:
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.rstrip("\n")
                if not line:
                    continue
                if line.startswith("# signature\t"):
                    saw_signature = line.split("\t", 1)[1] == signature
                if line.startswith("AUDIO\t"):
                    fields = line.split("\t")
                    if len(fields) < 3:
                        return False
                    rows += 1
                    audio_paths.append(fields[2])
        return saw_signature and rows >= max(1, min_samples) and all(Path(item).is_file() for item in audio_paths)
    except OSError:
        return False


def write_manifest(path, rows, signature):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        output.write("# HF guitar-chord-mix analyzer manifest v1\n")
        output.write(f"# signature\t{signature}\n")
        output.write("# source\thttps://huggingface.co/datasets/ryangowe/guitar-chord-mix\n")
        for row in rows:
            output.write(f"AUDIO\t{row['id']}\t{row['audio_path']}\n")
            for start, end, midi in row["notes"]:
                output.write(f"NOTE\t{row['id']}\t{start:.6f}\t{end:.6f}\t{midi}\n")


def prepare_pair(args, output_dir, pair):
    jams_path = output_dir / pair["jams"]
    wav_path = output_dir / pair["wav"]
    try:
        download_file(resource_url(args.base_url, pair["jams"]), jams_path, args.download_retries,
                      args.timeout)
        notes = parse_jams_notes(jams_path)
        pitch_classes = {midi % 12 for _, _, midi in notes}
        if len(notes) < args.min_notes or len(pitch_classes) < args.min_pitch_classes:
            return {"status": "sparse", "stem": pair["stem"]}

        download_file(resource_url(args.base_url, pair["wav"]), wav_path, args.download_retries,
                      args.timeout)
        if not args.skip_wav_check and not valid_wav(wav_path):
            return {"status": "invalid", "stem": pair["stem"]}
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return {"status": "error", "stem": pair["stem"], "reason": str(exc)}

    return {
        "status": "row",
        "row": {
            "id": pair["id"],
            "audio_path": str(wav_path.resolve()),
            "notes": notes,
            "label": pair["label"],
        },
    }


def prepare(args):
    sources = split_sources(args.sources)
    output_dir = Path(args.output)
    manifest_path = output_dir / "manifest.tsv"
    signature = signature_text(args, sources)
    min_samples = max(0, args.min_samples)

    if not args.refresh and manifest_complete(manifest_path, signature, min_samples):
        print(f"prepare_hf_guitar_chord_mix: keeping existing {manifest_path}")
        return

    entries = fetch_tree_entries(sources, args.tree_json, args.timeout)
    pairs = spread_pairs(pair_entries(entries, sources), args.limit)
    if not pairs:
        raise SystemExit("prepare_hf_guitar_chord_mix: no WAV/JAMS pairs found")

    rows = []
    skipped_sparse = 0
    skipped_invalid = 0
    skipped_errors = []
    processed = 0
    last_reported_prepared = 0

    def ordered_rows():
        return [row for _, row in sorted(rows, key=lambda item: item[0])]

    def record_result(index, result):
        nonlocal skipped_sparse, skipped_invalid, processed, last_reported_prepared
        processed += 1
        status = result.get("status")
        if status == "row":
            rows.append((index, result["row"]))
        elif status == "sparse":
            skipped_sparse += 1
        elif status == "invalid":
            skipped_invalid += 1
        elif status == "error":
            skipped_errors.append((result.get("stem", "<unknown>"), result.get("reason", "unknown error")))
        else:
            skipped_errors.append((result.get("stem", "<unknown>"), f"unknown result status {status!r}"))

        if args.progress_every > 0 and len(rows) >= last_reported_prepared + args.progress_every:
            last_reported_prepared = len(rows)
            print(
                f"prepare_hf_guitar_chord_mix: prepared {len(rows)} clips "
                f"({processed}/{len(pairs)} candidates)",
                flush=True,
            )

    try:
        jobs = max(1, args.jobs)
        if jobs == 1:
            for index, pair in enumerate(pairs, start=1):
                record_result(index, prepare_pair(args, output_dir, pair))
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
                futures = {
                    executor.submit(prepare_pair, args, output_dir, pair): index
                    for index, pair in enumerate(pairs, start=1)
                }
                for future in concurrent.futures.as_completed(futures):
                    index = futures[future]
                    record_result(index, future.result())
    except KeyboardInterrupt:
        if rows:
            partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
            write_manifest(partial_path, ordered_rows(), signature)
            print(
                f"prepare_hf_guitar_chord_mix: interrupted after {len(rows)} prepared clips; "
                f"wrote partial manifest {partial_path}",
                file=sys.stderr,
            )
        raise

    required = max(1, min_samples)
    if len(rows) < required:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, ordered_rows(), signature)
        raise SystemExit(
            f"prepare_hf_guitar_chord_mix: expected at least {required} prepared clips, "
            f"got {len(rows)}; wrote partial manifest {partial_path}"
        )

    prepared_rows = ordered_rows()
    write_manifest(manifest_path, prepared_rows, signature)
    labels = len({row["label"] for row in prepared_rows})
    note_count = sum(len(row["notes"]) for row in prepared_rows)
    print(
        f"prepare_hf_guitar_chord_mix: wrote {len(rows)} clips and {note_count} notes "
        f"across {labels} chord labels to {manifest_path} "
        f"(skipped_sparse {skipped_sparse}; skipped_invalid {skipped_invalid}; "
        f"skipped_errors {len(skipped_errors)})"
    )
    for sample_id, reason in skipped_errors[:12]:
        print(f"prepare_hf_guitar_chord_mix: skipped {sample_id}: {reason}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare Hugging Face guitar-chord-mix WAV/JAMS clips for analyzer_guitarset."
    )
    parser.add_argument("--output", default=os.environ.get("GUITAR_CHORD_MIX_SAMPLE_DIR",
                                                           "build/guitar_chord_mix_samples"))
    parser.add_argument("--sources", default=os.environ.get("GUITAR_CHORD_MIX_SOURCES",
                                                            ",".join(DEFAULT_SOURCES)))
    parser.add_argument("--tree-json", default=os.environ.get("GUITAR_CHORD_MIX_TREE_JSON", ""))
    parser.add_argument("--base-url", default=os.environ.get("GUITAR_CHORD_MIX_BASE_URL", HF_RESOLVE_BASE_URL))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("GUITAR_CHORD_MIX_LIMIT", "0")))
    parser.add_argument("--min-samples", type=int,
                        default=int(os.environ.get("GUITAR_CHORD_MIX_MIN_EXCERPTS", "500")))
    parser.add_argument("--min-notes", type=int, default=int(os.environ.get("GUITAR_CHORD_MIX_MIN_NOTES", "3")))
    parser.add_argument("--min-pitch-classes", type=int,
                        default=int(os.environ.get("GUITAR_CHORD_MIX_MIN_PITCH_CLASSES", "3")))
    parser.add_argument("--download-retries", type=int,
                        default=int(os.environ.get("GUITAR_CHORD_MIX_DOWNLOAD_RETRIES", "3")))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("GUITAR_CHORD_MIX_TIMEOUT", "45")))
    parser.add_argument("--progress-every", type=int,
                        default=int(os.environ.get("GUITAR_CHORD_MIX_PROGRESS_EVERY", "25")))
    parser.add_argument("--jobs", type=int, default=int(os.environ.get("GUITAR_CHORD_MIX_JOBS", "1")))
    parser.add_argument("--skip-wav-check", action="store_true",
                        default=os.environ.get("GUITAR_CHORD_MIX_SKIP_WAV_CHECK") == "1")
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("GUITAR_CHORD_MIX_REFRESH") == "1")
    args = parser.parse_args(argv)
    prepare(args)


if __name__ == "__main__":
    main()
