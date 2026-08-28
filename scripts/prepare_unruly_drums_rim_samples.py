#!/usr/bin/env python3
"""Convert a bounded, evenly-spread Unruly Drums rimshot subset to WAV."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import wave
import zipfile
from pathlib import Path


def rimshot_members(archive: zipfile.ZipFile) -> list[str]:
    return [
        info.filename for info in archive.infolist()
        if not info.is_dir()
        and info.filename.lower().endswith(".flac")
        and "rimshot" in Path(info.filename).name.lower()
    ]


def spread(items: list[str], limit: int) -> list[str]:
    if len(items) <= limit:
        return items
    return [items[index * len(items) // limit] for index in range(limit)]


def convert(ffmpeg: str, source: Path, destination: Path) -> None:
    subprocess.run(
        [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
         "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(destination)],
        check=True,
    )


def duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=96)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()

    ffmpeg = shutil.which(args.ffmpeg) if "/" not in args.ffmpeg else args.ffmpeg
    if not ffmpeg:
        raise SystemExit(f"prepare_unruly_drums_rim_samples: ffmpeg not found: {args.ffmpeg}")
    if not args.archive.is_file():
        raise SystemExit(f"prepare_unruly_drums_rim_samples: archive not found: {args.archive}")
    if args.limit < 1:
        raise SystemExit("prepare_unruly_drums_rim_samples: --limit must be positive")

    with zipfile.ZipFile(args.archive) as source:
        selected = spread(sorted(rimshot_members(source)), args.limit)
        if not selected:
            raise SystemExit("prepare_unruly_drums_rim_samples: no rimshot FLAC members found")
        cache = args.output / ".source_flac"
        rim_output = args.output / "rim"
        cache.mkdir(parents=True, exist_ok=True)
        rim_output.mkdir(parents=True, exist_ok=True)
        rows: list[tuple[str, str, float, str]] = []
        for index, member in enumerate(selected, 1):
            cached = cache / f"{index:03d}_{Path(member).name}"
            destination = rim_output / f"{index:03d}_{Path(member).stem}.wav"
            if not destination.is_file():
                cached.write_bytes(source.read(member))
                convert(ffmpeg, cached, destination)
            rows.append(("rim", str(destination.relative_to(args.output)), duration_seconds(destination),
                         f"{args.archive}!{member}"))

    manifest = args.output / "manifest.tsv"
    with manifest.open("w", encoding="utf-8") as handle:
        handle.write("category\tpath\tduration_seconds\tsource\n")
        for category, relative, duration, source in rows:
            handle.write(f"{category}\t{relative}\t{duration:.6f}\t{source}\n")
    print(f"prepare_unruly_drums_rim_samples: wrote {manifest} (rim={len(rows)})")


if __name__ == "__main__":
    main()
