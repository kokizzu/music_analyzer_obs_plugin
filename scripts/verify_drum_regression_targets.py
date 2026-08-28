#!/usr/bin/env python3
"""Verify the fixed drum regression targets are present in the Makefile."""

from pathlib import Path


TARGETS = (
    "test-drum-samples-spread",
    "test-mdb-drums-samples-parallel",
    "test-star-drums-samples-parallel",
)


def main() -> None:
    lines = Path("Makefile").read_text(encoding="utf-8").splitlines()
    declared = {line.split(":", 1)[0] for line in lines if ":" in line and not line.startswith("\t")}
    missing = [target for target in TARGETS if target not in declared]
    if missing:
        raise SystemExit("missing targets: " + ", ".join(missing))
    print("verified targets: " + ", ".join(TARGETS))


if __name__ == "__main__":
    main()
