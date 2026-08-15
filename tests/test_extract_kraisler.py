#!/usr/bin/env python3
import hashlib
import importlib.util
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("extract_kraisler", ROOT / "scripts" / "extract_kraisler.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_archive(path: Path) -> str:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("KRAISLER/performance_wav/01_PF_dry.wav", b"piano")
        archive.writestr("KRAISLER/performance_wav/01_VN_dry.wav", b"violin")
        archive.writestr("KRAISLER/performance_wav/01_mix_dry.wav", b"mix")
        archive.writestr("KRAISLER/performance_midi/01_PF.mid", b"MThd")
        archive.writestr("KRAISLER/annotation_csv/01_notes_VN.csv", b"onset,offset,midi\n0,1,60\n")
    return hashlib.md5(path.read_bytes()).hexdigest()


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        archive = root / "source.zip"
        digest = write_archive(archive)
        output = root / "extracted"
        assert MODULE.extract(archive, output, digest, 1) == 5
        assert (output / "KRAISLER/performance_wav/01_mix_dry.wav").is_file()
        assert MODULE.extract(archive, output, digest, 1) == 5
        (output / "KRAISLER/performance_wav/01_VN_dry.wav").unlink()
        try:
            MODULE.extract(archive, output, digest, 1)
        except ValueError as exc:
            assert "incomplete extraction" in str(exc)
        else:
            raise AssertionError("incomplete output was replaced")
    print("test_extract_kraisler: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
