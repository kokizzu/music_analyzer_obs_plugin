#!/usr/bin/env python3
"""Prepare external-only Iowa piano sustains for continuous Vocal precision checks."""

from __future__ import annotations

import csv
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = Path(__import__("os").environ.get(
    "MUSIC_ANALYZER_FIXTURE_CACHE", "/media/kyz/sshflashtor/InstrumentSamples/build-cache"
))
SOURCE_ROOT = REPO_ROOT / "build" / "iowa_piano_samples"
DESTINATION = CACHE_ROOT / "iowa_piano_temporal_controls"
OUTPUT_LINK = REPO_ROOT / "build" / "iowa_piano_temporal_controls"
TARGET_IDS = ("Piano.mf.C3", "Piano.mf.E3", "Piano.mf.G3", "Piano.mf.C4", "Piano.mf.E4", "Piano.mf.G4")
HEADER = ("id", "family", "nsynth_family", "source", "midi", "note", "path", "details")


def ensure_link() -> None:
    OUTPUT_LINK.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT_LINK.is_symlink() and OUTPUT_LINK.resolve() == DESTINATION:
        return
    if OUTPUT_LINK.exists() or OUTPUT_LINK.is_symlink():
        raise RuntimeError(f"refusing to replace nonmatching control link: {OUTPUT_LINK}")
    OUTPUT_LINK.symlink_to(DESTINATION)


def rows() -> list[dict[str, str]]:
    manifest = SOURCE_ROOT / "manifest.tsv"
    if not manifest.is_file():
        raise RuntimeError(f"missing Iowa piano manifest: {manifest}")
    with manifest.open(encoding="utf-8", newline="") as source:
        by_id = {row["id"]: row for row in csv.DictReader(source, delimiter="\t")}
    missing = [sample_id for sample_id in TARGET_IDS if sample_id not in by_id]
    if missing:
        raise RuntimeError(f"missing Iowa piano controls: {', '.join(missing)}")
    return [by_id[sample_id] for sample_id in TARGET_IDS]


def manifest_text(selected: list[dict[str, str]]) -> str:
    lines = ["\t".join(HEADER)]
    for row in selected:
        output = f"audio/{row['id']}.wav"
        lines.append("\t".join((
            f"iowa_temporal_{row['id']}", "piano", "keyboard", "iowa-piano-temporal-control",
            row["midi"], row["note"], output, "duration=2.00,source=Iowa Piano",
        )))
    return "\n".join(lines) + "\n"


def apply(ffmpeg: str) -> int:
    if not shutil.which(ffmpeg):
        raise RuntimeError(f"ffmpeg is required but was not found: {ffmpeg}")
    selected = rows()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    ensure_link()
    audio = DESTINATION / "audio"
    audio.mkdir(exist_ok=True)
    for row in selected:
        source = SOURCE_ROOT / row["path"]
        if not source.is_file():
            raise RuntimeError(f"missing Iowa source audio: {source}")
        target = audio / f"{row['id']}.wav"
        if target.is_file():
            continue
        temporary = target.with_suffix(".tmp.wav")
        subprocess.run([
            ffmpeg, "-v", "error", "-y", "-ss", "0", "-t", "2.00", "-i", str(source),
            "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(temporary),
        ], check=True)
        temporary.replace(target)
    manifest = DESTINATION / "manifest.tsv"
    temporary_manifest = manifest.with_suffix(".tmp")
    temporary_manifest.write_text(manifest_text(selected), encoding="utf-8")
    temporary_manifest.replace(manifest)
    print(f"link={OUTPUT_LINK} -> {DESTINATION}")
    print(f"controls={len(selected)}")
    return 0


def verify() -> int:
    expected = len(TARGET_IDS)
    audio = DESTINATION / "audio"
    actual = len(list(audio.glob("*.wav"))) if audio.is_dir() else 0
    manifest = DESTINATION / "manifest.tsv"
    rows_count = len(manifest.read_text(encoding="utf-8").splitlines()) - 1 if manifest.is_file() else 0
    print(f"audio-files={actual}/{expected}")
    print(f"manifest-rows={rows_count}/{expected}")
    return 0 if actual == expected and rows_count == expected else 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("apply", "verify"))
    parser.add_argument("--ffmpeg", default="ffmpeg")
    arguments = parser.parse_args()
    try:
        raise SystemExit(apply(arguments.ffmpeg) if arguments.command == "apply" else verify())
    except RuntimeError as error:
        print(f"prepare_iowa_piano_temporal_controls: {error}")
        raise SystemExit(1)
