#!/usr/bin/env python3

import argparse
import hashlib
import html
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


FIXTURE_VERSION = "iowa-piano-v1"
NOTE_RE = re.compile(r"Piano\.(pp|mf|ff)\.([A-G](?:b)?[0-8])\.aiff$", re.IGNORECASE)
DYNAMIC_ORDER = {"mf": 0, "ff": 1, "pp": 2}
FLAT_NOTE_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")
NOTE_PITCH_CLASS = {
    "C": 0,
    "Db": 1,
    "D": 2,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "Gb": 6,
    "G": 7,
    "Ab": 8,
    "A": 9,
    "Bb": 10,
    "B": 11,
}


def run(command, timeout_seconds=None):
    subprocess.run(command, check=True, timeout=timeout_seconds)


def find_command(name):
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"prepare_iowa_piano_samples: missing required tool `{name}`")
    return path


def fetch_bytes(url):
    request = urllib.request.Request(url, headers={"User-Agent": "music-analyzer-test-fixture/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def escape_url(url):
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            urllib.parse.quote(parts.path, safe="/%:"),
            urllib.parse.quote(parts.query, safe="=&%:"),
            urllib.parse.quote(parts.fragment, safe="%:"),
        )
    )


def download_file(curl, url, path, timeout_seconds, retries):
    if path.is_file() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = path.with_suffix(path.suffix + ".part")
    last_exc = None
    for attempt in range(max(1, retries + 1)):
        try:
            run([
                curl,
                "-L",
                "--fail",
                "--show-error",
                "--silent",
                "--connect-timeout",
                "20",
                "--max-time",
                str(timeout_seconds),
                "-C",
                "-",
                "-o",
                str(partial_path),
                url,
            ], timeout_seconds=timeout_seconds + 30)
            break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            last_exc = exc
            if attempt >= retries:
                raise
            size = partial_path.stat().st_size if partial_path.exists() else 0
            print(
                f"prepare_iowa_piano_samples: retrying {path.name} after partial download "
                f"({size} bytes, attempt {attempt + 1}/{retries + 1})",
                file=sys.stderr,
            )
    else:
        if last_exc:
            raise last_exc
    partial_path.replace(path)


def note_to_midi(note):
    match = re.fullmatch(r"([A-G](?:b)?)([0-8])", note)
    if not match:
        raise ValueError(f"unsupported note label {note}")
    name, octave_text = match.groups()
    return (int(octave_text) + 1) * 12 + NOTE_PITCH_CLASS[name]


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def row_for_file(filename, dynamic, source_note, midi, url):
    return {
        "filename": filename,
        "dynamic": dynamic,
        "source_note": source_note,
        "midi": midi,
        "url": escape_url(url),
    }


def discover_samples_from_page(page_url, page):
    seen = set()
    rows = []
    for href in re.findall(r'href=["\']([^"\']+\.aiff)["\']', page, flags=re.IGNORECASE):
        href = html.unescape(href)
        filename = Path(urllib.parse.urlparse(href).path).name
        match = NOTE_RE.match(filename)
        if not match or filename in seen:
            continue
        seen.add(filename)
        dynamic = match.group(1).lower()
        source_note = match.group(2)
        midi = note_to_midi(source_note)
        if midi < 21 or midi > 108:
            continue
        rows.append(row_for_file(filename, dynamic, source_note, midi, urllib.parse.urljoin(page_url, href)))
    rows.sort(key=lambda row: (DYNAMIC_ORDER.get(row["dynamic"], 9), row["midi"], row["filename"]))
    return rows


def fallback_samples(file_base_url):
    rows = []
    for dynamic in ("mf", "ff", "pp"):
        for midi in range(21, 109):
            note = FLAT_NOTE_NAMES[midi % 12]
            octave = midi // 12 - 1
            source_note = f"{note}{octave}"
            filename = f"Piano.{dynamic}.{source_note}.aiff"
            rows.append(row_for_file(filename, dynamic, source_note, midi,
                                     urllib.parse.urljoin(file_base_url, filename)))
    rows.sort(key=lambda row: (DYNAMIC_ORDER.get(row["dynamic"], 9), row["midi"], row["filename"]))
    return rows


def discover_samples(curl, page_url, file_base_url, source_dir, timeout_seconds, retries, refresh):
    page_path = source_dir / "MISpiano.html"
    try:
        if refresh and page_path.exists():
            page_path.unlink()
        download_file(curl, escape_url(page_url), page_path, timeout_seconds, retries)
        rows = discover_samples_from_page(page_url, page_path.read_text(encoding="utf-8", errors="replace"))
        if rows:
            return rows
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"prepare_iowa_piano_samples: page discovery failed, using URL-pattern fallback: {exc}",
              file=sys.stderr)
    return fallback_samples(file_base_url)


def limited_rows(rows, limit):
    if limit <= 0 or len(rows) <= limit:
        return rows
    return rows[:limit]


def signature_text(page_url, file_base_url, limit):
    payload = f"{FIXTURE_VERSION}|{page_url}|base={file_base_url}|limit={limit}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def manifest_complete(path, expected_signature, min_rows):
    if not path.is_file():
        return False
    root = path.parent
    rows = 0
    with path.open("r", encoding="utf-8") as file:
        header = file.readline()
        if "\tpath\t" not in header:
            return False
        for line in file:
            rows += 1
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                return False
            if fields[7] != expected_signature:
                return False
            if not (root / fields[6]).is_file():
                return False
    return rows >= max(1, min_rows)


def convert_aiff(ffmpeg, source_path, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    run([
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source_path),
        "-ac",
        "1",
        "-ar",
        "48000",
        "-f",
        "wav",
        str(temporary_path),
    ])
    temporary_path.replace(output_path)


def write_manifest(path, prepared, signature):
    with path.open("w", encoding="utf-8") as file:
        file.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tsignature\n")
        for row, wav_name in prepared:
            sample_id = Path(row["filename"]).stem
            file.write(
                "\t".join([
                    sample_id,
                    "piano",
                    "keyboard",
                    f"iowa-piano-{row['dynamic']}",
                    str(row["midi"]),
                    note_name(row["midi"]),
                    wav_name,
                    signature,
                ]) + "\n"
            )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare University of Iowa piano note WAV fixtures.")
    parser.add_argument("--page-url", default=os.environ.get("IOWA_PIANO_PAGE_URL",
                                                             "https://theremin.music.uiowa.edu/MISpiano.html"))
    parser.add_argument("--file-base-url", default=os.environ.get(
        "IOWA_PIANO_FILE_BASE_URL",
        "https://theremin.music.uiowa.edu/sound files/MIS/Piano_Other/piano/"))
    parser.add_argument("--source-dir", default=os.environ.get("IOWA_PIANO_SOURCE_DIR",
                                                               "build/real_sample_sources/iowa_piano"))
    parser.add_argument("--output", default=os.environ.get("IOWA_PIANO_SAMPLE_DIR",
                                                           "build/iowa_piano_samples"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("IOWA_PIANO_SAMPLE_LIMIT", "84")))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    parser.add_argument("--curl", default=os.environ.get("CURL", "curl"))
    parser.add_argument("--download-timeout", type=int,
                        default=int(os.environ.get("IOWA_PIANO_DOWNLOAD_TIMEOUT", "240")))
    parser.add_argument("--download-retries", type=int,
                        default=int(os.environ.get("IOWA_PIANO_DOWNLOAD_RETRIES", "4")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("IOWA_PIANO_MIN_SAMPLES", "0")))
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("IOWA_PIANO_REFRESH") == "1")
    args = parser.parse_args(argv)

    ffmpeg = find_command(args.ffmpeg)
    curl = find_command(args.curl)
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output)
    manifest_path = output_dir / "manifest.tsv"
    signature = signature_text(args.page_url, args.file_base_url, args.limit)
    min_samples = max(0, args.min_samples)
    if not args.refresh and manifest_complete(manifest_path, signature, min_samples):
        print(f"prepare_iowa_piano_samples: keeping existing {manifest_path}")
        return

    rows = limited_rows(
        discover_samples(curl, args.page_url, args.file_base_url, source_dir, args.download_timeout,
                         max(0, args.download_retries), args.refresh),
        args.limit,
    )
    if not rows:
        raise SystemExit("prepare_iowa_piano_samples: no piano AIFF links discovered")

    output_dir.mkdir(parents=True, exist_ok=True)
    prepared = []
    skipped = []
    total = len(rows)
    for index, row in enumerate(rows, start=1):
        raw_path = source_dir / row["filename"]
        wav_name = Path(row["filename"]).with_suffix(".wav").name
        wav_path = output_dir / wav_name
        try:
            print(
                f"prepare_iowa_piano_samples: [{index}/{total}] {row['filename']} -> {wav_name}",
                file=sys.stderr,
                flush=True,
            )
            download_file(curl, row["url"], raw_path, args.download_timeout, max(0, args.download_retries))
            convert_aiff(ffmpeg, raw_path, wav_path)
        except (urllib.error.URLError, subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            skipped.append((row["filename"], str(exc)))
            continue
        prepared.append((row, wav_name))

    required_prepared = max(1, min_samples)
    if len(prepared) < required_prepared:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, prepared, signature)
        print(f"prepare_iowa_piano_samples: wrote {len(prepared)} rows to {partial_path}", file=sys.stderr)
        raise SystemExit(
            f"prepare_iowa_piano_samples: expected at least {required_prepared} prepared piano samples, "
            f"got {len(prepared)}"
        )

    write_manifest(manifest_path, prepared, signature)
    print(f"prepare_iowa_piano_samples: wrote {len(prepared)} rows to {manifest_path}")
    if skipped:
        print(f"prepare_iowa_piano_samples: skipped {len(skipped)} files", file=sys.stderr)
        for filename, reason in skipped[:12]:
            print(f"prepare_iowa_piano_samples: skipped {filename}: {reason}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"prepare_iowa_piano_samples: command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(exc.returncode)
    except subprocess.TimeoutExpired as exc:
        print(f"prepare_iowa_piano_samples: command timed out: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(124)
