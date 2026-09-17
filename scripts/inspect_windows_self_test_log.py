#!/usr/bin/env python3
"""Print the recorded Wine self-test logs for the current Windows build."""

from pathlib import Path


build = Path(__file__).resolve().parents[1] / "build" / "windows-x64"
for name in ("MusicAnalyzer", "HalfMusicAnalyzer"):
    path = build / f"{name}-self-test.log"
    print(f"[{path}]")
    if path.exists():
        print(path.read_text(encoding="utf-8", errors="replace"))
    else:
        print("missing")
