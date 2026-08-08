#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib import parse, request


DATASET = "airasoul/drum-kit"
CONFIG = "default"
SPLITS = ("train", "test")
ROWS_ENDPOINT = "https://datasets-server.huggingface.co/rows"
LABEL_MAP = {
    "kick": "kick",
    "snare": "snare",
    "hat": "hihat",
    "crash": "crash",
    "tom": "tom",
    "ride": "ride",
    "rim": "rim",
}


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


def iter_rows(splits, page_size, retries):
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

            offset += len(rows)
            if offset >= total:
                break


def write_manifest(output, manifest_rows):
    manifest = output / "manifest.tsv"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output,
                                     prefix=".manifest.tsv.", suffix=".tmp",
                                     delete=False) as file:
        tmp = Path(file.name)
        file.write("category\tpath\tduration_seconds\tsource\n")
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


def read_cached_manifest(output):
    manifest = output / "manifest.tsv"
    if not manifest.is_file():
        return [], {category: 0 for category in LABEL_MAP.values()}

    rows = []
    counts = {category: 0 for category in LABEL_MAP.values()}
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines()):
        if line_number == 0:
            continue
        columns = line.split("\t")
        if len(columns) < 4:
            continue
        category, relative_path, duration, source = columns[:4]
        if category not in counts:
            continue
        sample_path = output / relative_path
        if not sample_path.is_file() or sample_path.stat().st_size <= 0:
            continue
        counts[category] += 1
        rows.append((category, relative_path, duration, source))
    return rows, counts


def cache_satisfies(counts, required_per_category):
    if required_per_category <= 0:
        return False
    return all(counts.get(category, 0) >= required_per_category for category in LABEL_MAP.values())


def counts_text(counts):
    return " ".join(f"{category}={counts[category]}" for category in sorted(counts))


def prepare(output, splits=SPLITS, page_size=100, limit_per_category=0, retries=3,
            cache_min_per_category=300, manifest_checkpoint=50):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for category in LABEL_MAP.values():
        (output / category).mkdir(parents=True, exist_ok=True)

    cached_rows, cached_counts = read_cached_manifest(output)
    required_cache_count = limit_per_category if limit_per_category > 0 else cache_min_per_category
    if cache_satisfies(cached_counts, required_cache_count):
        print(f"prepare_hf_drum_kit_samples: reused {output / 'manifest.tsv'} "
              f"({counts_text(cached_counts)})", flush=True)
        return len(cached_rows)

    counts = dict(cached_counts)
    skipped = {}
    manifest_rows = list(cached_rows)
    cached_sources = {source for _category, _path, _duration, source in cached_rows}
    pending_since_manifest = 0
    try:
        row_iter = iter_rows(splits, page_size, retries)
        for split, row_index, row in row_iter:
            label = str(row.get("label", "")).strip().lower()
            category = LABEL_MAP.get(label)
            if not category:
                skipped[label or "<empty>"] = skipped.get(label or "<empty>", 0) + 1
                continue
            if limit_per_category > 0 and counts[category] >= limit_per_category:
                continue

            audio = row.get("audio") or []
            if not audio or not audio[0].get("src"):
                skipped[f"{label}:no_audio"] = skipped.get(f"{label}:no_audio", 0) + 1
                continue

            source = f"{DATASET}:{split}:{row_index}:{label}"
            if source in cached_sources:
                continue
            counts[category] += 1
            sample_id = f"{split}_{row_index:04d}_{label}_{counts[category]:04d}"
            relative_path = Path(category) / (sanitize(sample_id) + ".wav")
            download_file(audio[0]["src"], output / relative_path, retries=retries)
            manifest_rows.append((category, str(relative_path), "0.000000", source))
            cached_sources.add(source)
            pending_since_manifest += 1
            if pending_since_manifest >= manifest_checkpoint:
                write_manifest(output, manifest_rows)
                pending_since_manifest = 0
                print(f"prepare_hf_drum_kit_samples: downloaded {len(manifest_rows)} samples...", flush=True)
    except RuntimeError as exc:
        if cache_satisfies(cached_counts, required_cache_count):
            print(f"prepare_hf_drum_kit_samples: reused cached manifest after fetch failure: {exc}",
                  flush=True)
            return len(cached_rows)
        raise

    manifest = write_manifest(output, manifest_rows)
    skipped_text = " ".join(f"{label}={count}" for label, count in sorted(skipped.items()))
    print(f"prepare_hf_drum_kit_samples: wrote {manifest} ({counts_text(counts)}; skipped {skipped_text or 'none'})",
          flush=True)
    missing = [category for category, count in counts.items() if count == 0]
    if missing:
        raise SystemExit("prepare_hf_drum_kit_samples: missing categories: " + ", ".join(missing))
    return len(manifest_rows)


def main():
    parser = argparse.ArgumentParser(description="Download airasoul/drum-kit one-shots into a drum fixture.")
    parser.add_argument("--output", default=os.environ.get("HF_DRUM_KIT_SAMPLE_DIR",
                                                           "build/hf_drum_kit_samples"))
    parser.add_argument("--splits", default=os.environ.get("HF_DRUM_KIT_SPLITS", ",".join(SPLITS)))
    parser.add_argument("--page-size", type=int, default=int(os.environ.get("HF_DRUM_KIT_PAGE_SIZE", "100")))
    parser.add_argument("--limit-per-category", type=int,
                        default=int(os.environ.get("HF_DRUM_KIT_LIMIT_PER_CATEGORY", "0")))
    parser.add_argument("--retries", type=int, default=int(os.environ.get("HF_DRUM_KIT_RETRIES", "3")))
    parser.add_argument("--cache-min-per-category", type=int,
                        default=int(os.environ.get("HF_DRUM_KIT_CACHE_MIN_PER_CATEGORY", "300")))
    parser.add_argument("--manifest-checkpoint", type=int,
                        default=int(os.environ.get("HF_DRUM_KIT_MANIFEST_CHECKPOINT", "50")))
    args = parser.parse_args()

    splits = tuple(split.strip() for split in args.splits.split(",") if split.strip())
    count = prepare(args.output, splits=splits, page_size=max(1, args.page_size),
                    limit_per_category=max(0, args.limit_per_category), retries=max(1, args.retries),
                    cache_min_per_category=max(1, args.cache_min_per_category),
                    manifest_checkpoint=max(1, args.manifest_checkpoint))
    if count == 0:
        raise SystemExit("prepare_hf_drum_kit_samples: no samples downloaded")


if __name__ == "__main__":
    main()
