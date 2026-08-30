#!/usr/bin/env python3
"""Prepare external-only University of Iowa Steinway Piano midrange fixtures."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
import re
import subprocess
import tempfile
import time
import urllib.request
from urllib.parse import quote, urljoin
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LINK = REPO_ROOT / "build" / "iowa_piano_midrange_samples"
CACHE_ROOT = Path(os.environ.get("MUSIC_ANALYZER_FIXTURE_CACHE",
                                 "/media/kyz/sshflashtor/InstrumentSamples/build-cache"))
OUTPUT_DIRECTORY = "iowa_piano_midrange_samples"
URL_ROOT = "https://theremin.music.uiowa.edu/sound%20files/MIS/Piano_Other/piano"
HEADER = ("id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities")
PITCH_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
IOWA_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")
DYNAMICS = ("pp", "mf", "ff")


def note_name(midi: int) -> str:
    return f"{PITCH_NAMES[midi % 12]}{midi // 12 - 1}"


def iowa_name(midi: int) -> str:
    return f"{IOWA_NAMES[midi % 12]}{midi // 12 - 1}"


def items():
    for dynamic in DYNAMICS:
        for midi in range(48, 84):
            stem = f"Piano.{dynamic}.{iowa_name(midi)}"
            yield dynamic, midi, stem


def output_root() -> Path:
    return CACHE_ROOT / OUTPUT_DIRECTORY


def manifest_text(selection=None) -> str:
    rows = ["\t".join(HEADER)]
    for dynamic, midi, stem in (items() if selection is None else selection):
        rows.append("\t".join((
            f"iowa_piano_{dynamic}_{note_name(midi)}", "piano", "piano", "iowa-steinway",
            str(midi), note_name(midi), f"wav/{stem}.wav",
            f"dynamic={dynamic},annotated_note={note_name(midi)},University-of-Iowa-Steinway",
        )))
    return "\n".join(rows) + "\n"


def write_manifest(destination: Path, selection) -> None:
    manifest = destination / "manifest.tsv"
    temporary_manifest = manifest.with_suffix(".tmp")
    temporary_manifest.write_text(manifest_text(selection), encoding="utf-8")
    temporary_manifest.replace(manifest)


def materialize_test_wavs(destination: Path, selection, ffmpeg: str) -> None:
    if not shutil_which(ffmpeg):
        raise RuntimeError(f"ffmpeg is required but was not found: {ffmpeg}")
    wav = destination / "wav"
    wav.mkdir(exist_ok=True)
    for _dynamic, _midi, stem in selection:
        source = destination / "audio" / f"{stem}.flac"
        target = wav / f"{stem}.wav"
        if target.is_file():
            continue
        temporary_target = target.with_suffix(".tmp.wav")
        subprocess.run([
            ffmpeg, "-v", "error", "-y", "-i", str(source), "-t", "3", "-ac", "1", "-ar", "44100",
            "-c:a", "pcm_s16le", str(temporary_target),
        ], check=True)
        temporary_target.replace(target)


def publish_partial(ffmpeg: str) -> int:
    destination = output_root()
    audio = destination / "audio"
    destination.mkdir(parents=True, exist_ok=True)
    audio.mkdir(exist_ok=True)
    ensure_link(destination)
    selection = tuple(item for item in items() if (audio / f"{item[2]}.flac").is_file())
    materialize_test_wavs(destination, selection, ffmpeg)
    write_manifest(destination, selection)
    print(f"manifest={destination / 'manifest.tsv'}")
    print(f"samples={len(selection)}/{sum(1 for _ in items())}")
    return 0


def ensure_link(destination: Path) -> None:
    if OUTPUT_LINK.is_symlink() and OUTPUT_LINK.resolve() == destination:
        return
    if OUTPUT_LINK.exists() or OUTPUT_LINK.is_symlink():
        raise RuntimeError(f"refusing to replace existing fixture path: {OUTPUT_LINK}")
    OUTPUT_LINK.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_LINK.symlink_to(destination)


def plan() -> int:
    destination = output_root()
    print(f"destination={destination}")
    print(f"link={OUTPUT_LINK} -> {destination}")
    print(f"samples={sum(1 for _ in items())}")
    print(f"url-example={URL_ROOT}/Piano.mf.C4.aiff")
    return 0


def probe() -> int:
    page = "https://theremin.music.uiowa.edu/MISPiano.html"
    with urllib.request.urlopen(page) as response:
        html = response.read().decode("utf-8", errors="replace")
    match = re.search(r'href=["\']([^"\']*Piano\.mf\.C4\.aiff[^"\']*)', html, re.IGNORECASE)
    if not match:
        raise RuntimeError("could not locate Piano.mf.C4.aiff href on the Iowa piano page")
    url = quote(urljoin(page, match.group(1)), safe=":/%")
    request = urllib.request.Request(url, headers={"User-Agent": "music-analyzer-fixture-fetch/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read(1)
        print(f"sample-url={response.url}")
        print(f"content-length={response.headers.get('Content-Length', 'unknown')}")
    return 0


def apply(ffmpeg: str) -> int:
    if not shutil_which(ffmpeg):
        raise RuntimeError(f"ffmpeg is required but was not found: {ffmpeg}")
    destination = output_root()
    audio = destination / "audio"
    destination.mkdir(parents=True, exist_ok=True)
    audio.mkdir(exist_ok=True)
    ensure_link(destination)
    with tempfile.TemporaryDirectory(prefix="iowa-piano-", dir=destination) as temporary:
        temporary_path = Path(temporary)

        def download(item: tuple[str, int, str]) -> None:
            dynamic, _midi, stem = item
            target = audio / f"{stem}.flac"
            if target.is_file() and target.stat().st_size > 0:
                return
            source = temporary_path / f"{stem}.aiff"
            url = f"{URL_ROOT}/{stem}.aiff"
            request = urllib.request.Request(url, headers={"User-Agent": "music-analyzer-fixture-fetch/1"})
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(request, timeout=180) as response, source.open("wb") as output:
                        while chunk := response.read(1024 * 1024):
                            output.write(chunk)
                    break
                except TimeoutError:
                    source.unlink(missing_ok=True)
                    if attempt == 2:
                        raise
                    print(f"retry={attempt + 1} target={target.name}", flush=True)
                    time.sleep(2**attempt)
            temporary_target = target.with_suffix(".tmp.flac")
            subprocess.run([ffmpeg, "-v", "error", "-y", "-i", str(source), str(temporary_target)],
                           check=True)
            temporary_target.replace(target)
            print(f"downloaded={target.name}", flush=True)
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(download, items()))
    selection = tuple(items())
    materialize_test_wavs(destination, selection, ffmpeg)
    write_manifest(destination, selection)
    manifest = destination / "manifest.tsv"
    print(f"manifest={manifest}")
    print(f"link={OUTPUT_LINK} -> {destination}")
    print(f"samples={sum(1 for _ in items())}")
    return 0


def verify() -> int:
    destination = output_root()
    manifest = destination / "manifest.tsv"
    expected = sum(1 for _ in items())
    actual = len(list((destination / "audio").glob("*.flac"))) if destination.is_dir() else 0
    wav_actual = len(list((destination / "wav").glob("*.wav"))) if destination.is_dir() else 0
    manifest_rows = len(manifest.read_text(encoding="utf-8").splitlines()) - 1 if manifest.is_file() else 0
    print(f"manifest={manifest}")
    print(f"audio-files={actual}/{expected}")
    print(f"wav-files={wav_actual}/{expected}")
    print(f"manifest-rows={manifest_rows}/{expected}")
    if not manifest.is_file() or actual != expected or wav_actual != expected or manifest_rows != expected:
        return 1
    return 0


def shutil_which(command: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / command
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("plan", "probe", "apply", "publish-partial", "verify"))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    args = parser.parse_args()
    if args.command == "plan":
        raise SystemExit(plan())
    if args.command == "probe":
        raise SystemExit(probe())
    if args.command == "verify":
        raise SystemExit(verify())
    if args.command == "publish-partial":
        raise SystemExit(publish_partial(args.ffmpeg))
    raise SystemExit(apply(args.ffmpeg))
