#!/usr/bin/env python3
"""Find local Windows signing certificate files without printing secrets."""

from __future__ import annotations

import os
from pathlib import Path


SEARCH_ROOTS = (
    Path.home() / "Downloads",
    Path.home() / "Documents",
    Path.home() / ".config",
    Path.home() / ".local" / "share",
    Path("/home/kyz/go/src/music_analyzer_obs_plugin"),
    Path("/media/kyz/aigenshared"),
    Path("/tmp"),
)
SUFFIXES = {".pfx", ".p12", ".pem", ".cer", ".crt"}
SKIP_NAMES = {".cache", ".git", "node_modules", "build"}
MAX_DEPTH = 4


def candidate_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    found: list[Path] = []
    root_depth = len(root.parts)
    for directory, names, files in os.walk(root):
        names[:] = [name for name in names if name not in SKIP_NAMES]
        if len(Path(directory).parts) - root_depth >= MAX_DEPTH:
            names[:] = []
        for name in files:
            path = Path(directory) / name
            if path.suffix.lower() in SUFFIXES:
                found.append(path)
    return found


def main() -> None:
    for variable in ("WINDOWS_SIGN_PFX", "WINDOWS_SIGN_CERT", "WINDOWS_SIGN_PASSWORD"):
        value = os.environ.get(variable, "")
        print(f"{variable}: {'set' if value else 'unset'}")
        if value and variable != "WINDOWS_SIGN_PASSWORD":
            print(f"{variable}_PATH={Path(value).expanduser()}")

    seen: set[Path] = set()
    candidates: list[Path] = []
    for root in SEARCH_ROOTS:
        for path in candidate_files(root):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                candidates.append(resolved)
    for path in sorted(candidates):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        print(f"certificate_candidate={path} bytes={size}")
    if not candidates:
        print("certificate_candidates=none")


if __name__ == "__main__":
    main()
