#!/usr/bin/env python3
"""Build a bounded labelled Tom/Ride/Rim fixture from ENST-Drums.

The YourMT3 archive keeps a declared-articulation annotation beside several
microphone renders of the same performance.  This fixture uses `dry_mix` only,
so the microphone variants of one hit pattern cannot inflate the evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import re
import shutil
import tarfile
import tempfile
import wave
from pathlib import Path, PurePosixPath


FIXTURE_VERSION = "enst-drums-tom-ride-rim-v2-crossstick"
CATEGORIES = ("rim", "tom", "ride")
HEADER = ("category", "path", "duration_seconds", "events", "source", "signature")


def safe_parts(name: str) -> tuple[str, ...] | None:
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path.parts


def category_for_annotation(name: str) -> str | None:
    parts = safe_parts(name)
    if parts is None or len(parts) < 4 or parts[-2] != "annotation" or Path(parts[-1]).suffix != ".txt":
        return None
    stem = Path(parts[-1]).stem.lower()
    # ENST separately declares rim-shots and cross-sticks.  Both are labelled
    # stick-on-rim articulations, matching the Rim/Cross-stick class used by
    # the existing independent one-shot fixtures.
    if "hits_rim-shot" in stem or "hits_cross-sticks" in stem:
        return "rim"
    if "hits_medium-tom" in stem or "hits_low-tom" in stem:
        return "tom"
    if any(token in stem for token in ("hits_ride-cymbal", "hits_flat-ride-cymbal", "hits_chinese-ride-cymbal")):
        return "ride"
    return None


def dry_mix_name(annotation_name: str) -> str:
    parts = safe_parts(annotation_name)
    if parts is None:
        raise ValueError(f"unsafe annotation path: {annotation_name}")
    return str(PurePosixPath(*parts[:-2], "audio", "dry_mix", parts[-1]).with_suffix(".wav"))


def annotation_event_count(data: bytes) -> int:
    return sum(1 for line in data.decode("utf-8", errors="replace").splitlines() if line.strip())


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
    counts = {category: 0 for category in CATEGORIES}
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


def write_manifest(output: Path, rows: list[tuple[str, str, str, str, str, str]]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output, prefix=".manifest.",
                                     suffix=".tmp", delete=False) as destination:
        temporary = Path(destination.name)
        destination.write("\t".join(HEADER) + "\n")
        for row in rows:
            destination.write("\t".join(row) + "\n")
    temporary.replace(output / "manifest.tsv")


def generated_manifest(path: Path) -> bool:
    if not path.is_file():
        return False
    rows = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return bool(rows and tuple(rows[0].split("\t")) == HEADER and
                all("\tENST-Drums:" in row for row in rows[1:]))


def prepare(archive: Path, output: Path, limit: int, minimum: int, reset_generated: bool = False) -> dict[str, int]:
    if not archive.is_file():
        raise RuntimeError(f"missing archive: {archive}")
    output.mkdir(parents=True, exist_ok=True)
    current_signature = signature(archive, limit, minimum)
    manifest = output / "manifest.tsv"
    if read_complete_manifest(manifest, current_signature, minimum):
        return {category: sum(1 for row in manifest.read_text(encoding="utf-8").splitlines()[1:]
                              if row.startswith(category + "\t")) for category in CATEGORIES}
    if any(output.iterdir()):
        if not reset_generated or (manifest.exists() and not generated_manifest(manifest)):
            raise RuntimeError(f"{output}: refuses to replace an incomplete or mismatched generated fixture")
        # Only an explicitly requested ENST-generated fixture is reset.
        # Resolve a build symlink so the external-store link itself is preserved.
        shutil.rmtree(output.resolve() if output.is_symlink() else output)
        output.mkdir(parents=True, exist_ok=True)

    candidates = {category: [] for category in CATEGORIES}
    with tarfile.open(archive, "r:gz") as source:
        names = {member.name for member in source if member.isfile()}
        for name in sorted(names):
            category = category_for_annotation(name)
            if category is not None and dry_mix_name(name) in names:
                candidates[category].append(name)
    chosen = {category: selected(candidates[category], limit) for category in CATEGORIES}
    missing = [f"{category}={len(chosen[category])}" for category in CATEGORIES
               if len(chosen[category]) < minimum]
    if missing:
        raise RuntimeError("insufficient declared ENST articulations: " + ", ".join(missing))

    selected_rows: dict[str, tuple[str, str, Path]] = {}
    for category in CATEGORIES:
        for index, annotation_name in enumerate(chosen[category], start=1):
            relative = Path(category) / f"{index:03d}_{sanitize(Path(annotation_name).stem)}.wav"
            selected_rows[annotation_name] = (category, dry_mix_name(annotation_name), relative)
    events: dict[str, int] = {}
    durations: dict[str, float] = {}
    # Streaming mode avoids a compressed-tar seek for every selected sample.
    # The first scan chose the bounded names; this scan extracts them in archive
    # order, doing at most two sequential decompressions of the source archive.
    audio_to_annotation = {audio_name: annotation_name for annotation_name, (_, audio_name, _)
                           in selected_rows.items()}
    with tarfile.open(archive, "r|gz") as source:
        for member in source:
            if not member.isfile() or (member.name not in selected_rows and member.name not in audio_to_annotation):
                continue
            contents = source.extractfile(member)
            if contents is None:
                raise RuntimeError(f"unreadable ENST member: {member.name}")
            data = contents.read()
            if member.name in selected_rows:
                events[member.name] = annotation_event_count(data)
                continue
            annotation_name = audio_to_annotation[member.name]
            duration = duration_seconds(data)
            if duration is None:
                raise RuntimeError(f"invalid WAV: {member.name}")
            _, _, relative = selected_rows[annotation_name]
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(destination.suffix + ".tmp")
            temporary.write_bytes(data)
            temporary.replace(destination)
            durations[annotation_name] = duration

    rows: list[tuple[str, str, str, str, str, str]] = []
    for annotation_name, (category, audio_name, relative) in selected_rows.items():
        if annotation_name not in events or annotation_name not in durations:
            raise RuntimeError(f"missing paired ENST members for {annotation_name}")
        rows.append((category, str(relative), f"{durations[annotation_name]:.6f}",
                     str(events[annotation_name]), f"ENST-Drums:{audio_name}", current_signature))
    counts = {category: sum(row[0] == category for row in rows) for category in CATEGORIES}
    if any(counts[category] < minimum for category in CATEGORIES):
        raise RuntimeError("invalid WAV count: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    write_manifest(output, rows)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit-per-category", type=int, default=32)
    parser.add_argument("--min-per-category", type=int, default=1)
    parser.add_argument("--reset-generated", action="store_true",
                        help="reset only a generated ENST fixture")
    args = parser.parse_args()
    try:
        counts = prepare(args.archive, args.output, max(0, args.limit_per_category), max(1, args.min_per_category),
                         reset_generated=args.reset_generated)
    except (OSError, RuntimeError, tarfile.TarError) as error:
        parser.error(str(error))
    print("prepare_enst_drums_samples: " + str(args.output / "manifest.tsv") + " " +
          " ".join(f"{category}={counts[category]}" for category in CATEGORIES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
