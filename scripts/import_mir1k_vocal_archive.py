#!/usr/bin/env python3
"""Download and extract MIR-1K for local, non-committed vocal fixture curation."""

from pathlib import Path
import shutil
import subprocess
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build/mir1k_vocal_fixtures"
ARCHIVE = OUTPUT / "MIR-1K.rar"
EXTRACTED = OUTPUT / "source"
URL = "https://ndownloader.figshare.com/files/10256751"


def download() -> None:
    if ARCHIVE.is_file() and ARCHIVE.stat().st_size > 100_000_000:
        print(f"using cached archive: {ARCHIVE}")
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    temporary = ARCHIVE.with_suffix(".rar.partial")
    if temporary.exists():
        temporary.unlink()
    print(f"downloading MIR-1K to {ARCHIVE}")
    request = urllib.request.Request(URL, headers={"User-Agent": "music-analyzer-fixture-import/1.0"})
    with urllib.request.urlopen(request) as response, temporary.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
    if not temporary.is_file() or temporary.stat().st_size < 100_000_000:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("MIR-1K download was incomplete or blocked")
    temporary.replace(ARCHIVE)


def extract() -> None:
    if (EXTRACTED / ".complete").is_file():
        print(f"using extracted archive: {EXTRACTED}")
        return
    extractor = shutil.which("unrar") or shutil.which("7z")
    if not extractor:
        raise RuntimeError("7z or unrar is required to extract MIR-1K.rar")
    if EXTRACTED.exists():
        # An interrupted RAR extraction can leave zero-byte files that 7z will
        # otherwise preserve on retry. This directory is generated solely by
        # this importer, so replacing an incomplete tree is deterministic.
        shutil.rmtree(EXTRACTED)
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    if Path(extractor).name == "7z":
        command = [extractor, "x", "-y", "-aoa", f"-o{EXTRACTED}", str(ARCHIVE)]
    else:
        command = [extractor, "x", "-o+", str(ARCHIVE), str(EXTRACTED)]
    subprocess.run(command, cwd=ROOT, check=True)
    (EXTRACTED / ".complete").touch()


def catalog() -> None:
    wavs = sorted(EXTRACTED.rglob("*.wav"))
    pitches = sorted(EXTRACTED.rglob("*.pv"))
    print(f"extracted WAV files: {len(wavs)}")
    print(f"extracted pitch files: {len(pitches)}")
    for path in wavs[:5]:
        print(f"wav: {path.relative_to(ROOT)}")
    for path in pitches[:5]:
        print(f"pitch: {path.relative_to(ROOT)}")


def main() -> int:
    download()
    extract()
    catalog()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
