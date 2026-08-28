#!/usr/bin/env python3
"""Show the real-note Make target and files it uses or writes."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def print_target(path: Path, target: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith(f"{target}:"):
            for line_no in range(index, min(index + 12, len(lines))):
                print(f"{line_no + 1}: {lines[line_no]}")
            return
    print(f"target not found: {target}")


def main() -> int:
    makefile = ROOT / "Makefile"
    for target in (
        "test-real-note-samples",
        "analyze-real-note-misses",
        "analyze-real-note-attributes",
        "analyze-guitarset-misses",
        "summarize-latest-guitarset-miss-run",
        "inspect-guitar-primary-promotion",
        "inspect-guitar-octave-shadow",
        "analyze-guitarset-attributes",
        "status-real-note-full-mix",
        "summarize-real-note-full-mix-attributes",
        "analyze-real-note-guitar-ownership",
        "analyze-real-note-piano-guitar-routes",
        "inspect-full-mix-ownership-classifier",
        "evaluate-owner-classifier-loco",
        "evaluate-owner-classifier-quality-loco",
        "audit-owner-classifier-quality-margin",
        "inspect-full-mix-ownership-application",
        "inspect-note-owner-classifier",
        "inspect-shared-ownership-ranking",
        "inspect-analyzer-cases-main",
        "test-analyzer-cases",
        "report-analyzer-cases-process",
        "summarize-analyzer-cases-log",
    "test-ambiguous-display-recovery",
    "test-high-soprano-vocal-mirror",
    "summarize-high-soprano-vocal-mirror-result",
    "stage-high-soprano-vocal-mirror",
    "commit-high-soprano-vocal-mirror",
        "plan-stage-ambiguous-display-recovery",
        "summarize-mir1k-vocal-attributes",
    "evaluate-mir1k-vocal-recovery-rules",
    "inspect-mir1k-vocal-fixture-pipeline",
    "test-mir1k-vocal-full-mix",
    "stage-mir1k-vocal-fixture-gate",
    "commit-mir1k-vocal-fixture-gate",
    "test-mir1k-vocal-full-mix-baseline",
    "collect-mir1k-vocal-full-mix-attributes",
    "summarize-mir1k-vocal-ownership",
        "compare-mir1k-vocal-feature-distributions",
        "inspect-full-mix-vocal-scoring",
        "inspect-full-mix-vocal-profile",
        "inspect-real-note-vocal-routes",
    ):
        print_target(makefile, target)
    for name in (
        "real_note_verbose.out",
        "real_note_verbose.err",
        "real_note_attributes.tsv",
        "real_note_misses.tsv",
    ):
        path = ROOT / "build" / name
        if path.exists():
            print(f"result: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
