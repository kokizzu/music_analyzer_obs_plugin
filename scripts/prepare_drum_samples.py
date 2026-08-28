#!/usr/bin/env python3

import argparse
from collections import OrderedDict, defaultdict
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import wave
import zipfile


CATEGORIES = ("kick", "snare", "hihat", "crash", "tom", "ride", "rim")
CACHE_VERSION = 3
SKIP_REASONS = (
    "excluded_loop",
    "unsupported_percussion",
    "uncategorized",
    "bad_duration",
    "archive_error",
)

EXCLUDE_RE = re.compile(r"(break|loop|groove|pattern|beat|fill|construction|song)", re.I)
UNSUPPORTED_PERCUSSION_NAME_RE = re.compile(
    r"(clap|handclap|clave|claves|conga|bongo|cowbell|shaker|tambourine|tamb|maraca|agogo|woodblock|snap)",
    re.I,
)
TOM_TOKEN_RE = re.compile(
    r"(^|[/ _.-])(?:tom|toms|floor\s*tom|low\s*tom|mid\s*tom|hi\s*tom|hitom|lowtom|midtom|htom|mtom|ltom)([0-9 _./-]|$)",
    re.I,
)


class Candidate:
    def __init__(self, category, kind, path, original_name, duration, source_label, member_name=None, data=None):
        self.category = category
        self.kind = kind
        self.path = path
        self.original_name = original_name
        self.duration = duration
        self.source_label = source_label
        self.member_name = member_name
        self.data = data


class SkipAudit:
    def __init__(self):
        self.counts = defaultdict(int)
        self.kind_counts = defaultdict(int)
        self.kind_reason_counts = defaultdict(lambda: {reason: 0 for reason in SKIP_REASONS})
        self.examples = defaultdict(list)

    def record(self, kind, reason, label):
        if reason not in SKIP_REASONS:
            reason = "uncategorized"
        self.counts[reason] += 1
        self.kind_counts[kind] += 1
        self.kind_reason_counts[kind][reason] += 1
        if len(self.examples[reason]) < 3:
            self.examples[reason].append(label)

    @property
    def total(self):
        return sum(self.counts.values())


class ZipReadCache:
    def __init__(self, limit=16):
        self.limit = max(1, limit)
        self.handles = OrderedDict()

    def read(self, archive, member_name):
        handle = self.handles.pop(archive, None)
        if handle is None:
            handle = zipfile.ZipFile(archive)
        self.handles[archive] = handle
        while len(self.handles) > self.limit:
            _old_archive, old_handle = self.handles.popitem(last=False)
            old_handle.close()
        return handle.read(member_name)

    def close(self):
        for handle in self.handles.values():
            handle.close()
        self.handles.clear()


def sanitize_name(text):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._-")
    return cleaned[:80] or "sample"


def category_and_rejection_reason(path):
    text = str(path).replace("\\", "/").lower()
    name = Path(path).name.lower()
    stem = Path(path).stem.lower()
    compact_stem = re.sub(r"[^a-z0-9]+", "", stem)
    hihat_compact = (
        compact_stem.startswith(("chh", "ohh", "hh", "hat", "hihat")) or
        "clsd" in compact_stem or
        "closedhat" in compact_stem or
        "openhat" in compact_stem
    )
    compact_kick_alias = (
        re.search(r"(?:^|[0-9])bd[a-z0-9]*$", compact_stem) or
        re.search(
            r"^(?:cfm|cpc|csp|dmx|prom|prommer|rz1|r8|xd5|mr10|sp[0-9]+[fr]?|"
            r"analog|vinyl)[a-z0-9]*bd[a-z0-9]*$",
            compact_stem,
        )
    )
    compact_snare_alias = (
        re.search(r"(?:^|[0-9])sd[a-z0-9]*$", compact_stem) or
        re.search(
            r"^(?:cfm|cpc|csp|tr[0-9]{3,4}|sdr|dmx|prom|rz1|r8|xd5|mr10|"
            r"sp[0-9]+[fr]?|analog|vinyl)[a-z0-9]*sd[a-z0-9]*$",
            compact_stem,
        )
    )
    compact_tom_alias = bool(re.search(r"(?:hitom|lotom|midtom|tomhi|tomlo|tommid)", compact_stem))

    if EXCLUDE_RE.search(text):
        return None, "excluded_loop"
    if re.search(r"rim\s*shot|rimshot|rimhot|(^|[/ _-])rim([0-9 _.-]|$)|side[ _.-]*stick|sideststick", text):
        return "rim", ""
    if (re.search(r"kick|(^|[/ _.-])kic([0-9 _.-]|$)|bass\s*drum|bassdrum|bassdm|(^|[/ _-])bd([0-9 _.-]|$)", text) or
            compact_stem.startswith(("bd", "bdr")) or
            re.search(r"^tr[0-9]{3,4}bd[0-9]*$", compact_stem) or
            (compact_kick_alias and not hihat_compact)):
        return "kick", ""
    if "roland tr-909 drum samples" in text and stem.startswith("bt"):
        return "kick", ""
    if (re.search(r"snare|snaredm|(^|[/ _-])sd([0-9 _.-]|$)", text) or
            "snr" in compact_stem or
            re.search(r"^tr[0-9]{3,4}sd[0-9]*$", compact_stem) or
            (compact_snare_alias and not hihat_compact)):
        return "snare", ""
    if "roland tr-909 drum samples" in text and stem.startswith("st"):
        return "snare", ""
    if (re.search(
            r"hihat|hi\s*hat|hat\s*(closed|open|middle|pedal|reverse)|"
            r"(closed|open|middle|pedal|reverse|live)\s*hats?|"
            r"(closed|open)\s*cym(?:bal|bol|b)|closed\s*hh|open\s*hh|closedhh|openhh|"
            r"(^|[/ _.-])[co]hh[0-9a-z]*|(^|[/ _.-])hh[co]?",
            text,
        ) or
            re.search(r"^(?:[0-9]{2,3}|real|room)?(?:ch|oh)[0-9]?$", stem) or
            re.search(r"^hh[co]d?[0-9a-f]?$", stem) or
            compact_stem.endswith(("hat", "hats", "hatc", "hato")) or
            ("hat" in compact_stem and "clsd" in compact_stem)):
        return "hihat", ""
    if "roland tr-909 drum samples" in text and (stem.startswith("hhc") or stem.startswith("hho")):
        return "hihat", ""
    if re.search(r"ride|ridecym", text):
        return "ride", ""
    if (re.search(r"crash|crsh|cymbal|cymball|cymbol|(^|[/ _.-])cymb?l?([0-9 _.-]|$)|(^|[/ _-])csh", text) or
            compact_stem.startswith(("cym", "cymb", "cymbl"))):
        return "crash", ""
    if UNSUPPORTED_PERCUSSION_NAME_RE.search(name) and not re.search(r"snare|snr|rim|side\s*stick|sidestick", name):
        return None, "unsupported_percussion"
    if TOM_TOKEN_RE.search(text) or compact_tom_alias:
        return "tom", ""
    if "roland tr-909 drum samples" in text and stem[:2] in ("lt", "mt", "ht"):
        return "tom", ""
    return None, "uncategorized"


def category_for_path(path):
    category, _reason = category_and_rejection_reason(path)
    return category


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


def collect_plain_wavs(source, audit=None):
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix.lower() != ".wav":
            continue
        category, reason = category_and_rejection_reason(path)
        if not category:
            if audit is not None:
                audit.record("plain", reason, str(path))
            continue
        duration = wav_duration_from_file(path)
        if not one_shot_duration(duration):
            if audit is not None:
                audit.record("plain", "bad_duration", str(path))
            continue
        yield Candidate(category, "plain", path, path.name, duration, str(path))


def collect_zip_wavs(source, retain_data=False, audit=None):
    for archive in sorted(source.rglob("*.zip")):
        try:
            with zipfile.ZipFile(archive) as zf:
                for info in sorted(zf.infolist(), key=lambda item: item.filename):
                    if info.is_dir() or not info.filename.lower().endswith(".wav"):
                        continue
                    source_label = f"{archive}!{info.filename}"
                    category, reason = category_and_rejection_reason(
                        archive_member_label(source, archive, info.filename)
                    )
                    if not category:
                        if audit is not None:
                            audit.record("zip", reason, source_label)
                        continue
                    data = zf.read(info)
                    duration = wav_duration_from_bytes(data)
                    if not one_shot_duration(duration):
                        if audit is not None:
                            audit.record("zip", "bad_duration", source_label)
                        continue
                    yield Candidate(category, "zip", archive, Path(info.filename).name, duration,
                                    f"{archive}!{info.filename}", member_name=info.filename,
                                    data=data if retain_data else None)
        except (zipfile.BadZipFile, OSError):
            if audit is not None:
                audit.record("zip", "archive_error", str(archive))
            continue


def collect_rar_wavs(source, unrar, retain_data=False, audit=None):
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
            if audit is not None:
                audit.record("rar", "archive_error", str(archive))
            continue
        member_names = listing.stdout.decode("utf-8", errors="replace").splitlines()
        for member_name in member_names:
            if not member_name.lower().endswith(".wav"):
                continue
            source_label = f"{archive}!{member_name}"
            category, reason = category_and_rejection_reason(
                archive_member_label(source, archive, member_name)
            )
            if not category:
                if audit is not None:
                    audit.record("rar", reason, source_label)
                continue
            try:
                extracted = subprocess.run(
                    [unrar, "p", "-inul", str(archive), member_name],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
            except (OSError, subprocess.CalledProcessError):
                if audit is not None:
                    audit.record("rar", "archive_error", source_label)
                continue
            data = extracted.stdout
            duration = wav_duration_from_bytes(data)
            if not one_shot_duration(duration):
                if audit is not None:
                    audit.record("rar", "bad_duration", source_label)
                continue
            yield Candidate(category, "rar", archive, Path(member_name).name, duration,
                            f"{archive}!{member_name}", member_name=member_name,
                            data=data if retain_data else None)


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


def candidate_bucket(candidate):
    if candidate.kind == "plain":
        return str(Path(candidate.source_label).parent)
    archive = str(candidate.path)
    if candidate.member_name:
        parent = str(Path(candidate.member_name).parent)
        return archive if parent == "." else f"{archive}!{parent}"
    return archive


def select_candidates(candidates, limit_per_category):
    by_category = defaultdict(list)
    for candidate in candidates:
        by_category[candidate.category].append(candidate)

    selected = []
    for category in CATEGORIES:
        items = by_category[category]
        if limit_per_category <= 0 or len(items) <= limit_per_category:
            selected.extend(items)
            continue

        buckets = OrderedDict()
        for candidate in items:
            buckets.setdefault(candidate_bucket(candidate), []).append(candidate)

        category_selected = []
        while len(category_selected) < limit_per_category:
            progressed = False
            for bucket in list(buckets):
                if not buckets[bucket]:
                    continue
                category_selected.append(buckets[bucket].pop(0))
                progressed = True
                if len(category_selected) >= limit_per_category:
                    break
            if not progressed:
                break
        selected.extend(category_selected)

    return selected


def candidate_data(candidate, unrar=None, zip_cache=None):
    if candidate.data is not None:
        return candidate.data
    if candidate.kind == "plain":
        return None
    if candidate.kind == "zip":
        if zip_cache is not None:
            return zip_cache.read(candidate.path, candidate.member_name)
        with zipfile.ZipFile(candidate.path) as zf:
            return zf.read(candidate.member_name)
    if candidate.kind == "rar" and unrar:
        extracted = subprocess.run(
            [unrar, "p", "-inul", str(candidate.path), candidate.member_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        return extracted.stdout
    raise RuntimeError(f"unsupported candidate source: {candidate.source_label}")


def copy_candidate(candidate, output, counts, manifest, unrar=None, zip_cache=None):
    counts[candidate.category] += 1
    dest_name = f"{counts[candidate.category]:03d}_{sanitize_name(candidate.original_name)}"
    dest = output / candidate.category / dest_name
    if candidate.kind == "plain":
        shutil.copy2(candidate.path, dest)
    else:
        dest.write_bytes(candidate_data(candidate, unrar=unrar, zip_cache=zip_cache))
        candidate.data = None
    manifest.append((candidate.category, str(dest.relative_to(output)), f"{candidate.duration:.6f}",
                     candidate.source_label))


def write_manifest(output, manifest):
    manifest.sort()
    manifest_path = output / "manifest.tsv"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output,
                                     prefix=".manifest.tsv.", suffix=".tmp",
                                     delete=False) as file:
        tmp_path = Path(file.name)
        file.write("category\tpath\tduration_seconds\tsource\n")
        for row in manifest:
            file.write("\t".join(row) + "\n")
    try:
        tmp_path.replace(manifest_path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise
    try:
        manifest_metadata_path(output).unlink()
    except FileNotFoundError:
        pass
    return manifest_path


def manifest_metadata_path(output):
    return output / "manifest.meta.json"


def source_signature(source, include_archives):
    suffixes = {".wav"}
    if include_archives:
        suffixes.update((".zip", ".rar"))

    digest = hashlib.sha256()
    file_count = 0
    total_bytes = 0
    newest_mtime_ns = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        try:
            stat = path.stat()
            relative = path.relative_to(source).as_posix()
        except OSError:
            continue
        file_count += 1
        total_bytes += stat.st_size
        newest_mtime_ns = max(newest_mtime_ns, stat.st_mtime_ns)
        digest.update(relative.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")
        digest.update(str(stat.st_size).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(stat.st_mtime_ns).encode("ascii"))
        digest.update(b"\n")

    return {
        "files": file_count,
        "bytes": total_bytes,
        "newest_mtime_ns": newest_mtime_ns,
        "sha256": digest.hexdigest(),
    }


def cache_metadata(source, limit_per_category, selection, include_archives, source_filter_text, unrar_available):
    return {
        "version": CACHE_VERSION,
        "source": str(source.resolve()),
        "limit_per_category": limit_per_category,
        "selection": selection,
        "include_archives": include_archives,
        "source_filter": source_filter_text or "",
        "unrar_available": bool(unrar_available),
        "source_signature": source_signature(source, include_archives),
    }


def read_manifest_metadata(output):
    try:
        with manifest_metadata_path(output).open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def write_manifest_metadata(output, metadata):
    metadata_path = manifest_metadata_path(output)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output,
                                     prefix=".manifest.meta.json.", suffix=".tmp",
                                     delete=False) as file:
        tmp_path = Path(file.name)
        json.dump(metadata, file, indent=2, sort_keys=True)
        file.write("\n")
    try:
        tmp_path.replace(metadata_path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def manifest_counts_if_complete(output, limit_per_category, source_filter=None, expected_metadata=None,
                                required_categories=CATEGORIES):
    manifest_path = output / "manifest.tsv"
    if not manifest_path.is_file():
        return None
    if expected_metadata is not None and read_manifest_metadata(output) != expected_metadata:
        return None

    counts = {category: 0 for category in CATEGORIES}
    try:
        with manifest_path.open("r", encoding="utf-8") as file:
            header = file.readline().rstrip("\n").split("\t")
            if header != ["category", "path", "duration_seconds", "source"]:
                return None
            for line in file:
                if not line.strip():
                    continue
                fields = line.rstrip("\n").split("\t")
                if len(fields) != 4:
                    return None
                category, relative_path, duration_text, _source = fields
                if category not in counts:
                    return None
                if source_filter is not None and not source_filter.search(_source):
                    return None
                try:
                    duration = float(duration_text)
                except ValueError:
                    return None
                if not one_shot_duration(duration):
                    return None
                if not (output / relative_path).is_file():
                    return None
                counts[category] += 1
    except OSError:
        return None

    required = 1 if expected_metadata is not None or limit_per_category <= 0 else limit_per_category
    if any(counts[category] < required for category in required_categories):
        return None
    return counts


def copy_selected_samples(candidates, output, unrar=None):
    counts = {category: 0 for category in CATEGORIES}
    manifest = []
    zip_cache = ZipReadCache()

    try:
        for candidate in candidates:
            copy_candidate(candidate, output, counts, manifest, unrar=unrar, zip_cache=zip_cache)
    finally:
        zip_cache.close()

    return counts, write_manifest(output, manifest)


def candidate_matches_filter(candidate, source_filter):
    return source_filter is None or source_filter.search(candidate.source_label)


def copy_samples_first(source, output, limit_per_category, unrar=None, include_archives=True, source_filter=None):
    counts = {category: 0 for category in CATEGORIES}
    manifest = []

    for candidate in collect_plain_wavs(source):
        if not candidate_matches_filter(candidate, source_filter):
            continue
        if reached_sample_limit(counts, limit_per_category):
            break
        if limit_per_category > 0 and counts[candidate.category] >= limit_per_category:
            continue
        copy_candidate(candidate, output, counts, manifest, unrar=unrar)

    if include_archives and not reached_sample_limit(counts, limit_per_category):
        for candidate in collect_zip_wavs(source, retain_data=True):
            if not candidate_matches_filter(candidate, source_filter):
                continue
            if reached_sample_limit(counts, limit_per_category):
                break
            if limit_per_category > 0 and counts[candidate.category] >= limit_per_category:
                continue
            copy_candidate(candidate, output, counts, manifest, unrar=unrar)

    if include_archives and not reached_sample_limit(counts, limit_per_category):
        for candidate in collect_rar_wavs(source, unrar, retain_data=True):
            if not candidate_matches_filter(candidate, source_filter):
                continue
            if reached_sample_limit(counts, limit_per_category):
                break
            if limit_per_category > 0 and counts[candidate.category] >= limit_per_category:
                continue
            copy_candidate(candidate, output, counts, manifest, unrar=unrar)

    return counts, write_manifest(output, manifest)


def copy_samples_spread(source, output, limit_per_category, unrar=None, include_archives=True, source_filter=None):
    candidates = [
        candidate for candidate in collect_plain_wavs(source)
        if candidate_matches_filter(candidate, source_filter)
    ]
    counts = {category: 0 for category in CATEGORIES}
    for candidate in candidates:
        counts[candidate.category] += 1

    needs_archives = limit_per_category <= 0 or any(
        counts[category] < limit_per_category for category in CATEGORIES
    )
    if include_archives and needs_archives:
        candidates.extend(
            candidate for candidate in collect_zip_wavs(source, retain_data=False)
            if candidate_matches_filter(candidate, source_filter)
        )
        candidates.extend(
            candidate for candidate in collect_rar_wavs(source, unrar, retain_data=False)
            if candidate_matches_filter(candidate, source_filter)
        )

    selected = select_candidates(candidates, limit_per_category)
    return copy_selected_samples(selected, output, unrar=unrar)


def copy_samples(source, output, limit_per_category, selection, unrar=None, include_archives=True,
                 source_filter=None):
    if selection == "spread":
        return copy_samples_spread(source, output, limit_per_category, unrar=unrar,
                                   include_archives=include_archives, source_filter=source_filter)
    return copy_samples_first(source, output, limit_per_category, unrar=unrar,
                              include_archives=include_archives, source_filter=source_filter)


def all_candidates(source, unrar=None, include_archives=True, source_filter=None, audit=None):
    candidates = [
        candidate for candidate in collect_plain_wavs(source, audit=audit)
        if candidate_matches_filter(candidate, source_filter)
    ]
    if include_archives:
        candidates.extend(
            candidate for candidate in collect_zip_wavs(source, retain_data=False, audit=audit)
            if candidate_matches_filter(candidate, source_filter)
        )
        candidates.extend(
            candidate for candidate in collect_rar_wavs(source, unrar, retain_data=False, audit=audit)
            if candidate_matches_filter(candidate, source_filter)
        )
    return candidates


def first_selection_candidates(candidates, limit_per_category):
    if limit_per_category <= 0:
        return list(candidates)

    counts = {category: 0 for category in CATEGORIES}
    selected = []
    for candidate in candidates:
        if reached_sample_limit(counts, limit_per_category):
            break
        if counts[candidate.category] >= limit_per_category:
            continue
        counts[candidate.category] += 1
        selected.append(candidate)
    return selected


def count_candidates(candidates):
    counts = {category: 0 for category in CATEGORIES}
    kind_counts = defaultdict(int)
    kind_category_counts = defaultdict(lambda: {category: 0 for category in CATEGORIES})
    for candidate in candidates:
        counts[candidate.category] += 1
        kind_counts[candidate.kind] += 1
        kind_category_counts[candidate.kind][candidate.category] += 1
    return counts, kind_counts, kind_category_counts


def counts_summary(counts):
    return " ".join(f"{category}={counts.get(category, 0)}" for category in CATEGORIES)


def kind_category_summary(kind_category_counts):
    parts = []
    for kind in ("plain", "zip", "rar"):
        counts = kind_category_counts.get(kind)
        if not counts or not any(counts.values()):
            continue
        parts.append(f"{kind}[{counts_summary(counts)}]")
    return " ".join(parts) if parts else "--"


def skip_reason_summary(audit):
    return (
        f"total={audit.total} "
        f"plain={audit.kind_counts['plain']} zip={audit.kind_counts['zip']} "
        f"rar={audit.kind_counts['rar']} "
        + " ".join(f"{reason}={audit.counts[reason]}" for reason in SKIP_REASONS)
    )


def skip_kind_reason_summary(audit):
    parts = []
    for kind in ("plain", "zip", "rar"):
        counts = audit.kind_reason_counts.get(kind)
        if not counts or not any(counts.values()):
            continue
        parts.append(
            f"{kind}[" + " ".join(f"{reason}={counts[reason]}" for reason in SKIP_REASONS) + "]"
        )
    return " ".join(parts) if parts else "--"


def skip_example_summary(audit):
    parts = []
    for reason in SKIP_REASONS:
        examples = audit.examples.get(reason, [])
        if not examples:
            continue
        parts.append(
            f"{reason}="
            + ",".join(compact_bucket_label(example, max_parts=4) for example in examples)
        )
    return " ".join(parts) if parts else "--"


def compact_bucket_label(label, max_parts=3):
    archive, separator, member = label.partition("!")
    if separator:
        return f"{compact_bucket_label(archive, max_parts)}!{compact_bucket_label(member, max_parts)}"
    parts = Path(label).parts
    if len(parts) <= max_parts:
        return label
    return "/".join(parts[-max_parts:])


def source_bucket_summary(candidates, limit=8):
    counts = defaultdict(int)
    for candidate in candidates:
        counts[candidate_bucket(candidate)] += 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], compact_bucket_label(item[0])))
    top = " ".join(
        f"{compact_bucket_label(bucket)}={count}"
        for bucket, count in ordered[:max(0, limit)]
    )
    return len(counts), top or "--"


def print_sample_audit(source, limit_per_category, selection, unrar=None, include_archives=True,
                       source_filter=None):
    skip_audit = SkipAudit()
    candidates = all_candidates(source, unrar=unrar, include_archives=include_archives,
                                source_filter=source_filter, audit=skip_audit)
    candidate_counts, kind_counts, candidate_kind_category_counts = count_candidates(candidates)
    if selection == "spread":
        selected = select_candidates(candidates, limit_per_category)
    else:
        selected = first_selection_candidates(candidates, limit_per_category)
    selected_counts, _selected_kind_counts, selected_kind_category_counts = count_candidates(selected)
    candidate_bucket_count, candidate_bucket_top = source_bucket_summary(candidates)
    selected_bucket_count, selected_bucket_top = source_bucket_summary(selected)

    print(
        "prepare_drum_samples audit: "
        f"candidates={len(candidates)} plain={kind_counts['plain']} "
        f"zip={kind_counts['zip']} rar={kind_counts['rar']} source={source}"
    )
    print(f"candidate counts {counts_summary(candidate_counts)}")
    print(f"candidate kind/category {kind_category_summary(candidate_kind_category_counts)}")
    print(f"candidate source buckets total={candidate_bucket_count} top={candidate_bucket_top}")
    print(f"skipped counts {skip_reason_summary(skip_audit)}")
    print(f"skipped kind/reason {skip_kind_reason_summary(skip_audit)}")
    print(f"skipped examples {skip_example_summary(skip_audit)}")
    print(
        f"selected counts limit={limit_per_category} selection={selection} "
        f"{counts_summary(selected_counts)}"
    )
    print(f"selected kind/category {kind_category_summary(selected_kind_category_counts)}")
    print(f"selected source buckets total={selected_bucket_count} top={selected_bucket_top}")


def main():
    parser = argparse.ArgumentParser(description="Copy one-shot drum samples into a build-local fixture directory.")
    parser.add_argument("--source", default=os.environ.get("DRUM_SAMPLE_SOURCE_DIR", "/media/kyz/sshflashtor/DrumSamples"))
    parser.add_argument("--output", default=os.environ.get("DRUM_SAMPLE_BUILD_DIR", "build/drum_samples"))
    parser.add_argument("--limit-per-category", type=int, default=int(os.environ.get("DRUM_SAMPLE_LIMIT", "32")))
    parser.add_argument("--selection", choices=("first", "spread"), default=os.environ.get("DRUM_SAMPLE_SELECTION", "first"))
    parser.add_argument("--unrar", default=os.environ.get("UNRAR", "unrar"))
    parser.add_argument("--no-archives", action="store_true",
                        help="copy only plain WAV files; ZIP/RAR archives are skipped")
    parser.add_argument("--source-filter", default=os.environ.get("DRUM_SAMPLE_SOURCE_FILTER", ""),
                        help="optional regex matched against the manifest source label")
    parser.add_argument("--required-categories", default=os.environ.get("DRUM_SAMPLE_REQUIRED_CATEGORIES", ""),
                        help="comma-separated categories that must be present (default: every drum category)")
    parser.add_argument("--audit", action="store_true",
                        help="print candidate and selected category counts without writing samples")
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("DRUM_SAMPLE_REFRESH") == "1",
                        help="rescan sources and rewrite the output manifest even when a complete manifest exists")
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    if not source.is_dir():
        raise SystemExit(f"prepare_drum_samples: source directory not found: {source}")

    limit_per_category = max(0, args.limit_per_category)
    if args.required_categories:
        required_categories = tuple(category.strip().lower() for category in args.required_categories.split(",")
                                    if category.strip())
        unknown_categories = sorted(set(required_categories) - set(CATEGORIES))
        if not required_categories or unknown_categories:
            unknown = ", ".join(unknown_categories) or "none"
            raise SystemExit(f"prepare_drum_samples: invalid --required-categories value: {unknown}")
    else:
        required_categories = CATEGORIES
    source_filter = None
    if args.source_filter:
        try:
            source_filter = re.compile(args.source_filter, re.I)
        except re.error as exc:
            raise SystemExit(f"prepare_drum_samples: invalid --source-filter regex: {exc}") from exc

    unrar = shutil.which(args.unrar) if args.unrar else None
    if args.audit:
        print_sample_audit(source, limit_per_category, args.selection, unrar=unrar,
                           include_archives=not args.no_archives, source_filter=source_filter)
        return

    ensure_dirs(output)
    if not args.refresh:
        expected_metadata = cache_metadata(source, limit_per_category, args.selection, not args.no_archives,
                                           args.source_filter, unrar is not None)
        counts = manifest_counts_if_complete(output, limit_per_category, source_filter=source_filter,
                                             expected_metadata=expected_metadata,
                                             required_categories=required_categories)
        if counts is not None:
            summary = " ".join(f"{category}={counts[category]}" for category in CATEGORIES)
            print(f"prepare_drum_samples: reused {output / 'manifest.tsv'} ({summary})")
            return
    else:
        expected_metadata = cache_metadata(source, limit_per_category, args.selection, not args.no_archives,
                                           args.source_filter, unrar is not None)

    counts, manifest_path = copy_samples(source, output, limit_per_category, args.selection,
                                         unrar=unrar, include_archives=not args.no_archives,
                                         source_filter=source_filter)
    summary = " ".join(f"{category}={counts[category]}" for category in CATEGORIES)

    missing = [category for category in required_categories if counts[category] == 0]
    if missing:
        raise SystemExit("prepare_drum_samples: missing categories: " + ", ".join(missing))
    write_manifest_metadata(output, expected_metadata)
    print(f"prepare_drum_samples: wrote {manifest_path} ({summary})")


if __name__ == "__main__":
    main()
