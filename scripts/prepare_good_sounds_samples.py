#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile


FIXTURE_VERSION = "good-sounds-v1"
NOTE_PITCH_CLASS = {
    "C": 0,
    "B#": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "Fb": 4,
    "E#": 5,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "Cb": 11,
}


def run(command):
    subprocess.run(command, check=True)


def sanitize(text):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_") or "sample"


def source_name(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).strip().lower()).strip("-") or "unknown"


def analyzer_family(instrument):
    text = source_name(instrument)
    if text in {"bass", "double-bass", "contrabass", "upright-bass", "electric-bass"}:
        return "bass"
    if "guitar" in text:
        return "guitar"
    if text in {"piano", "keyboard", "keyboards", "organ", "accordion"}:
        return "piano"
    if text in {"voice", "vocal", "vocals", "singer", "singing"}:
        return "vocals"
    return "other"


def note_name_from_midi(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def midi_from_note(note, octave):
    note_text = str(note).strip().replace("♯", "#").replace("♭", "b")
    octave_text = str(octave).strip()
    if not note_text:
        return None
    match = re.fullmatch(r"([A-Ga-g](?:#|b)?)(-?[0-9]+)", note_text)
    if match and not octave_text:
        note_text, octave_text = match.groups()
    if not octave_text:
        return None
    if note_text not in NOTE_PITCH_CLASS and note_text[:1].upper() + note_text[1:] in NOTE_PITCH_CLASS:
        note_text = note_text[:1].upper() + note_text[1:]
    try:
        octave_value = int(float(octave_text))
    except ValueError:
        return None
    pitch_class = NOTE_PITCH_CLASS.get(note_text)
    if pitch_class is None:
        return None
    return (octave_value + 1) * 12 + pitch_class


def maybe_int(value):
    if value is None:
        return None
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return None


def table_columns(conn, table):
    try:
        rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    except sqlite3.DatabaseError:
        return []
    return [str(row[1]) for row in rows]


def table_exists(conn, table):
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND lower(name)=lower(?)",
        (table,),
    ).fetchone() is not None


def prefixed_select(alias, columns, prefix):
    return [f'{alias}."{column}" AS "{prefix}_{column}"' for column in columns]


def prefixed_row(row):
    return {key.lower(): row[key] for key in row.keys()}


def first_value(row, prefixes, names):
    for prefix in prefixes:
        for name in names:
            key = f"{prefix}_{name}".lower() if prefix else name.lower()
            value = row.get(key)
            if value is not None and str(value).strip() != "":
                return value
    return None


def query_official_rows(conn):
    if not table_exists(conn, "takes") or not table_exists(conn, "sounds"):
        return []
    take_columns = table_columns(conn, "takes")
    sound_columns = table_columns(conn, "sounds")
    pack_columns = table_columns(conn, "packs") if table_exists(conn, "packs") else []
    select = prefixed_select("t", take_columns, "take") + prefixed_select("s", sound_columns, "sound")
    joins = ' FROM "takes" t JOIN "sounds" s ON t."sound_id" = s."id"'
    take_column_set = {column.lower() for column in take_columns}
    sound_column_set = {column.lower() for column in sound_columns}
    if pack_columns and "pack_id" in take_column_set:
        select += prefixed_select("p", pack_columns, "pack")
        joins += ' LEFT JOIN "packs" p ON t."pack_id" = p."id"'
    elif pack_columns and "pack_id" in sound_column_set:
        select += prefixed_select("p", pack_columns, "pack")
        joins += ' LEFT JOIN "packs" p ON s."pack_id" = p."id"'
    query = "SELECT " + ", ".join(select) + joins
    return [prefixed_row(row) for row in conn.execute(query)]


def query_generic_rows(conn):
    rows = []
    table_names = [
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        if not str(row[0]).startswith("sqlite_")
    ]
    for table in table_names:
        columns = table_columns(conn, table)
        lower_columns = {column.lower() for column in columns}
        if not lower_columns & {"filename", "file_name", "path", "file", "audio", "audio_path"}:
            continue
        if not (lower_columns & {"midi", "midi_note", "pitch", "note"}):
            continue
        select = prefixed_select("r", columns, "row")
        for row in conn.execute("SELECT " + ", ".join(select) + f' FROM "{table}" r'):
            rows.append(prefixed_row(row))
    return rows


def find_database_member(archive):
    candidates = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and Path(name).suffix.lower() in {".sqlite", ".sqlite3", ".db"}
    ]
    if not candidates:
        raise SystemExit("prepare_good_sounds_samples: no SQLite database found in archive")
    candidates.sort(key=lambda name: (0 if "good" in name.lower() else 1, len(name), name))
    return candidates[0]


def normalized_names(archive):
    names = [name for name in archive.namelist() if not name.endswith("/")]
    exact = {name: name for name in names}
    folded = {name.lower(): name for name in names}
    return names, exact, folded


def candidate_audio_names(filename, pack):
    raw = str(filename).strip().replace("\\", "/").lstrip("/")
    if not raw:
        return []
    variants = [raw]
    if not Path(raw).suffix:
        variants.append(raw + ".flac")
    pack_text = str(pack or "").strip().replace("\\", "/").strip("/")
    expanded = []
    for value in variants:
        expanded.append(value)
        expanded.append("sound_files/" + value)
        if pack_text:
            expanded.append(f"{pack_text}/{value}")
            expanded.append(f"sound_files/{pack_text}/{value}")
    seen = set()
    result = []
    for value in expanded:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def find_audio_member(archive_names, exact, folded, filename, pack):
    for candidate in candidate_audio_names(filename, pack):
        if candidate in exact:
            return exact[candidate]
        lowered = candidate.lower()
        if lowered in folded:
            return folded[lowered]

    basename = Path(str(filename).replace("\\", "/")).name.lower()
    if not basename:
        return None
    if not Path(basename).suffix:
        basename += ".flac"
    matches = [name for name in archive_names if Path(name).name.lower() == basename]
    if len(matches) == 1:
        return matches[0]
    pack_text = str(pack or "").strip().replace("\\", "/").strip("/").lower()
    if pack_text:
        matches = [name for name in matches if f"/{pack_text}/" in f"/{name.lower()}"]
        if len(matches) == 1:
            return matches[0]
    return None


def row_to_sample(row):
    filename = first_value(row, ["take", "row"], ["filename", "file_name", "path", "file", "audio", "audio_path"])
    if filename is None:
        return None
    pack = first_value(row, ["pack", "take", "row"], ["name", "pack", "folder", "directory", "session"])
    instrument = first_value(row, ["sound", "take", "row"], ["instrument", "instrument_name", "source"]) or "unknown"
    klass = str(first_value(row, ["sound", "take", "row"], ["klass", "class", "tags"]) or "").lower()
    if "scale" in klass:
        return None
    midi = first_value(row, ["sound", "take", "row"], ["semitone", "midi", "midi_note", "pitch_id", "pitch"])
    midi_value = maybe_int(midi)
    if midi_value is None:
        note = first_value(row, ["sound", "take", "row"], ["note", "pitch_name"])
        octave = first_value(row, ["sound", "take", "row"], ["octave"])
        midi_value = midi_from_note(note, octave)
    if midi_value is None or midi_value < 21 or midi_value > 108:
        return None
    family = analyzer_family(instrument)
    low_high = {
        "bass": (28, 67),
        "guitar": (40, 88),
        "piano": (24, 95),
        "vocals": (40, 84),
        "other": (36, 84),
    }[family]
    if not (low_high[0] <= midi_value <= low_high[1]):
        return None
    row_id = first_value(row, ["take", "sound", "row"], ["id"]) or Path(str(filename)).stem
    dynamics = first_value(row, ["sound", "take", "row"], ["dynamics", "dynamic"]) or ""
    return {
        "id": f"good_sounds_{sanitize(instrument)}_{sanitize(row_id)}",
        "family": family,
        "nsynth_family": "good-sounds",
        "source": source_name(instrument),
        "midi": midi_value,
        "note": note_name_from_midi(midi_value),
        "filename": str(filename),
        "pack": str(pack or ""),
        "qualities": ",".join(part for part in [str(instrument), str(dynamics), FIXTURE_VERSION] if part),
    }


def manifest_complete(path, min_rows):
    if not path.is_file():
        return False
    root = path.parent
    rows = 0
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header[:7] != ["id", "family", "nsynth_family", "source", "midi", "note", "path"]:
            return False
        for line in file:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 7:
                return False
            if not (root / fields[6]).is_file():
                return False
            rows += 1
    return rows >= max(1, min_rows)


def convert_audio(ffmpeg, input_path, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    run([
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        "48000",
        "-f",
        "wav",
        str(temporary_path),
    ])
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


def prepare_rows(conn):
    rows = query_official_rows(conn)
    if not rows:
        rows = query_generic_rows(conn)
    samples = []
    skipped = 0
    for row in rows:
        sample = row_to_sample(row)
        if sample is None:
            skipped += 1
            continue
        samples.append(sample)
    samples.sort(key=lambda item: (item["family"], item["midi"], item["source"], item["pack"], item["filename"]))
    return samples, skipped


def limited_samples(samples, limit):
    if limit <= 0 or len(samples) <= limit:
        return samples
    buckets = {}
    for sample in samples:
        buckets.setdefault(sample["source"], []).append(sample)
    result = []
    source_names = sorted(buckets)
    while len(result) < limit:
        progressed = False
        for source in source_names:
            bucket = buckets[source]
            if not bucket:
                continue
            result.append(bucket.pop(0))
            progressed = True
            if len(result) >= limit:
                break
        if not progressed:
            break
    result.sort(key=lambda item: (item["family"], item["midi"], item["source"], item["pack"], item["filename"]))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare Good-sounds real single-note WAV fixtures.")
    parser.add_argument("--archive", default=os.environ.get(
        "GOOD_SOUNDS_ARCHIVE",
        "build/real_sample_sources/good_sounds/good-sounds.zip"))
    parser.add_argument("--output", default=os.environ.get("GOOD_SOUNDS_SAMPLE_DIR",
                                                           "build/good_sounds_samples"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("GOOD_SOUNDS_SAMPLE_LIMIT", "1000")))
    parser.add_argument("--min-samples", type=int, default=int(os.environ.get("GOOD_SOUNDS_MIN_SAMPLES", "500")))
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("GOOD_SOUNDS_REFRESH") == "1")
    args = parser.parse_args(argv)

    archive_path = Path(args.archive)
    output_dir = Path(args.output)
    manifest_path = output_dir / "manifest.tsv"
    if not args.refresh and manifest_complete(manifest_path, args.min_samples):
        print(f"prepare_good_sounds_samples: keeping existing {manifest_path}")
        return 0
    if not archive_path.is_file():
        raise SystemExit(f"prepare_good_sounds_samples: missing archive {archive_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    prepared = []
    skipped_missing_audio = 0
    with zipfile.ZipFile(archive_path) as archive, tempfile.TemporaryDirectory() as temp_name:
        database_member = find_database_member(archive)
        temp_dir = Path(temp_name)
        database_path = temp_dir / Path(database_member).name
        with archive.open(database_member) as source, database_path.open("wb") as target:
            shutil.copyfileobj(source, target)

        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        samples, skipped_rows = prepare_rows(conn)
        conn.close()
        archive_names, exact_names, folded_names = normalized_names(archive)

        samples = limited_samples(samples, args.limit)
        for sample in samples:
            member = find_audio_member(archive_names, exact_names, folded_names,
                                       sample["filename"], sample["pack"])
            if member is None:
                skipped_missing_audio += 1
                continue
            rel_path = f"{sample['family']}/{sample['source']}/{sanitize(sample['id'])}.wav"
            output_path = output_dir / rel_path
            if not output_path.is_file() or args.refresh:
                extracted = temp_dir / Path(member).name
                with archive.open(member) as source, extracted.open("wb") as target:
                    shutil.copyfileobj(source, target)
                convert_audio(args.ffmpeg, extracted, output_path)
            row = dict(sample)
            row["path"] = rel_path
            prepared.append(row)

    partial_path = output_dir / "manifest.tsv.partial"
    write_manifest(partial_path, prepared)
    counts = {}
    for row in prepared:
        counts[row["family"]] = counts.get(row["family"], 0) + 1
    count_text = " ".join(f"{name}={counts[name]}" for name in sorted(counts))
    if len(prepared) < args.min_samples:
        raise SystemExit(
            f"prepare_good_sounds_samples: prepared {len(prepared)} samples, below minimum "
            f"{args.min_samples} ({count_text}, skipped rows={skipped_rows}, missing audio={skipped_missing_audio})"
        )
    partial_path.replace(manifest_path)
    print(
        f"prepare_good_sounds_samples: wrote {len(prepared)} rows to {manifest_path} "
        f"({count_text}, skipped rows={skipped_rows}, missing audio={skipped_missing_audio})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
