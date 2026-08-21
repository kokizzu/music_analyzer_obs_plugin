#!/usr/bin/env python3
"""Extract the isolated Pixabay/Freesound Rimshot outcome from the harness log."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


ACTIVE_RE = re.compile(r"^  expected rim\s+.*?\bsnare=(?P<snare>\d+).*?\brim=(?P<rim>\d+)$", re.MULTILINE)
PRIMARY_RE = re.compile(r"^  expected rim\s+.*?\bsnare=(?P<snare>\d+).*?\brim=(?P<rim>\d+)\s+ambiguous=(?P<ambiguous>\d+)\s+none=(?P<none>\d+)$", re.MULTILINE)


def render(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    active = ACTIVE_RE.search(text)
    primary = PRIMARY_RE.search(text)
    if active is None or primary is None:
        raise ValueError(f"{path}: missing isolated Rimshot matrices")
    detected = int(active["rim"])
    snare_primary = int(primary["snare"])
    rim_primary = int(primary["rim"])
    total = rim_primary + snare_primary + int(primary["ambiguous"]) + int(primary["none"])
    if total != 1 or detected not in {0, 1}:
        raise ValueError(f"{path}: invalid isolated Rimshot counts")
    return [
        "pixabay_rimshot_measurement: "
        f"detected={detected}/1 primary={rim_primary}/1 snare_primary={snare_primary}/1",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        rendered = "\n".join(render(args.input)) + "\n"
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"pixabay_rimshot_measurement: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
