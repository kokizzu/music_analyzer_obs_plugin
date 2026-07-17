#!/usr/bin/env python3

import argparse
import csv
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile


FIXTURE_VERSION = "tinysol-v1"


def normalize_bool(value):
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def family_for_values(family, instrument_name):
    instrument = instrument_name.strip().lower()
    family = family.strip().lower()
    if instrument == "contrabass":
        return "bass"
    if family == "keyboards":
        return "piano"
    return "other"


def note_name_from_midi(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def sanitize_id(text):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")


def source_name_from_text(text):
    name = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-")


def output_name(row):
    source = row.get("source") or source_name(row)
    stem = Path(row.get("archive_path") or row["Path"]).stem
    return f"tinysol_{source}_{sanitize_id(stem)}.wav"


def archive_folder_name(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text.strip()).strip("_")


def read_metadata(path, include_resampled):
    def value(row, *names):
        for name in names:
            if name in row:
                return row[name]
        return ""

    rows = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required = [
            ("Path",),
            ("Family",),
            ("Instrument", "Instrument (abbr.)"),
            ("Instrument Name", "Instrument (in full)"),
            ("Technique Name", "Technique (in full)"),
            ("Pitch",),
            ("Pitch ID",),
            ("Dynamics",),
            ("Resampled",),
        ]
        fieldnames = set(reader.fieldnames or [])
        missing = ["/".join(names) for names in required if not any(name in fieldnames for name in names)]
        if missing:
            raise SystemExit("prepare_tinysol_samples: missing metadata columns: " + ", ".join(missing))
        for row in reader:
            family = value(row, "Family").strip()
            instrument = value(row, "Instrument", "Instrument (abbr.)").strip()
            instrument_name = value(row, "Instrument Name", "Instrument (in full)").strip()
            technique_name = value(row, "Technique Name", "Technique (in full)").strip()
            if not include_resampled and normalize_bool(value(row, "Resampled")):
                continue
            try:
                midi = int(value(row, "Pitch ID"))
            except ValueError:
                continue
            if midi < 21 or midi > 108:
                continue
            rows.append({
                "archive_path": value(row, "Path").strip(),
                "family": family_for_values(family, instrument_name),
                "nsynth_family": family.lower(),
                "source": source_name_from_text(instrument_name),
                "instrument": instrument_name,
                "instrument_abbr": instrument,
                "technique": technique_name,
                "midi": midi,
                "note": note_name_from_midi(midi),
                "dynamics": value(row, "Dynamics").strip(),
                "resampled": normalize_bool(value(row, "Resampled")),
            })
    rows.sort(key=lambda item: (item["family"], item["source"], item["midi"], item["dynamics"], item["archive_path"]))
    return rows


def limited_rows(rows, limit):
    if limit <= 0 or len(rows) <= limit:
        return rows
    return rows[:limit]


def find_zip_member(archive, row):
    wanted = row["archive_path"]
    raw_wanted = wanted
    wanted = wanted.lstrip("/")
    names = archive.namelist()
    if wanted in names:
        return wanted
    candidates = [
        wanted,
        f"TinySOL/audio/{wanted}",
        "/".join([
            "TinySOL",
            "audio",
            archive_folder_name(row["nsynth_family"]),
            archive_folder_name(row["instrument"]),
            archive_folder_name(row["technique"]),
            Path(raw_wanted).name,
        ]),
    ]
    seen = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if candidate in names:
            return candidate
        suffix = "/" + candidate
        for name in names:
            if name.endswith(suffix) and not name.startswith("__MACOSX/") and "/._" not in name:
                return name
    filename = "/" + Path(raw_wanted).name
    basename_matches = [
        name for name in names
        if name.endswith(filename) and not name.startswith("__MACOSX/") and "/._" not in name
    ]
    if len(basename_matches) == 1:
        return basename_matches[0]
    return None


def copy_member(archive, member, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with archive.open(member) as source, temporary_path.open("wb") as target:
        shutil.copyfileobj(source, target)
    temporary_path.replace(output_path)


def write_manifest(path, rows):
    with path.open("w", encoding="utf-8") as file:
        file.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities\n")
        for row in rows:
            file.write(
                "\t".join([
                    row["id"],
                    row["family"],
                    row["nsynth_family"],
                    row["source"],
                    str(row["midi"]),
                    row["note"],
                    row["path"],
                    row["qualities"],
                ]) + "\n"
            )


def manifest_complete(path, min_rows):
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
            if not (root / fields[6]).is_file():
                return False
            rows += 1
    return rows >= max(1, min_rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare TinySOL real isolated-note fixtures.")
    parser.add_argument("--metadata", default=os.environ.get(
        "TINYSOL_METADATA_PATH",
        "build/real_sample_sources/tinysol/TinySOL_metadata.csv"))
    parser.add_argument("--archive", default=os.environ.get(
        "TINYSOL_ARCHIVE",
        "build/real_sample_sources/tinysol/TinySOL.zip"))
    parser.add_argument("--output", default=os.environ.get("TINYSOL_SAMPLE_DIR",
                                                           "build/tinysol_samples"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("TINYSOL_SAMPLE_LIMIT", "0")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("TINYSOL_MIN_SAMPLES", "1000")))
    parser.add_argument("--include-resampled", action="store_true",
                        default=os.environ.get("TINYSOL_INCLUDE_RESAMPLED") == "1")
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("TINYSOL_REFRESH") == "1")
    args = parser.parse_args(argv)

    metadata_path = Path(args.metadata)
    archive_path = Path(args.archive)
    output_dir = Path(args.output)
    manifest_path = output_dir / "manifest.tsv"
    min_samples = max(0, args.min_samples)
    if not args.refresh and manifest_complete(manifest_path, min_samples):
        print(f"prepare_tinysol_samples: keeping existing {manifest_path}")
        return

    if not metadata_path.is_file():
        raise SystemExit(f"prepare_tinysol_samples: missing metadata: {metadata_path}")
    if not archive_path.is_file():
        raise SystemExit(f"prepare_tinysol_samples: missing archive: {archive_path}")

    candidates = limited_rows(read_metadata(metadata_path, args.include_resampled), args.limit)
    if not candidates:
        raise SystemExit("prepare_tinysol_samples: no usable TinySOL metadata rows")

    output_dir.mkdir(parents=True, exist_ok=True)
    prepared = []
    missing = []
    with zipfile.ZipFile(archive_path) as archive:
        for row in candidates:
            member = find_zip_member(archive, row)
            if not member:
                missing.append(row["archive_path"])
                continue
            rel_path = Path("audio") / output_name(row)
            output_path = output_dir / rel_path
            if not output_path.is_file():
                copy_member(archive, member, output_path)
            prepared_row = dict(row)
            prepared_row["id"] = Path(rel_path).stem
            prepared_row["path"] = str(rel_path)
            prepared_row["qualities"] = f"{row['instrument']},{row['dynamics']},resampled={int(row['resampled'])},{FIXTURE_VERSION}"
            prepared.append(prepared_row)

    required_prepared = max(1, min_samples)
    if len(prepared) < required_prepared:
        partial_path = manifest_path.with_suffix(manifest_path.suffix + ".partial")
        write_manifest(partial_path, prepared)
        print(f"prepare_tinysol_samples: wrote {len(prepared)} rows to {partial_path}", file=sys.stderr)
        raise SystemExit(
            f"prepare_tinysol_samples: expected at least {required_prepared} prepared samples, "
            f"got {len(prepared)}"
        )

    write_manifest(manifest_path, prepared)
    counts = {}
    for row in prepared:
        counts[row["family"]] = counts.get(row["family"], 0) + 1
    summary = " ".join(f"{name}={counts[name]}" for name in sorted(counts))
    print(f"prepare_tinysol_samples: wrote {len(prepared)} rows to {manifest_path} ({summary})")
    if missing:
        print(f"prepare_tinysol_samples: missing {len(missing)} archive members", file=sys.stderr)
        for member in missing[:12]:
            print(f"prepare_tinysol_samples: missing {member}", file=sys.stderr)


if __name__ == "__main__":
    main()
