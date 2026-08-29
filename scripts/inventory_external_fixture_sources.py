#!/usr/bin/env python3
"""Inventory the external fixture store without modifying its contents."""

import os
from pathlib import Path


def main() -> int:
    root = Path("build/InstrumentSamples").resolve()
    if not root.is_dir():
        raise SystemExit(f"missing external fixture store: {root}")
    print(f"fixture_store={root}")
    for path, directories, files in os.walk(root):
        relative = Path(path).relative_to(root)
        depth = len(relative.parts)
        if depth > 2:
            directories[:] = []
            continue
        manifests = sorted(name for name in files if name in {"manifest.tsv", "README.md", "LICENSE"})
        audio_count = sum(name.lower().endswith((".wav", ".flac", ".mp3", ".ogg")) for name in files)
        if relative == Path(".") or manifests or audio_count:
            print(f"path={relative} audio_files={audio_count} manifests={','.join(manifests) or '--'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
