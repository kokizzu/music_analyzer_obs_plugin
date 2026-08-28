#!/usr/bin/env python3
"""Report the active GuitarSet miss-analysis process and fixture progress."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path("build/InstrumentSamples/guitarset")


def main() -> int:
    active: list[str] = []
    for proc in pathlib.Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if "analyze_guitarset" in command or "analyzer_guitarset" in command:
            active.append(f"pid={proc.name} {command}")
    print("active GuitarSet analysis:")
    print("\n".join(active) if active else "none")
    for path in (ROOT / "annotation.zip", ROOT / "audio_mono-mic.zip"):
        print(f"{path}: {path.stat().st_size if path.exists() else 0} bytes")
    print(f"extracted WAVs: {sum(1 for _ in ROOT.rglob('*.wav')) if ROOT.exists() else 0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
