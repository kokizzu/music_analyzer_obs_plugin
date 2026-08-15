#!/usr/bin/env python3

import argparse
import csv
import fcntl
import os
from pathlib import Path
import re
import shutil
import zipfile


FIXTURE_VERSION = "maps-piano-maestro-v1"
DEFAULT_KINDS = "UCHO,RAND,MUS"


def sanitize(text, limit=140):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def archive_signature(path):
    archive = Path(path)
    if not archive.is_file():
        return "missing"
    stat = archive.stat()
    return f"{stat.st_size}:{int(stat.st_mtime)}"


def signature_text(args):
    return "|".join([
        FIXTURE_VERSION,
        f"archive={Path(args.archive)}:{archive_signature(args.archive)}",
        f"limit={args.limit}",
        f"kinds={args.kinds}",
    ])


def normalized_kind_set(text):
    return {token.strip().upper() for token in text.split(",") if token.strip()}


def detect_kind(member_name):
    parts = [part.upper() for part in Path(member_name).parts]
    basename = Path(member_name).name.upper()
    for kind in ("UCHO", "RAND", "MUS", "ISOL"):
        if kind in parts or f"_{kind}" in basename:
            return kind
    return "OTHER"


def strip_audio_extension(member_name):
    path = Path(member_name)
    suffix = path.suffix.lower()
    if suffix not in (".wav", ".mid", ".midi"):
        return None
    return str(path.with_suffix(""))


def collect_pairs(archive, allowed_kinds):
    audio_by_stem = {}
    midi_by_stem = {}
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            suffix = Path(info.filename).suffix.lower()
            stem = strip_audio_extension(info.filename)
            if stem is None:
                continue
            kind = detect_kind(info.filename)
            if kind not in allowed_kinds:
                continue
            if suffix == ".wav":
                audio_by_stem.setdefault(stem, info.filename)
            elif suffix in (".mid", ".midi"):
                midi_by_stem.setdefault(stem, info.filename)

    pairs = []
    for stem in sorted(audio_by_stem):
        midi_member = midi_by_stem.get(stem)
        if not midi_member:
            continue
        pairs.append({
            "stem": stem,
            "kind": detect_kind(audio_by_stem[stem]),
            "audio_member": audio_by_stem[stem],
            "midi_member": midi_member,
        })
    return pairs


def select_pairs(pairs, limit):
    if limit <= 0 or len(pairs) <= limit:
        return list(pairs)

    by_kind = {}
    for pair in pairs:
        by_kind.setdefault(pair["kind"], []).append(pair)
    for rows in by_kind.values():
        rows.sort(key=lambda row: row["stem"])

    selected = []
    kind_order = [kind for kind in ("UCHO", "RAND", "MUS", "ISOL", "OTHER") if kind in by_kind]
    while len(selected) < limit:
        changed = False
        for kind in kind_order:
            rows = by_kind[kind]
            if not rows:
                continue
            selected.append(rows.pop(0))
            changed = True
            if len(selected) >= limit:
                break
        if not changed:
            break

    selected.sort(key=lambda row: (row["kind"], row["stem"]))
    return selected


def read_existing_metadata(path):
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            rows.append(row)
    return rows


def cache_ok(output, signature, min_recordings):
    signature_path = output / ".maps_piano_signature"
    metadata = output / "maestro-v3.0.0.csv"
    if not signature_path.is_file() or not metadata.is_file():
        return False
    if signature_path.read_text(encoding="utf-8") != signature:
        return False
    rows = read_existing_metadata(metadata)
    if len(rows) < min_recordings:
        return False
    for row in rows:
        if not (output / row.get("audio_filename", "")).is_file():
            return False
        if not (output / row.get("midi_filename", "")).is_file():
            return False
    return True


def extract_member(zf, member, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(member) as source, dest.open("wb") as target:
        shutil.copyfileobj(source, target)


def write_metadata(output, rows):
    metadata = output / "maestro-v3.0.0.csv"
    tmp = metadata.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "canonical_composer",
                "canonical_title",
                "split",
                "year",
                "midi_filename",
                "audio_filename",
                "duration",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(metadata)
    return metadata


def preserve_previous_output(output):
    """Move an incomplete external subset aside without a slow recursive delete."""
    if not output.exists():
        return None
    index = 1
    while True:
        backup = output.with_name(f"{output.name}.incomplete-{index}")
        if not backup.exists():
            output.replace(backup)
            return backup


def prepare(args):
    archive = Path(args.archive)
    if not archive.is_file():
        raise SystemExit(f"prepare_maps_piano_samples: missing archive {archive}")

    output = Path(args.output)
    # Corpus fixtures live outside build; build/<fixture> is intentionally a symlink.
    # Refresh the target contents without replacing that required link.
    if output.is_symlink():
        output = output.resolve()
    lock_path = output.parent / f".{output.name}.prepare.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SystemExit(f"prepare_maps_piano_samples: preparation already active for {output}") from exc
        min_recordings = max(0, args.min_recordings)
        signature = signature_text(args)
        if not args.refresh and cache_ok(output, signature, min_recordings):
            rows = read_existing_metadata(output / "maestro-v3.0.0.csv")
            print(f"prepare_maps_piano_samples: reused {output / 'maestro-v3.0.0.csv'} ({len(rows)} recordings)")
            return len(rows)

        allowed_kinds = normalized_kind_set(args.kinds)
        pairs = collect_pairs(archive, allowed_kinds)
        selected = select_pairs(pairs, max(0, args.limit))
        if not selected:
            raise SystemExit(
                "prepare_maps_piano_samples: no MAPS WAV/MIDI pairs found for kinds "
                + ",".join(sorted(allowed_kinds))
            )

        preserved = preserve_previous_output(output)
        output.mkdir(parents=True, exist_ok=True)

        rows = []
        kind_counts = {}
        with zipfile.ZipFile(archive) as zf:
            for index, pair in enumerate(selected, start=1):
                kind = pair["kind"].lower()
                stem = sanitize(Path(pair["stem"]).name)
                row_stem = f"{index:04d}_{kind}_{stem}"
                audio_rel = Path("maps") / kind / f"{row_stem}.wav"
                midi_rel = Path("maps") / kind / f"{row_stem}.mid"
                extract_member(zf, pair["audio_member"], output / audio_rel)
                extract_member(zf, pair["midi_member"], output / midi_rel)
                kind_counts[pair["kind"]] = kind_counts.get(pair["kind"], 0) + 1
                rows.append({
                    "canonical_composer": "MAPS",
                    "canonical_title": row_stem,
                    "split": "test",
                    "year": "2006",
                    "midi_filename": str(midi_rel),
                    "audio_filename": str(audio_rel),
                    "duration": "",
                })

        metadata = write_metadata(output, rows)
        (output / ".maps_piano_signature").write_text(signature, encoding="utf-8")
    if len(rows) < min_recordings:
        raise SystemExit(
            f"prepare_maps_piano_samples: expected at least {min_recordings} recordings, got {len(rows)}"
        )

    kind_text = " ".join(f"{kind}={kind_counts[kind]}" for kind in sorted(kind_counts))
    preserved_text = f"; preserved incomplete subset at {preserved}" if preserved else ""
    print(f"prepare_maps_piano_samples: wrote {metadata} ({len(rows)} recordings; {kind_text}){preserved_text}")
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare MAPS piano WAV/MIDI pairs as MAESTRO-shaped fixtures.")
    parser.add_argument("--archive", default=os.environ.get(
        "MAPS_PIANO_ARCHIVE",
        "build/real_sample_sources/maps_piano/ENSTDkCl.zip",
    ))
    parser.add_argument("--output", default=os.environ.get(
        "MAPS_PIANO_SAMPLE_DIR",
        "build/maps_piano_samples",
    ))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("MAPS_PIANO_RECORDING_LIMIT", "80")))
    parser.add_argument("--min-recordings", type=int,
                        default=int(os.environ.get("MAPS_PIANO_MIN_RECORDINGS", "40")))
    parser.add_argument("--kinds", default=os.environ.get("MAPS_PIANO_KINDS", DEFAULT_KINDS))
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("MAPS_PIANO_REFRESH") == "1")
    args = parser.parse_args(argv)
    args.limit = max(0, args.limit)
    args.min_recordings = max(0, args.min_recordings)
    prepare(args)


if __name__ == "__main__":
    raise SystemExit(main())
