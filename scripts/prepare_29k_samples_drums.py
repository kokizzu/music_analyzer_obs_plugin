#!/usr/bin/env python3
"""Build a bounded, labelled Tom/Ride fixture from 29kSamplesDrumsDataset."""

from __future__ import annotations

import argparse
import hashlib
import io
import re
import tempfile
import wave
import zipfile
from pathlib import Path, PurePosixPath


FIXTURE_VERSION = "29k-samples-drums-tom-ride-v1"
HEADER = ("category", "path", "duration_seconds", "source", "signature")
COMPONENT_CATEGORY = {"ft": "tom", "mt": "tom", "ht": "tom", "cy": "ride"}


def safe_parts(name: str) -> tuple[str, ...] | None:
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path.parts


def category_for(name: str) -> str | None:
    parts = safe_parts(name)
    if parts is None or Path(parts[-1]).suffix.lower() != ".wav":
        return None
    if parts[0] == "__MACOSX":
        return None
    # The published class name is the immediate parent.  A combined folder
    # such as ft+kd is not a pure Tom ground-truth sample, even though it
    # contains a Tom code in its name.
    return COMPONENT_CATEGORY.get(parts[-2].lower()) if len(parts) >= 2 else None


def duration_seconds(data: bytes) -> float | None:
    try:
        with wave.open(io.BytesIO(data), "rb") as source:
            if source.getframerate() <= 0 or source.getnframes() <= 0:
                return None
            return source.getnframes() / source.getframerate()
    except (wave.Error, EOFError):
        return None


def signature(archive: Path, limit: int, minimum: int) -> str:
    stat = archive.stat()
    payload = f"{FIXTURE_VERSION}|{archive.name}|{stat.st_size}|{stat.st_mtime_ns}|{limit}|{minimum}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def sanitize(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-")[:180] or "sample"


def selected(names: list[str], limit: int) -> list[str]:
    if limit <= 0 or len(names) <= limit:
        return names
    if limit == 1:
        return [names[len(names) // 2]]
    return [names[round(index * (len(names) - 1) / (limit - 1))] for index in range(limit)]


def read_complete_manifest(path: Path, expected_signature: str, minimum: int) -> bool:
    if not path.is_file():
        return False
    counts = {"tom": 0, "ride": 0}
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        fields = line.split("\t")
        if index == 0:
            if tuple(fields) != HEADER:
                return False
            continue
        if len(fields) != len(HEADER) or fields[0] not in counts or fields[-1] != expected_signature:
            return False
        if not (path.parent / fields[1]).is_file():
            return False
        counts[fields[0]] += 1
    return all(count >= minimum for count in counts.values())


def write_manifest(output: Path, rows: list[tuple[str, str, str, str, str]]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output, prefix=".manifest.",
                                     suffix=".tmp", delete=False) as destination:
        temporary = Path(destination.name)
        destination.write("\t".join(HEADER) + "\n")
        for row in rows:
            destination.write("\t".join(row) + "\n")
    temporary.replace(output / "manifest.tsv")


def prepare(archive: Path, output: Path, limit: int, minimum: int) -> int:
    if not archive.is_file():
        raise RuntimeError(f"missing archive: {archive}")
    output.mkdir(parents=True, exist_ok=True)
    current_signature = signature(archive, limit, minimum)
    manifest = output / "manifest.tsv"
    if read_complete_manifest(manifest, current_signature, minimum):
        print(f"prepare_29k_samples_drums: reused {manifest}")
        return sum(1 for _ in manifest.read_text(encoding="utf-8").splitlines()[1:])

    with zipfile.ZipFile(archive) as source:
        candidates = {"tom": [], "ride": []}
        for item in source.infolist():
            if item.is_dir() or item.flag_bits & 0x1:
                continue
            category = category_for(item.filename)
            if category:
                candidates[category].append(item.filename)
        rows = []
        for category in sorted(candidates):
            names = selected(sorted(candidates[category]), limit)
            if len(names) < minimum:
                raise RuntimeError(f"{category}: found {len(names)} samples, need {minimum}")
            for index, member in enumerate(names, start=1):
                data = source.read(member)
                duration = duration_seconds(data)
                if duration is None:
                    continue
                relative = Path(category) / f"{index:05d}_{sanitize(member)}"
                destination = output / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                temporary = destination.with_suffix(destination.suffix + ".tmp")
                temporary.write_bytes(data)
                temporary.replace(destination)
                rows.append((category, str(relative), f"{duration:.6f}",
                             f"29kSamplesDrumsDataset:{member}", current_signature))
    counts = {category: sum(row[0] == category for row in rows) for category in ("tom", "ride")}
    if any(counts[category] < minimum for category in counts):
        raise RuntimeError("invalid WAV count: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    write_manifest(output, rows)
    print("prepare_29k_samples_drums: wrote " + str(manifest) + " " +
          " ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit-per-category", type=int, default=600)
    parser.add_argument("--min-per-category", type=int, default=500)
    args = parser.parse_args()
    try:
        prepare(args.archive, args.output, max(0, args.limit_per_category), max(1, args.min_per_category))
    except (OSError, RuntimeError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
