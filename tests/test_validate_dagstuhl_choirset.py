#!/usr/bin/env python3
import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import validate_dagstuhl_choirset as validator


def write_archive(path: Path, member: str) -> str:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, "fixture")
    return hashlib.md5(path.read_bytes()).hexdigest()


def test_accepts_a_safe_archive_with_matching_digest():
    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / "dcs.zip"
        digest = write_archive(archive, "DagstuhlChoirSet/audio/piece.wav")
        if validator.main(["--archive", str(archive), "--expected-md5", digest]) != 0:
            raise AssertionError("safe archive should validate")


def test_rejects_a_digest_mismatch():
    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / "dcs.zip"
        write_archive(archive, "DagstuhlChoirSet/audio/piece.wav")
        if validator.main(["--archive", str(archive), "--expected-md5", "0" * 32]) == 0:
            raise AssertionError("digest mismatch should fail")


def test_rejects_a_traversal_member():
    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / "dcs.zip"
        digest = write_archive(archive, "../escape.wav")
        if validator.main(["--archive", str(archive), "--expected-md5", digest]) == 0:
            raise AssertionError("unsafe archive member should fail")


def main():
    test_accepts_a_safe_archive_with_matching_digest()
    test_rejects_a_digest_mismatch()
    test_rejects_a_traversal_member()
    print("test_validate_dagstuhl_choirset: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
