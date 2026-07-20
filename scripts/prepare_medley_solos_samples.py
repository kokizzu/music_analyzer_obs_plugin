#!/usr/bin/env python3

import argparse
import csv
import os
from pathlib import Path
import re
import shutil
import tarfile


FIXTURE_VERSION = "medley-solos-family-v1"

FAMILY_BY_INSTRUMENT = {
    "clarinet": "other",
    "distorted electric guitar": "guitar",
    "female singer": "vocals",
    "flute": "other",
    "piano": "piano",
    "tenor saxophone": "other",
    "trumpet": "other",
    "violin": "other",
}


def sanitize(text, limit=120):
    cleaned = re.sub(r"[^A-Za-z0-9._#-]+", "_", str(text)).strip("._-")
    return cleaned[:limit] or "sample"


def medley_filename(row):
    return f"Medley-solos-DB_{row['subset']}-{row['instrument_id']}_{row['uuid4']}.wav"


def read_metadata(path, subsets):
    selected_subsets = {subset.strip() for subset in subsets.split(",") if subset.strip()}
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required = {"subset", "instrument", "instrument_id", "song_id", "uuid4"}
        missing = sorted(required - set(reader.fieldnames or ()))
        if missing:
            raise SystemExit(f"prepare_medley_solos_samples: metadata missing columns {', '.join(missing)}")
        for row in reader:
            instrument = row["instrument"].strip()
            family = FAMILY_BY_INSTRUMENT.get(instrument)
            if family is None:
                continue
            if selected_subsets and row["subset"].strip() not in selected_subsets:
                continue
            rows.append({
                "subset": row["subset"].strip(),
                "instrument": instrument,
                "instrument_id": row["instrument_id"].strip(),
                "song_id": row["song_id"].strip(),
                "uuid4": row["uuid4"].strip(),
                "family": family,
            })
    return rows


def select_rows(rows, limit_per_instrument):
    counts = {}
    selected = []
    for row in rows:
        instrument = row["instrument"]
        count = counts.get(instrument, 0)
        if limit_per_instrument > 0 and count >= limit_per_instrument:
            continue
        counts[instrument] = count + 1
        selected.append(row)
    return selected, counts


def archive_signature(path):
    archive = Path(path)
    if not archive.is_file():
        return "missing"
    stat = archive.stat()
    return f"{stat.st_size}:{int(stat.st_mtime)}"


def signature_text(args):
    metadata = Path(args.metadata)
    metadata_stamp = "missing"
    if metadata.is_file():
        stat = metadata.stat()
        metadata_stamp = f"{stat.st_size}:{int(stat.st_mtime)}"
    return "|".join([
        FIXTURE_VERSION,
        f"metadata={metadata}:{metadata_stamp}",
        f"archive={Path(args.archive)}:{archive_signature(args.archive)}",
        f"limit_per_instrument={args.limit_per_instrument}",
        f"subsets={args.subsets}",
    ])


def read_manifest_counts(manifest):
    counts = {}
    with Path(manifest).open("r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file, delimiter="\t"):
            family = row.get("family", "")
            counts[family] = counts.get(family, 0) + 1
    return counts


def cache_ok(output, signature, min_total, min_counts):
    signature_path = output / ".medley_solos_signature"
    manifest = output / "manifest.tsv"
    if not signature_path.is_file() or not manifest.is_file():
        return False
    if signature_path.read_text(encoding="utf-8") != signature:
        return False
    counts = read_manifest_counts(manifest)
    if sum(counts.values()) < min_total:
        return False
    for family, minimum in min_counts.items():
        if counts.get(family, 0) < minimum:
            return False
    return True


def tar_members_by_basename(archive, basenames):
    members = {}
    wanted = set(basenames)
    with tarfile.open(archive, "r:*") as tar:
        for member in tar:
            if not member.isfile():
                continue
            basename = Path(member.name).name
            if basename in wanted and basename not in members:
                members[basename] = member.name
            if len(members) == len(wanted):
                break
    return members


def extract_selected(archive, selected, output):
    by_filename = {medley_filename(row): row for row in selected}
    members = tar_members_by_basename(archive, by_filename)
    missing = sorted(set(by_filename) - set(members))
    if missing:
        preview = ", ".join(missing[:5])
        raise SystemExit(
            f"prepare_medley_solos_samples: archive missing {len(missing)} selected WAV files: {preview}"
        )

    rows = []
    with tarfile.open(archive, "r:*") as tar:
        for source_name, row in by_filename.items():
            member_name = members[source_name]
            extracted = tar.extractfile(member_name)
            if extracted is None:
                raise SystemExit(f"prepare_medley_solos_samples: cannot extract {member_name}")
            track_id = sanitize(f"{row['subset']}_{row['instrument']}_{row['uuid4']}")
            rel_path = Path("audio") / row["family"] / f"{track_id}.wav"
            dest = output / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("wb") as file:
                shutil.copyfileobj(extracted, file)
            rows.append({
                "id": track_id,
                "family": row["family"],
                "instrument": row["instrument"],
                "subset": row["subset"],
                "song_id": row["song_id"],
                "uuid4": row["uuid4"],
                "path": str(rel_path),
            })
    return rows


def write_manifest(output, rows):
    manifest = output / "manifest.tsv"
    tmp = manifest.with_suffix(".tsv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=("id", "family", "instrument", "subset", "song_id", "uuid4", "path"),
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(manifest)
    return manifest


def parse_min_counts(text):
    counts = {}
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue
        if "=" not in token:
            raise SystemExit(f"prepare_medley_solos_samples: bad --min-count token {token}")
        family, value = token.split("=", 1)
        counts[family.strip()] = int(value)
    return counts


def prepare(args):
    metadata = Path(args.metadata)
    archive = Path(args.archive)
    if not metadata.is_file():
        raise SystemExit(f"prepare_medley_solos_samples: missing metadata {metadata}")
    if not archive.is_file():
        raise SystemExit(f"prepare_medley_solos_samples: missing archive {archive}")

    output = Path(args.output)
    min_counts = parse_min_counts(args.min_counts)
    signature = signature_text(args)
    min_total = max(0, args.min_samples)
    if not args.refresh and cache_ok(output, signature, min_total, min_counts):
        counts = read_manifest_counts(output / "manifest.tsv")
        count_text = " ".join(f"{family}={counts[family]}" for family in sorted(counts))
        print(f"prepare_medley_solos_samples: reused {output / 'manifest.tsv'} ({count_text})")
        return sum(counts.values())

    rows = read_metadata(metadata, args.subsets)
    selected, instrument_counts = select_rows(rows, args.limit_per_instrument)
    if not selected:
        raise SystemExit("prepare_medley_solos_samples: no selected metadata rows")

    if output.exists():
        shutil.rmtree(output)
    (output / "audio").mkdir(parents=True, exist_ok=True)

    manifest_rows = extract_selected(archive, selected, output)
    manifest = write_manifest(output, manifest_rows)
    (output / ".medley_solos_signature").write_text(signature, encoding="utf-8")

    family_counts = {}
    for row in manifest_rows:
        family_counts[row["family"]] = family_counts.get(row["family"], 0) + 1

    if len(manifest_rows) < min_total:
        raise SystemExit(
            f"prepare_medley_solos_samples: expected at least {min_total} samples, got {len(manifest_rows)}"
        )
    for family, minimum in min_counts.items():
        if family_counts.get(family, 0) < minimum:
            raise SystemExit(
                f"prepare_medley_solos_samples: expected at least {minimum} {family} samples, "
                f"got {family_counts.get(family, 0)}"
            )

    family_text = " ".join(f"{family}={family_counts[family]}" for family in sorted(family_counts))
    instrument_text = " ".join(f"{instrument}={instrument_counts[instrument]}" for instrument in sorted(instrument_counts))
    print(
        f"prepare_medley_solos_samples: wrote {manifest} ({len(manifest_rows)} samples; "
        f"{family_text}; instruments {instrument_text})"
    )
    return len(manifest_rows)


def main():
    parser = argparse.ArgumentParser(description="Prepare Medley-solos-DB real solo-instrument samples.")
    parser.add_argument("--metadata", default=os.environ.get("MEDLEY_SOLOS_METADATA",
                                                            "build/real_sample_sources/medley_solos/Medley-solos-DB_metadata.csv"))
    parser.add_argument("--archive", default=os.environ.get("MEDLEY_SOLOS_ARCHIVE",
                                                           "build/real_sample_sources/medley_solos/Medley-solos-DB.tar.gz"))
    parser.add_argument("--output", default=os.environ.get("MEDLEY_SOLOS_SAMPLE_DIR",
                                                          "build/medley_solos_samples"))
    parser.add_argument("--limit-per-instrument", type=int,
                        default=int(os.environ.get("MEDLEY_SOLOS_LIMIT_PER_INSTRUMENT", "120")))
    parser.add_argument("--min-samples", type=int,
                        default=int(os.environ.get("MEDLEY_SOLOS_MIN_SAMPLES", "600")))
    parser.add_argument("--min-counts", default=os.environ.get(
        "MEDLEY_SOLOS_MIN_COUNTS",
        "guitar=100,piano=100,vocals=100,other=300",
    ))
    parser.add_argument("--subsets", default=os.environ.get("MEDLEY_SOLOS_SUBSETS", "test,validation,training"))
    parser.add_argument("--refresh", action="store_true",
                        default=os.environ.get("MEDLEY_SOLOS_REFRESH") == "1")
    args = parser.parse_args()
    args.limit_per_instrument = max(0, args.limit_per_instrument)
    args.min_samples = max(0, args.min_samples)
    prepare(args)


if __name__ == "__main__":
    main()
