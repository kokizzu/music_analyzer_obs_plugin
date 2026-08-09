#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib import parse, request


DATASET = "collegefishiesd/guitar-fretboard-notes"
CONFIG = "default"
SPLITS = ("train", "test", "validation")
ROWS_ENDPOINT = "https://datasets-server.huggingface.co/rows"


def sanitize(text):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:80] or "sample"


def fetch_json(url, retries=3, sleep_seconds=1.0):
    last_error = None
    for attempt in range(max(1, retries)):
        try:
            with request.urlopen(url, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - exact urllib errors vary by platform.
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(sleep_seconds)
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def download_file(url, path, retries=3, sleep_seconds=1.0):
    if path.is_file() and path.stat().st_size > 0:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    last_error = None
    for attempt in range(max(1, retries)):
        try:
            with request.urlopen(url, timeout=120) as response:
                tmp.write_bytes(response.read())
            if tmp.stat().st_size <= 0:
                raise RuntimeError("empty download")
            tmp.replace(path)
            return
        except Exception as exc:  # pragma: no cover - exact urllib errors vary by platform.
            last_error = exc
            if tmp.exists():
                tmp.unlink()
            if attempt + 1 < retries:
                time.sleep(sleep_seconds)
    raise RuntimeError(f"failed to download {url}: {last_error}")


def rows_url(split, offset, length):
    query = parse.urlencode(
        {
            "dataset": DATASET,
            "config": CONFIG,
            "split": split,
            "offset": offset,
            "length": length,
        }
    )
    return f"{ROWS_ENDPOINT}?{query}"


def iter_rows(splits, page_size, limit, retries):
    emitted = 0
    for split in splits:
        offset = 0
        while True:
            payload = fetch_json(rows_url(split, offset, page_size), retries=retries)
            rows = payload.get("rows", [])
            total = int(payload.get("num_rows_total", offset + len(rows)))
            if not rows:
                break

            for item in rows:
                yield split, item["row_idx"], item["row"]
                emitted += 1
                if limit > 0 and emitted >= limit:
                    return

            offset += len(rows)
            if offset >= total:
                break


def write_manifest(output, manifest_rows):
    manifest = output / "manifest.tsv"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output,
                                     prefix=".manifest.tsv.", suffix=".tmp",
                                     delete=False) as file:
        tmp = Path(file.name)
        file.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\n")
        for row in manifest_rows:
            file.write("\t".join(row) + "\n")
    try:
        tmp.replace(manifest)
    except Exception:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise
    return manifest


def existing_manifest_count(output):
    manifest = Path(output) / "manifest.tsv"
    if not manifest.is_file():
        return 0
    try:
        with manifest.open("r", encoding="utf-8", newline="") as file:
            rows = list(file)
    except OSError:
        return 0
    if not rows or not rows[0].startswith("id\tfamily\t"):
        return 0
    count = 0
    for line in rows[1:]:
        fields = line.rstrip("\n").split("\t")
        if len(fields) != 7 or not fields[6] or not (Path(output) / fields[6]).is_file():
            return 0
        count += 1
    return count


def prepare(output, splits=SPLITS, page_size=100, limit=0, retries=3, offline=False):
    output = Path(output)
    audio_root = output / "audio"
    output.mkdir(parents=True, exist_ok=True)
    audio_root.mkdir(parents=True, exist_ok=True)

    cached_count = existing_manifest_count(output)
    if cached_count and (limit <= 0 or cached_count >= limit):
        print(f"prepare_guitar_fretboard_notes: keeping existing {output / 'manifest.tsv'} "
              f"({cached_count} samples)")
        return cached_count
    if offline:
        raise RuntimeError(
            "offline cache miss: Guitar Fretboard manifest is missing or below the requested limit"
        )

    manifest_rows = []
    for split, row_index, row in iter_rows(splits, page_size, limit, retries):
        audio = row.get("audio") or []
        if not audio or not audio[0].get("src"):
            continue

        source = str(row.get("source", "unknown"))
        guitar_type = str(row.get("guitar_type", "guitar"))
        string_name = str(row.get("string_name", "string"))
        fret = int(row.get("fret", 0))
        midi = int(row.get("midi_number"))
        note = str(row.get("note_name") or "")
        sample_id = f"{split}_{row_index:04d}_{source}_{string_name}_f{fret}_{note}"
        filename = sanitize(sample_id) + ".wav"
        relative_path = Path("audio") / filename
        download_file(audio[0]["src"], output / relative_path, retries=retries)

        manifest_rows.append(
            (
                sample_id,
                "guitar",
                "guitar_fretboard_notes",
                f"{guitar_type}:{source}:{string_name}:f{fret}",
                str(midi),
                note,
                str(relative_path),
            )
        )
        if len(manifest_rows) % 25 == 0:
            print(f"prepare_guitar_fretboard_notes: downloaded {len(manifest_rows)} samples...")

    manifest = write_manifest(output, manifest_rows)
    print(f"prepare_guitar_fretboard_notes: wrote {manifest} ({len(manifest_rows)} samples)")
    return len(manifest_rows)


def main():
    parser = argparse.ArgumentParser(
        description="Download the Hugging Face guitar-fretboard single-note dataset into a real-note fixture."
    )
    parser.add_argument("--output", default=os.environ.get("GUITAR_FRETBOARD_NOTES_SAMPLE_DIR",
                                                           "build/guitar_fretboard_notes_samples"))
    parser.add_argument("--splits", default=os.environ.get("GUITAR_FRETBOARD_NOTES_SPLITS",
                                                          ",".join(SPLITS)))
    parser.add_argument("--page-size", type=int, default=int(os.environ.get("GUITAR_FRETBOARD_NOTES_PAGE_SIZE",
                                                                            "100")))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("GUITAR_FRETBOARD_NOTES_LIMIT", "0")))
    parser.add_argument("--retries", type=int, default=int(os.environ.get("GUITAR_FRETBOARD_NOTES_RETRIES", "3")))
    parser.add_argument("--offline", action="store_true",
                        default=os.environ.get("GUITAR_FRETBOARD_NOTES_OFFLINE", "") not in ("", "0", "false", "FALSE"),
                        help="Reuse only a complete cached manifest; never access the dataset service.")
    args = parser.parse_args()

    splits = tuple(split.strip() for split in args.splits.split(",") if split.strip())
    count = prepare(args.output, splits=splits, page_size=max(1, args.page_size),
                    limit=max(0, args.limit), retries=max(1, args.retries), offline=args.offline)
    if count == 0:
        raise SystemExit("prepare_guitar_fretboard_notes: no samples prepared")


if __name__ == "__main__":
    main()
