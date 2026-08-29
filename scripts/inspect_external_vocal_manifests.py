#!/usr/bin/env python3
"""Inspect available external vocal fixture manifests for pitch-label fields."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE = (ROOT / "build" / "InstrumentSamples").resolve()
CANDIDATES = (
    "vocalset_samples/manifest.tsv",
    "vocadito_samples/manifest.tsv",
    "vocals_samples/manifest.tsv",
    "build-cache/vocalset_samples/manifest.tsv",
    "build-cache/vocadito_samples/manifest.tsv",
)


def main() -> int:
    print(f"fixture_store={STORE}")
    for relative in CANDIDATES:
        manifest = STORE / relative
        if not manifest.is_file():
            print(f"missing={relative}")
            continue
        lines = manifest.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"manifest={relative} rows={max(0, len(lines) - 1)}")
        for line in lines[:4]:
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
