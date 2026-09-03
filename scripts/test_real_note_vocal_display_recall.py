#!/usr/bin/env python3
"""Require high full-mix Vocal-row recall on the audited real-note fixtures."""

from pathlib import Path


MAX_EXPECTED_ROW_MISSES = 0


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    audit = root / "build" / "real_note_vocal_audit.out"
    if not audit.is_file():
        raise SystemExit("missing real-note vocal audit; run make audit-real-note-vocals first")

    misses = sum(
        " vocals/" in line and "expected-row ownership missing" in line
        for line in audit.read_text(encoding="utf-8").splitlines()
    )
    print(f"real-vocal expected-row misses {misses}, maximum {MAX_EXPECTED_ROW_MISSES}")
    if misses > MAX_EXPECTED_ROW_MISSES:
        raise SystemExit(f"expected at most {MAX_EXPECTED_ROW_MISSES} real-vocal expected-row misses, got {misses}")


if __name__ == "__main__":
    main()
