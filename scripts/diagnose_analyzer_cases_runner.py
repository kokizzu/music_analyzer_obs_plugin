#!/usr/bin/env python3
"""Show the established analyzer-cases runner build configuration."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for relative in ("scripts/run_analyzer_cases_logged.py", "scripts/run_with_duration.sh"):
    path = ROOT / relative
    print(f"--- {relative} ---")
    print(path.read_text(encoding="utf-8"))

makefile = (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
for target in ("$(BUILD_DIR)/analyzer_cases:", "test-analyzer-cases:"):
    for index, line in enumerate(makefile):
        if line.startswith(target):
            print(f"--- Makefile:{target} ---")
            for target_line in makefile[index:index + 10]:
                print(target_line)
            break
