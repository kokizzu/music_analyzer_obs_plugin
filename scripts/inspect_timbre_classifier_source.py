#!/usr/bin/env python3
"""Print the classifier report's fixture and score extraction paths."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
def main() -> None:
    path = ROOT / "scripts" / "report_timbre_classifier.py"
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        print(f"{number}: {line}")


if __name__ == "__main__":
    main()
