#!/usr/bin/env python3
"""Inspect MIR-1K audio and manual pitch-label layout before curation."""

from pathlib import Path
import subprocess
import shutil


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "build/mir1k_vocal_fixtures/source"
ARCHIVE = ROOT / "build/mir1k_vocal_fixtures/MIR-1K.rar"


def main() -> int:
    disk = shutil.disk_usage(ROOT)
    print(f"workspace free bytes: {disk.free}")
    files = [path for path in SOURCE.rglob("*") if path.is_file()]
    wavs = sorted(path for path in files if path.suffix.lower() == ".wav")
    pitches = sorted(path for path in files if path.suffix.lower() == ".pv")
    print("top-level entries:")
    for path in sorted(SOURCE.iterdir()):
        print(path.name)
    suffixes: dict[str, int] = {}
    for path in files:
        suffixes[path.suffix.lower() or "<none>"] = suffixes.get(path.suffix.lower() or "<none>", 0) + 1
    print("file suffixes: " + ", ".join(f"{suffix}={count}" for suffix, count in sorted(suffixes.items())))
    print(f"WAV count: {len(wavs)}")
    print(f"pitch count: {len(pitches)}")
    for path in wavs[:8]:
        print(f"wav {path.relative_to(SOURCE)} bytes={path.stat().st_size}")
    for path in pitches[:8]:
        print(f"pitch {path.relative_to(SOURCE)}")
    for path in sorted(files)[:16]:
        print(f"file {path.relative_to(SOURCE)}")
    if pitches:
        print("first pitch rows:")
        for line in pitches[0].read_text(encoding="utf-8", errors="replace").splitlines()[:12]:
            print(line)
    listing = subprocess.run(["7z", "l", str(ARCHIVE)], check=True, text=True,
                             capture_output=True).stdout.splitlines()
    print("archive audio entries:")
    count = 0
    for line in listing:
        lower = line.lower()
        if ".wav" in lower or "pitch" in lower:
            print(line)
            count += 1
            if count >= 20:
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
