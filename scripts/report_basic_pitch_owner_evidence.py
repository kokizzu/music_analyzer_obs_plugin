#!/usr/bin/env python3
"""Report Basic Pitch owner-evidence workers and their persisted measurements."""

from __future__ import annotations

from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
KEYWORDS = ("basic_pitch_onnx_musicnet", "basic_pitch_owner_evidence")
TEXT_SUFFIXES = {".out", ".txt", ".tsv", ".csv", ".json", ".log"}


def process_matches() -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            command = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if any(keyword in command for keyword in KEYWORDS):
            matches.append((entry.name, command))
    return matches


def evidence_files() -> list[Path]:
    if not BUILD.exists():
        return []
    files = [
        path for path in BUILD.rglob("*")
        if path.is_file() and path.suffix in TEXT_SUFFIXES and "basic_pitch" in path.name.lower()
    ]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def main() -> int:
    workers = process_matches()
    print(f"active_basic_pitch_owner_evidence_workers={len(workers)}")
    for pid, command in workers:
        print(f"pid={pid} command={command}")

    files = evidence_files()
    print(f"persisted_basic_pitch_evidence_files={len(files)}")
    for path in files[:12]:
        relative = path.relative_to(ROOT)
        print(f"file={relative} bytes={path.stat().st_size}")
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as error:
            print(f"read_error={error}")
            continue
        for line in lines[-12:]:
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
