#!/usr/bin/env python3
"""Provision URMP multitrack fixtures outside Git and expose them by symlink."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = Path("/media/kyz/sshflashtor/InstrumentSamples/build-cache")
DATASET_ROOT = CACHE_ROOT / "urmp_multitrack_samples"
DATA_ROOT = DATASET_ROOT / "data" / "urmp"
LINK = ROOT / "build" / "urmp_multitrack_samples"
REPOSITORY = "J1mmymm/MIMuT_Data_v2"
PATTERN = "data/urmp/**"


def print_plan() -> None:
    print("dataset=URMP multitrack real-instrument corpus")
    print(f"repository={REPOSITORY}")
    print(f"include={PATTERN}")
    print(f"external-cache={DATASET_ROOT}")
    print(f"audio-root={DATA_ROOT}")
    print(f"repository-link={LINK}")
    print("storage=external-only; Git stores neither audio nor annotations")


def install_link() -> None:
    if not DATA_ROOT.is_dir():
        raise SystemExit(f"download did not create expected URMP directory: {DATA_ROOT}")
    LINK.parent.mkdir(parents=True, exist_ok=True)
    temporary = LINK.with_name(f".{LINK.name}.tmp")
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(DATA_ROOT)
    os.replace(temporary, LINK)


def apply() -> None:
    DATASET_ROOT.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "hf", "download", REPOSITORY,
        "--repo-type", "dataset",
        "--include", PATTERN,
        "--local-dir", str(DATASET_ROOT),
    ], check=True)
    install_link()
    print_plan()
    print("status=ready")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
        raise SystemExit("usage: prepare_urmp_multitrack_fixtures.py plan|apply")
    if sys.argv[1] == "plan":
        print_plan()
    else:
        apply()


if __name__ == "__main__":
    main()
