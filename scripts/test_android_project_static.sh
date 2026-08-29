#!/usr/bin/env bash
# Run the Android source-level regression checks without requiring an emulator.
set -euo pipefail

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"
python3 tests/check_android_project.py
