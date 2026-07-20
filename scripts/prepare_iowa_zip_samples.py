#!/usr/bin/env python3

import argparse
import hashlib
import html
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import wave
import zipfile


FIXTURE_VERSION = "iowa-zip-v2"
SPEC_SEPARATOR = "|"
NOTE_RE = re.compile(r"\.([A-G](?:b)?[0-8])(?:\.stereo)?\.aiff?$", re.IGNORECASE)
ZIP_LINK_RE = re.compile(r"""href\s*=\s*["']([^"']+\.zip)["']""", re.IGNORECASE)
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
    path = shutil.which(name) if os.path.sep not in name else name
    if not path:
        raise SystemExit(f"prepare_iowa_zip_samples: missing required tool `{name}`")
    return path


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
                f"prepare_iowa_zip_samples: retrying {path.name} after partial download "
                f"({size} bytes, attempt {attempt + 1}/{retries + 1})",
                file=sys.stderr,
            )
    else:
        if last_exc:
            raise last_exc
    partial_path.replace(path)


def parse_spec(text):
    fields = text.split(SPEC_SEPARATOR)
    if len(fields) != 4:
        raise SystemExit(
            "prepare_iowa_zip_samples: spec must be family|nsynth_family|source|zip_url"
        )
    family, nsynth_family, source, url = fields
    if family not in {"bass", "guitar", "piano", "vocals", "other"}:
        raise SystemExit(f"prepare_iowa_zip_samples: unsupported family `{family}`")
    if not nsynth_family or not source or not url:
        raise SystemExit("prepare_iowa_zip_samples: empty spec field")
    return {
        "family": family,
        "nsynth_family": nsynth_family,
        "source": source,
        "url": escape_url(url),
    }


def parse_page_spec(text):
    fields = text.split(SPEC_SEPARATOR)
    if len(fields) != 4:
        raise SystemExit(
            "prepare_iowa_zip_samples: page spec must be family|nsynth_family|source_prefix|page_url"
        )
    family, nsynth_family, source_prefix, url = fields
    if family not in {"bass", "guitar", "piano", "vocals", "other"}:
        raise SystemExit(f"prepare_iowa_zip_samples: unsupported family `{family}`")
    if not nsynth_family or not source_prefix or not url:
        raise SystemExit("prepare_iowa_zip_samples: empty page spec field")
    return {
        "family": family,
        "nsynth_family": nsynth_family,
        "source_prefix": source_prefix,
        "url": escape_url(url),
    }


def source_suffix_from_url(url):
    parsed = urllib.parse.urlparse(url)
    stem = Path(urllib.parse.unquote(parsed.path)).stem
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", stem).strip("-") or "zip"


def cached_page_path(cache_dir, page_spec):
    digest = hashlib.sha256(page_spec["url"].encode("utf-8")).hexdigest()[:12]
    source = re.sub(r"[^A-Za-z0-9_.-]+", "-", page_spec["source_prefix"]).strip("-")
    return cache_dir / f"{source}-{digest}.html"


def read_page_body(page_spec, timeout_seconds, cache_dir, refresh):
    cache_path = cached_page_path(cache_dir, page_spec)
    if cache_path.is_file() and not refresh:
        return cache_path.read_text(encoding="latin1", errors="replace")
    with urllib.request.urlopen(page_spec["url"], timeout=timeout_seconds) as response:
        body = response.read().decode("latin1", "replace")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(body, encoding="latin1")
    return body


def specs_from_page_spec(page_spec, timeout_seconds, max_zips, cache_dir, refresh):
    body = read_page_body(page_spec, timeout_seconds, cache_dir, refresh)
    specs = []
    seen = set()
    for raw_href in ZIP_LINK_RE.findall(body):
        zip_url = escape_url(urllib.parse.urljoin(page_spec["url"], html.unescape(raw_href)))
        if zip_url in seen:
            continue
        seen.add(zip_url)
        specs.append({
            "family": page_spec["family"],
            "nsynth_family": page_spec["nsynth_family"],
            "source": f"{page_spec['source_prefix']}-{source_suffix_from_url(zip_url)}",
            "url": zip_url,
        })
        if max_zips > 0 and len(specs) >= max_zips:
            break
    if not specs:
        raise SystemExit(f"prepare_iowa_zip_samples: no ZIP links found on {page_spec['url']}")
    return specs


def note_to_midi(note):
    match = re.fullmatch(r"([A-G](?:b)?)([0-8])", note)
    if not match:
        raise ValueError(f"unsupported note label {note}")
    name, octave_text = match.groups()
    return (int(octave_text) + 1) * 12 + NOTE_PITCH_CLASS[name]


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def zip_filename(spec):
    parsed = urllib.parse.urlparse(spec["url"])
    name = Path(urllib.parse.unquote(parsed.path)).name
    if not name:
        digest = hashlib.sha256(spec["url"].encode("utf-8")).hexdigest()[:12]
        name = f"{spec['source']}-{digest}.zip"
    return name


def collect_zip_rows(spec, zip_path):
    rows = []
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.namelist():
            if member.startswith("__MACOSX/") or member.endswith("/"):
                continue
            basename = Path(member).name
            match = NOTE_RE.search(basename)
            if not match:
                continue
            source_note = match.group(1)
            midi = note_to_midi(source_note)
            if midi < 21 or midi > 108:
                continue
            rows.append({
                "spec": spec,
                "zip_path": zip_path,
                "member": member,
                "midi": midi,
                "note": note_name(midi),
            })
    rows.sort(key=lambda row: (row["midi"], row["member"]))
    return rows


def sanitize_id(row):
    source = re.sub(r"[^A-Za-z0-9_.-]+", "_", row["spec"]["source"])
    stem = Path(row["member"]).stem
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)
    return f"iowa_{source}_{stem}"


def convert_member(row, output_dir, ffmpeg):
    rel_path = Path("audio") / f"{sanitize_id(row)}.wav"
    output_path = output_dir / rel_path
    if output_path.is_file():
        return str(rel_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = Path(row["member"]).suffix or ".aif"
    with zipfile.ZipFile(row["zip_path"]) as archive:
        with archive.open(row["member"]) as source:
            data = source.read()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        run([
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            tmp_path,
            "-ac",
            "1",
            "-ar",
            "48000",
            "-f",
            "wav",
            str(temporary_path),
        ])
        temporary_path.replace(output_path)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        if temporary_path.exists():
            temporary_path.unlink()
    return str(rel_path)


def midi_frequency(midi):
    return 440.0 * math.pow(2.0, (midi - 69) / 12.0)


def goertzel_level(samples, sample_rate, freq):
    if not samples:
        return 0.0
    coeff = 2.0 * math.cos(2.0 * math.pi * freq / sample_rate)
    s1 = 0.0
    s2 = 0.0
    count = len(samples)
    mean = sum(samples) / count
    for index, sample in enumerate(samples):
        window = 0.5 - 0.5 * math.cos(2.0 * math.pi * index / max(1, count - 1))
        x = (sample - mean) * window
        s0 = x + coeff * s1 - s2
        s2 = s1
        s1 = s0
    return math.sqrt(max(0.0, s1 * s1 + s2 * s2 - coeff * s1 * s2))


def read_probe_window(path):
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        sample_width = wav.getsampwidth()
        frame_count = wav.getnframes()
        if sample_width != 2:
            return sample_rate, []
        start = min(frame_count, int(sample_rate * 0.18))
        count = min(frame_count - start, int(sample_rate * 0.25))
        if count <= 0:
            return sample_rate, []
        wav.setpos(start)
        data = wav.readframes(count)

    samples = []
    step = sample_width * channels
    for offset in range(0, len(data), step):
        total = 0.0
        for channel in range(channels):
            start = offset + channel * sample_width
            value = int.from_bytes(data[start:start + sample_width], byteorder="little", signed=True)
            total += value / 32768.0
        samples.append(total / channels)
    return sample_rate, samples


def pitch_reference_ok(path, midi):
    sample_rate, samples = read_probe_window(path)
    if not samples:
        return False
    expected = goertzel_level(samples, sample_rate, midi_frequency(midi))
    lower = goertzel_level(samples, sample_rate, midi_frequency(midi - 1)) if midi > 21 else 0.0
    upper = goertzel_level(samples, sample_rate, midi_frequency(midi + 1)) if midi < 108 else 0.0
    adjacent = max(lower, upper)
    if adjacent <= 1.0e-6:
        return True
    return expected >= adjacent * 0.90


def signature_text(specs, limit):
    payload = FIXTURE_VERSION + "|limit=" + str(limit) + "|" + "|".join(
        f"{spec['family']}:{spec['nsynth_family']}:{spec['source']}:{spec['url']}" for spec in specs
    )
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
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                return False
            if fields[7] != expected_signature:
                return False
            if not (root / fields[6]).is_file():
                return False
            rows += 1
    return rows >= max(1, min_rows)


def write_manifest(path, rows, signature):
    with path.open("w", encoding="utf-8") as file:
        file.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tsignature\n")
        for row in rows:
            spec = row["spec"]
            file.write(
                "\t".join([
                    row["id"],
                    spec["family"],
                    spec["nsynth_family"],
                    spec["source"],
                    str(row["midi"]),
                    row["note"],
                    row["path"],
                    signature,
                ]) + "\n"
            )


def limited_rows(rows, limit):
    if limit <= 0 or len(rows) <= limit:
        return rows
    buckets = {}
    for row in rows:
        buckets.setdefault(row["spec"]["source"], []).append(row)
    result = []
    sources = sorted(buckets)
    while len(result) < limit:
        progressed = False
        for source in sources:
            bucket = buckets[source]
            if not bucket:
                continue
            result.append(bucket.pop(0))
            progressed = True
            if len(result) >= limit:
                break
        if not progressed:
            break
    return sorted(result, key=lambda row: (row["spec"]["source"], row["midi"], row["member"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare one-note samples from Iowa post-2012 ZIP files.")
    parser.add_argument("--spec", action="append", default=[])
    parser.add_argument("--page-spec", action="append", default=[])
    parser.add_argument("--source-dir", default=os.environ.get("IOWA_ZIP_SOURCE_DIR",
                                                               "build/real_sample_sources/iowa_zip"))
    parser.add_argument("--output", default=os.environ.get("IOWA_ZIP_SAMPLE_DIR",
                                                           "build/iowa_zip_samples"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("IOWA_ZIP_SAMPLE_LIMIT", "0")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("IOWA_ZIP_MIN_SAMPLES", "0")))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    parser.add_argument("--curl", default=os.environ.get("CURL", "curl"))
    parser.add_argument("--download-timeout", type=int,
                        default=int(os.environ.get("IOWA_ZIP_DOWNLOAD_TIMEOUT", "240")))
    parser.add_argument("--download-retries", type=int,
                        default=int(os.environ.get("IOWA_ZIP_DOWNLOAD_RETRIES", "4")))
    parser.add_argument("--max-download-failures", type=int,
                        default=int(os.environ.get("IOWA_ZIP_MAX_DOWNLOAD_FAILURES", "0")))
    parser.add_argument("--max-zips-per-page", type=int,
                        default=int(os.environ.get("IOWA_ZIP_MAX_ZIPS_PER_PAGE", "0")))
    parser.add_argument("--skip-pitch-check", action="store_true",
                        default=os.environ.get("IOWA_ZIP_SKIP_PITCH_CHECK") == "1")
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("IOWA_ZIP_REFRESH") == "1")
    args = parser.parse_args(argv)

    if not args.spec and not args.page_spec:
        raise SystemExit("prepare_iowa_zip_samples: at least one --spec or --page-spec is required")

    ffmpeg = find_command(args.ffmpeg)
    curl = find_command(args.curl)
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output)
    manifest_path = output_dir / "manifest.tsv"
    specs = [parse_spec(spec) for spec in args.spec]
    for page_spec_text in args.page_spec:
        specs.extend(specs_from_page_spec(parse_page_spec(page_spec_text), args.download_timeout,
                                          max(0, args.max_zips_per_page), source_dir / "_pages",
                                          args.refresh))
    signature = signature_text(specs, f"{args.limit}|pitch={0 if args.skip_pitch_check else 1}")
    min_samples = max(0, args.min_samples)
    if not args.refresh and manifest_complete(manifest_path, signature, min_samples):
        print(f"prepare_iowa_zip_samples: keeping existing {manifest_path}")
        return

    rows = []
    download_failures = []
    for spec in specs:
        zip_path = source_dir / zip_filename(spec)
        try:
            download_file(curl, spec["url"], zip_path, args.download_timeout, max(0, args.download_retries))
            rows.extend(collect_zip_rows(spec, zip_path))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, zipfile.BadZipFile, OSError) as exc:
            download_failures.append((spec["source"], str(exc)))
            if len(download_failures) > max(0, args.max_download_failures):
                raise
            print(
                f"prepare_iowa_zip_samples: skipped source {spec['source']} after download/read failure: {exc}",
                file=sys.stderr,
            )
    rows = limited_rows(rows, args.limit)
    if not rows:
        raise SystemExit("prepare_iowa_zip_samples: no one-note AIF members discovered")

    output_dir.mkdir(parents=True, exist_ok=True)
    prepared = []
    skipped = []
    skipped_pitch_reference = 0
    for index, row in enumerate(rows, start=1):
        try:
            print(
                f"prepare_iowa_zip_samples: [{index}/{len(rows)}] {Path(row['member']).name}",
                file=sys.stderr,
                flush=True,
            )
            prepared_row = dict(row)
            prepared_row["id"] = sanitize_id(row)
            prepared_row["path"] = convert_member(row, output_dir, ffmpeg)
            if not args.skip_pitch_check and not pitch_reference_ok(output_dir / prepared_row["path"],
                                                                    prepared_row["midi"]):
                skipped_pitch_reference += 1
                continue
            prepared.append(prepared_row)
        except (zipfile.BadZipFile, KeyError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
                OSError) as exc:
            skipped.append((row["member"], str(exc)))

    required_prepared = max(1, min_samples)
    if len(prepared) < required_prepared:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, prepared, signature)
        print(f"prepare_iowa_zip_samples: wrote {len(prepared)} rows to {partial_path}", file=sys.stderr)
        raise SystemExit(
            f"prepare_iowa_zip_samples: expected at least {required_prepared} prepared samples, "
            f"got {len(prepared)}"
        )

    write_manifest(manifest_path, prepared, signature)
    print(f"prepare_iowa_zip_samples: wrote {len(prepared)} rows to {manifest_path}")
    if skipped_pitch_reference:
        print(
            f"prepare_iowa_zip_samples: skipped_pitch_reference {skipped_pitch_reference}",
            file=sys.stderr,
        )
    if skipped:
        print(f"prepare_iowa_zip_samples: skipped {len(skipped)} files", file=sys.stderr)
        for member, reason in skipped[:12]:
            print(f"prepare_iowa_zip_samples: skipped {member}: {reason}", file=sys.stderr)
    if download_failures:
        print(f"prepare_iowa_zip_samples: skipped_sources {len(download_failures)}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"prepare_iowa_zip_samples: command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(exc.returncode)
    except subprocess.TimeoutExpired as exc:
        print(f"prepare_iowa_zip_samples: command timed out: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(124)
