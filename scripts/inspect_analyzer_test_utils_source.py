#!/usr/bin/env python3
"""Show the test buffer and production analysis-window definitions."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "tests" / "analyzer_test_utils.hpp",
    ROOT / "src" / "analyzer.hpp",
)


def main() -> None:
    for source in SOURCES:
        print(f"[{source.relative_to(ROOT)}]")
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
            if "kAnalysisWindow" in line or "kDefaultAnalysisWindowMs" in line or "using Buffer" in line:
                print(f"{number}: {line}")


if __name__ == "__main__":
    main()
