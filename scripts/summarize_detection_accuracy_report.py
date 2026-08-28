#!/usr/bin/env python3
"""Print the result sections and failure-oriented lines from the accuracy report."""

from pathlib import Path


REPORT = Path("docs/detection_accuracy_report.md")
KEYWORDS = (
    "failure",
    "miss",
    "recall",
    "precision",
    "coverage",
    "skipped",
    "error",
    "remaining",
)


def main() -> None:
    if not REPORT.exists():
        raise SystemExit(f"missing {REPORT}; run make update-detection-accuracy-report-cached first")
    active_heading = ""
    emitted = 0
    for line in REPORT.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("##"):
            active_heading = line
            continue
        if not active_heading or not any(word in line.lower() for word in KEYWORDS):
            continue
        print(active_heading)
        print(line)
        emitted += 1
    print(f"summary_lines={emitted} report={REPORT}")


if __name__ == "__main__":
    main()
