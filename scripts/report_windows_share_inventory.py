#!/usr/bin/env python3
"""Report the mounted Windows package without changing the share."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path


MOUNTPOINT = Path("/media/kyz/aigenshared")
ARTIFACTS = (
    "MusicAnalyzer.exe",
    "HalfMusicAnalyzer.exe",
    "SDL2.dll",
    "build-provenance.json",
    "verification.json",
)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    print(f"share={MOUNTPOINT}")
    print(f"mounted={os.path.ismount(MOUNTPOINT)}")
    if not MOUNTPOINT.is_dir():
        print("status=unavailable")
        return 1

    for name in ARTIFACTS:
        path = MOUNTPOINT / name
        if not path.is_file():
            print(f"{name}: absent")
            continue
        stat = path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
        print(f"{name}: bytes={stat.st_size} sha256={digest(path)} modified={modified}")

    provenance = MOUNTPOINT / "build-provenance.json"
    if provenance.is_file():
        try:
            values = json.loads(provenance.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print(f"provenance: invalid ({error})")
        else:
            print(f"provenance.commit={values.get('commit', '(missing)')}")
            print(f"provenance.working_tree_modified={values.get('working_tree_modified', '(missing)')}")
            print(f"provenance.physical_windows_audio_tested={values.get('physical_windows_audio_tested', '(missing)')}")

    changelogs = sorted(MOUNTPOINT.glob("changelog-*.txt"))
    if changelogs:
        latest = changelogs[-1]
        print(f"latest_changelog={latest.name}")
        lines = latest.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[:8]:
            print(f"changelog: {line}")
    else:
        print("latest_changelog=absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
