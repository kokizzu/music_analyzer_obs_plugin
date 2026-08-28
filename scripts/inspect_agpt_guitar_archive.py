#!/usr/bin/env python3
"""Validate the published AG-PT audio/metadata contract without extraction."""

from __future__ import annotations

import argparse
import csv
import io
import zipfile


NOTE_COLUMNS = {
    "onset_label_seconds",
    "audio_file_path",
    "onset_label_samples",
    "expressive_technique_id",
    "pitch_midi",
    "string_number",
    "playing_intensity",
}


def find_member(names: set[str], suffix: str) -> str:
    matches = sorted(name for name in names if name.endswith(suffix))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {suffix}, found {matches}")
    return matches[0]


def read_rows(archive: zipfile.ZipFile, member: str) -> list[dict[str, str]]:
    with archive.open(member) as source:
        return list(csv.DictReader(io.TextIOWrapper(source, encoding="utf-8-sig", newline="")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()

    with zipfile.ZipFile(args.archive) as archive:
        members = [member.filename for member in archive.infolist() if not member.is_dir()]
        names = set(members)
        note_member = find_member(names, "/metadata/note_labels.csv")
        techniques_member = find_member(names, "/metadata/expressive_techniques.csv")
        files_member = find_member(names, "/metadata/files.csv")
        instruments_member = find_member(names, "/metadata/instruments.csv")
        audio_archive_member = find_member(names, "/data/audio.zip")
        notes = read_rows(archive, note_member)
        if not notes or not notes[0]:
            raise ValueError("note_labels.csv is empty")
        missing = sorted(NOTE_COLUMNS - set(notes[0]))
        if missing:
            raise ValueError(f"note_labels.csv missing columns: {', '.join(missing)}")
        techniques = read_rows(archive, techniques_member)
        files = read_rows(archive, files_member)
        instruments = read_rows(archive, instruments_member)
        if not techniques or not files or not instruments:
            raise ValueError("one or more AG-PT metadata tables are empty")
        if "filename" not in files[0]:
            raise ValueError("files.csv lacks filename")
        labelled_audio = {row["audio_file_path"] for row in notes if row.get("audio_file_path")}
        known_audio = {row["filename"] for row in files if row.get("filename")}
        unmatched = sorted(path for path in labelled_audio if path not in known_audio)
        if unmatched:
            raise ValueError(f"note labels reference missing audio (first): {unmatched[0]}")
        pitched_notes = sum(1 for row in notes if (row.get("pitch_midi") or "").strip())
        print(f"audio_archive_bytes={archive.getinfo(audio_archive_member).file_size}")
        print(f"audio_file_metadata={len(known_audio)}")
        print(f"note_labels={len(notes)}")
        print(f"pitch_labelled_notes={pitched_notes}")
        print(f"techniques={len(techniques)}")
        print(f"file_metadata={len(files)}")
        print(f"instruments={len(instruments)}")
        print("note_columns=" + ",".join(notes[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
