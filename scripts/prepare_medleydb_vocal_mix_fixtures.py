#!/usr/bin/env python3
"""Prepare compact, externally cached, F0-labelled MedleyDB vocal-mix fixtures."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

from inspect_medleydb_vocal_annotations import ARCHIVE, stable_runs


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = Path(os.environ.get(
    "MUSIC_ANALYZER_FIXTURE_CACHE", "/media/kyz/sshflashtor/InstrumentSamples/build-cache"
))
DESTINATION = CACHE_ROOT / "medleydb_vocal_mix_samples"
OUTPUT_LINK = REPO_ROOT / "build" / "medleydb_vocal_mix_samples"
MIX_MEMBER = "MedleyDB_sample/Audio/LizNelson_Rainfall/LizNelson_Rainfall_MIX.wav"
HEADER = ("id", "family", "nsynth_family", "source", "midi", "note", "path", "details")
MIN_DURATION = 0.65
CLIP_DURATION = 0.62


def note_name(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def entries() -> tuple[tuple[int, float, float], ...]:
    return tuple(run for run in stable_runs() if run[2] - run[1] >= MIN_DURATION)


def ensure_link() -> None:
    OUTPUT_LINK.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT_LINK.is_symlink() and OUTPUT_LINK.resolve() == DESTINATION:
        return
    if OUTPUT_LINK.exists() or OUTPUT_LINK.is_symlink():
        raise RuntimeError(f"refusing to replace nonmatching fixture link: {OUTPUT_LINK}")
    OUTPUT_LINK.symlink_to(DESTINATION)


def manifest_text() -> str:
    rows = ["\t".join(HEADER)]
    for index, (midi, start, end) in enumerate(entries()):
        stem = f"rainfall_mix_{index:02d}_{note_name(midi)}"
        rows.append("\t".join((
            f"medleydb_rainfall_mix_{index:02d}_{note_name(midi)}", "vocals", "vocals",
            "medleydb-liznelson-rainfall-mix", str(midi), note_name(midi), f"audio/{stem}.wav",
            f"f0_start={start:.3f},f0_end={end:.3f},window={CLIP_DURATION:.2f},source=MedleyDB",
        )))
    return "\n".join(rows) + "\n"


def extract_mix(destination: Path) -> Path:
    source = destination / "source" / "LizNelson_Rainfall_MIX.wav"
    if source.is_file():
        return source
    source.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        member = archive.extractfile(MIX_MEMBER)
        if member is None:
            raise RuntimeError(f"missing archive member: {MIX_MEMBER}")
        temporary = source.with_suffix(".tmp.wav")
        with temporary.open("wb") as output:
            shutil.copyfileobj(member, output)
        temporary.replace(source)
    return source


def apply(ffmpeg: str) -> int:
    if not ARCHIVE.is_file():
        raise RuntimeError(f"missing MedleyDB sample archive: {ARCHIVE}")
    if not shutil.which(ffmpeg):
        raise RuntimeError(f"ffmpeg is required but was not found: {ffmpeg}")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    ensure_link()
    source = extract_mix(DESTINATION)
    audio = DESTINATION / "audio"
    audio.mkdir(exist_ok=True)
    for index, (midi, start, _end) in enumerate(entries()):
        target = audio / f"rainfall_mix_{index:02d}_{note_name(midi)}.wav"
        if target.is_file():
            continue
        temporary = target.with_suffix(".tmp.wav")
        subprocess.run([
            ffmpeg, "-v", "error", "-y", "-ss", f"{start:.6f}", "-t", f"{CLIP_DURATION:.2f}",
            "-i", str(source), "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(temporary),
        ], check=True)
        temporary.replace(target)
    manifest = DESTINATION / "manifest.tsv"
    temporary_manifest = manifest.with_suffix(".tmp")
    temporary_manifest.write_text(manifest_text(), encoding="utf-8")
    temporary_manifest.replace(manifest)
    print(f"link={OUTPUT_LINK} -> {DESTINATION}")
    print(f"samples={len(entries())}")
    return 0


def verify() -> int:
    expected = len(entries())
    audio = DESTINATION / "audio"
    actual = len(list(audio.glob("*.wav"))) if audio.is_dir() else 0
    manifest = DESTINATION / "manifest.tsv"
    rows = len(manifest.read_text(encoding="utf-8").splitlines()) - 1 if manifest.is_file() else 0
    print(f"audio-files={actual}/{expected}")
    print(f"manifest-rows={rows}/{expected}")
    return 0 if actual == expected and rows == expected else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("plan", "apply", "verify"))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    args = parser.parse_args()
    if args.command == "plan":
        print(f"archive={ARCHIVE}")
        print(f"samples={len(entries())}")
        raise SystemExit(0)
    if args.command == "verify":
        raise SystemExit(verify())
    raise SystemExit(apply(args.ffmpeg))
