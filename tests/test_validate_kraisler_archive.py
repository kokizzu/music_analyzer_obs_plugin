#!/usr/bin/env python3
import hashlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_kraisler_archive.py"


def write_archive(path: Path, unsafe: bool = False) -> None:
    prefix = "../" if unsafe else "KRAISLER/"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"{prefix}performance_wav/01_PF_dry.wav", b"piano")
        archive.writestr(f"{prefix}performance_wav/01_VN_dry.wav", b"violin")
        archive.writestr(f"{prefix}performance_wav/01_mix_dry.wav", b"mix")
        archive.writestr(f"{prefix}performance_midi/01_PF.mid", b"MThd")
        archive.writestr(f"{prefix}annotation_csv/01_notes_VN.csv", b"onset,offset,midi\n0,1,60\n")


def run(path: Path, digest: str, expect: int) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--archive", str(path), "--expected-md5", digest, "--minimum-tracks", "1"],
        text=True,
        capture_output=True,
    )
    assert result.returncode == expect, result.stderr
    return result.stdout + result.stderr


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "kraisler.zip"
        write_archive(archive)
        digest = hashlib.md5(archive.read_bytes()).hexdigest()
        assert "complete_tracks=1" in run(archive, digest, 0)
        assert "MD5 mismatch" in run(archive, "0" * 32, 1)
        unsafe = root / "unsafe.zip"
        write_archive(unsafe, unsafe=True)
        digest = hashlib.md5(unsafe.read_bytes()).hexdigest()
        assert "unsafe archive member" in run(unsafe, digest, 1)
    print("test_validate_kraisler_archive: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
