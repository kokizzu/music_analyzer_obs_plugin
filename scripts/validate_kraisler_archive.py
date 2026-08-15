#!/usr/bin/env python3
"""Validate the public KRAISLER archive before extracting it externally."""

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import PurePosixPath


def safe_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    return bool(normalized) and not path.is_absolute() and ".." not in path.parts and not path.drive


def archive_md5(path: str) -> str:
    digest = hashlib.md5()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def track_ids(members: list[str], pattern: str) -> set[str]:
    matcher = re.compile(pattern, re.IGNORECASE)
    return {match.group(1) for member in members if (match := matcher.search(member))}


def validate_archive(path: str, expected_md5: str, minimum_tracks: int) -> tuple[int, int]:
    digest = archive_md5(path)
    if expected_md5 and digest.lower() != expected_md5.lower():
        raise ValueError(f"MD5 mismatch: got {digest}, expected {expected_md5}")
    with zipfile.ZipFile(path) as archive:
        members = []
        for member in archive.infolist():
            if not safe_member(member.filename):
                raise ValueError(f"unsafe archive member: {member.filename}")
            if not member.is_dir():
                members.append(member.filename)
    if not members:
        raise ValueError("archive has no files")
    piano_wav = track_ids(members, r"(?:^|/)(\d{2})_PF_(?:dry|studio|hall)\.wav$")
    violin_wav = track_ids(members, r"(?:^|/)(\d{2})_VN_(?:dry|studio|hall)\.wav$")
    mix_wav = track_ids(members, r"(?:^|/)(\d{2})_mix_(?:dry|studio|hall)\.wav$")
    piano_midi = track_ids(members, r"(?:^|/)(\d{2})_PF\.mid$")
    violin_notes = track_ids(members, r"(?:^|/)(\d{2})_notes_VN\.csv$")
    complete = piano_wav & violin_wav & mix_wav & piano_midi & violin_notes
    if len(complete) < minimum_tracks:
        raise ValueError(
            "missing complete KRAISLER track sets: "
            f"found {len(complete)}, expected at least {minimum_tracks} "
            "with piano/violin/mix WAV, piano MIDI, and violin notes"
        )
    return len(members), len(complete)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--expected-md5", default="")
    parser.add_argument("--minimum-tracks", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        files, complete = validate_archive(args.archive, args.expected_md5, args.minimum_tracks)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"validate_kraisler_archive: {exc}", file=sys.stderr)
        return 1
    print(f"validate_kraisler_archive: valid files={files} complete_tracks={complete} archive={args.archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
