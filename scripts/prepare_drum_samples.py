#!/usr/bin/env python3

import argparse
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import wave
import zipfile


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")

EXCLUDE_RE = re.compile(r"(break|loop|groove|pattern|beat|fill|construction|song)", re.I)


def sanitize_name(text):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._-")
    return cleaned[:80] or "sample"


def category_for_path(path):
    text = str(path).replace("\\", "/").lower()
    name = Path(path).name.lower()
    stem = Path(path).stem.lower()

    if EXCLUDE_RE.search(text):
        return None
    if re.search(r"rim\s*shot|rimshot|(^|[/ _-])rim([0-9 _.-]|$)|side\s*stick|sidestick", text):
        return "rim"
    if re.search(r"kick|bass\s*drum|bassdrum|bassdm|(^|[/ _-])bd([0-9 _.-]|$)", text):
        return "kick"
    if "roland tr-909 drum samples" in text and stem.startswith("bt"):
        return "kick"
    if re.search(r"snare|snaredm|(^|[/ _-])sd([0-9 _.-]|$)", text):
        return "snare"
    if "roland tr-909 drum samples" in text and stem.startswith("st"):
        return "snare"
    if re.search(r"hihat|hi\s*hat|hat\s*(closed|open|middle|reverse)|closed\s*hh|open\s*hh|closedhh|openhh|(^|[/ _-])hh[co]?", text):
        return "hihat"
    if "roland tr-909 drum samples" in text and (stem.startswith("hhc") or stem.startswith("hho")):
        return "hihat"
    if re.search(r"ride|ridecym", text):
        return "ride"
    if re.search(r"crash|crsh|cymbal|cymball|(^|[/ _-])csh", text):
        return "crash"
    if re.search(r"tom|floor\s*tom|lowtom|midtom|hitom", text):
        return "tom"
    if "roland tr-909 drum samples" in text and stem[:2] in ("lt", "mt", "ht"):
        return "tom"
    return None


def wav_duration_from_file(path):
    try:
        with wave.open(str(path), "rb") as wav:
            rate = wav.getframerate()
            frames = wav.getnframes()
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            if rate <= 0 or frames <= 0 or channels <= 0 or sample_width <= 0:
                return None
            return frames / float(rate)
    except (wave.Error, OSError, EOFError):
        return None


def wav_duration_from_bytes(data):
    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            rate = wav.getframerate()
            frames = wav.getnframes()
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            if rate <= 0 or frames <= 0 or channels <= 0 or sample_width <= 0:
                return None
            return frames / float(rate)
    except (wave.Error, OSError, EOFError):
        return None


def one_shot_duration(duration):
    return duration is not None and 0.015 <= duration <= 3.0


def archive_member_label(source, archive, member_name):
    try:
        archive_name = archive.relative_to(source)
    except ValueError:
        archive_name = archive.name
    return Path(archive_name) / member_name


def collect_plain_wavs(source):
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix.lower() != ".wav":
            continue
        category = category_for_path(path)
        if not category:
            continue
        duration = wav_duration_from_file(path)
        if not one_shot_duration(duration):
            continue
        yield category, path, path.name, duration


def collect_zip_wavs(source):
    for archive in sorted(source.rglob("*.zip")):
        try:
            with zipfile.ZipFile(archive) as zf:
                for info in sorted(zf.infolist(), key=lambda item: item.filename):
                    if info.is_dir() or not info.filename.lower().endswith(".wav"):
                        continue
                    category = category_for_path(archive_member_label(source, archive, info.filename))
                    if not category:
                        continue
                    data = zf.read(info)
                    duration = wav_duration_from_bytes(data)
                    if not one_shot_duration(duration):
                        continue
                    yield category, archive, info.filename, duration, data
        except (zipfile.BadZipFile, OSError):
            continue


def collect_rar_wavs(source, unrar):
    if not unrar:
        return
    for archive in sorted(source.rglob("*.rar")):
        try:
            listing = subprocess.run(
                [unrar, "lb", str(archive)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError):
            continue
        member_names = listing.stdout.decode("utf-8", errors="replace").splitlines()
        for member_name in member_names:
            if not member_name.lower().endswith(".wav"):
                continue
            category = category_for_path(archive_member_label(source, archive, member_name))
            if not category:
                continue
            try:
                extracted = subprocess.run(
                    [unrar, "p", "-inul", str(archive), member_name],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
            except (OSError, subprocess.CalledProcessError):
                continue
            data = extracted.stdout
            duration = wav_duration_from_bytes(data)
            if not one_shot_duration(duration):
                continue
            yield category, archive, member_name, duration, data


def ensure_dirs(output):
    output.mkdir(parents=True, exist_ok=True)
    for category in CATEGORIES:
        (output / category).mkdir(parents=True, exist_ok=True)


def clean_output(output):
    if output.exists():
        shutil.rmtree(output)
    ensure_dirs(output)


def reached_sample_limit(counts, limit_per_category):
    return limit_per_category > 0 and all(counts[category] >= limit_per_category for category in CATEGORIES)


def copy_samples(source, output, limit_per_category, unrar=None):
    counts = {category: 0 for category in CATEGORIES}
    manifest = []

    for category, path, original_name, duration in collect_plain_wavs(source):
        if reached_sample_limit(counts, limit_per_category):
            break
        if limit_per_category > 0 and counts[category] >= limit_per_category:
            continue
        counts[category] += 1
        dest_name = f"{counts[category]:03d}_{sanitize_name(original_name)}"
        dest = output / category / dest_name
        shutil.copy2(path, dest)
        manifest.append((category, str(dest.relative_to(output)), f"{duration:.6f}", str(path)))

    if not reached_sample_limit(counts, limit_per_category):
        for category, archive, member_name, duration, data in collect_zip_wavs(source):
            if reached_sample_limit(counts, limit_per_category):
                break
            if limit_per_category > 0 and counts[category] >= limit_per_category:
                continue
            counts[category] += 1
            dest_name = f"{counts[category]:03d}_{sanitize_name(Path(member_name).name)}"
            dest = output / category / dest_name
            dest.write_bytes(data)
            manifest.append((category, str(dest.relative_to(output)), f"{duration:.6f}", f"{archive}!{member_name}"))

    if not reached_sample_limit(counts, limit_per_category):
        for category, archive, member_name, duration, data in collect_rar_wavs(source, unrar):
            if reached_sample_limit(counts, limit_per_category):
                break
            if limit_per_category > 0 and counts[category] >= limit_per_category:
                continue
            counts[category] += 1
            dest_name = f"{counts[category]:03d}_{sanitize_name(Path(member_name).name)}"
            dest = output / category / dest_name
            dest.write_bytes(data)
            manifest.append((category, str(dest.relative_to(output)), f"{duration:.6f}", f"{archive}!{member_name}"))

    manifest.sort()
    manifest_path = output / "manifest.tsv"
    with manifest_path.open("w", encoding="utf-8") as file:
        file.write("category\tpath\tduration_seconds\tsource\n")
        for row in manifest:
            file.write("\t".join(row) + "\n")

    return counts, manifest_path


def main():
    parser = argparse.ArgumentParser(description="Copy one-shot drum samples into a build-local fixture directory.")
    parser.add_argument("--source", default=os.environ.get("DRUM_SAMPLE_SOURCE_DIR", "/media/kyz/sshflashtor/DrumSamples"))
    parser.add_argument("--output", default=os.environ.get("DRUM_SAMPLE_BUILD_DIR", "build/drum_samples"))
    parser.add_argument("--limit-per-category", type=int, default=int(os.environ.get("DRUM_SAMPLE_LIMIT", "32")))
    parser.add_argument("--unrar", default=os.environ.get("UNRAR", "unrar"))
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    if not source.is_dir():
        raise SystemExit(f"prepare_drum_samples: source directory not found: {source}")

    clean_output(output)
    unrar = shutil.which(args.unrar) if args.unrar else None
    counts, manifest_path = copy_samples(source, output, max(0, args.limit_per_category), unrar=unrar)
    summary = " ".join(f"{category}={counts[category]}" for category in CATEGORIES)
    print(f"prepare_drum_samples: wrote {manifest_path} ({summary})")

    missing = [category for category in CATEGORIES if counts[category] == 0]
    if missing:
        raise SystemExit("prepare_drum_samples: missing categories: " + ", ".join(missing))


if __name__ == "__main__":
    main()
