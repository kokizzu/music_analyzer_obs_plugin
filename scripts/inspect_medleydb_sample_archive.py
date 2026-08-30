#!/usr/bin/env python3
"""Inventory the downloaded MedleyDB sample archive without extracting it."""

from __future__ import annotations

import os
import tarfile
from pathlib import Path


CACHE_ROOT = Path(os.environ.get(
    "MUSIC_ANALYZER_FIXTURE_CACHE", "/media/kyz/sshflashtor/InstrumentSamples/build-cache"
))
ARCHIVE = CACHE_ROOT / "medleydb_sample" / "MedleyDB_Sample.tar.gz"


def main() -> int:
    if not ARCHIVE.is_file():
        print(f"missing-archive={ARCHIVE}")
        return 1
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        names = [member.name for member in archive.getmembers() if member.isfile()]
    metadata = [name for name in names if name.endswith("_METADATA.yaml")]
    pitch = [name for name in names if "/Pitch_Annotations/" in name]
    stems = [name for name in names if "_STEMS/" in name and name.endswith(".wav")]
    print(f"archive={ARCHIVE}")
    print(f"files={len(names)} metadata={len(metadata)} stems={len(stems)} pitch-annotations={len(pitch)}")
    for name in metadata:
        print(f"metadata={name}")
    for name in pitch[:24]:
        print(f"pitch={name}")
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        for name in metadata:
            if "/._" in name:
                continue
            content = archive.extractfile(name)
            if content is None:
                continue
            print(f"metadata-detail={name}")
            for line in content.read().decode("utf-8", errors="replace").splitlines():
                if any(key in line for key in ("component:", "filename:", "instrument:")):
                    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
