#!/usr/bin/env python3
"""Summarize strict Beat This! sidecar replay logs without inferring readiness."""
from __future__ import annotations

import argparse
from pathlib import Path
import re


ROW_RE = re.compile(r"^Beat This sidecar replay\t(?P<fields>.+)$", re.MULTILINE)
STATUSES = {"hit", "miss", "withheld", "unavailable"}


def rows(path: Path) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for match in ROW_RE.finditer(path.read_text(encoding="utf-8", errors="replace")):
        fields = dict(part.split("=", 1) for part in match["fields"].split("\t") if "=" in part)
        if fields.get("status") not in STATUSES or fields.get("packet_seconds") != "20":
            raise ValueError(f"{path}: malformed strict sidecar replay row")
        try:
            int(fields["id"])
            int(fields["intervals"])
            float(fields["wall_seconds"])
        except (KeyError, ValueError) as error:
            raise ValueError(f"{path}: invalid strict sidecar replay row") from error
        result.append(fields)
    if not result:
        raise ValueError(f"{path}: no strict sidecar replay rows")
    return result


def render(paths: list[Path]) -> str:
    all_rows = [row for path in paths for row in rows(path)]
    identifiers = [row["id"] for row in all_rows]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("strict sidecar replay inputs contain duplicate row ids")
    counts = {status: sum(row["status"] == status for row in all_rows) for status in STATUSES}
    maximum = max(float(row["wall_seconds"]) for row in all_rows)
    return (
        "beat_this_sidecar_replay: "
        f"rows={len(all_rows)} ready={counts['hit'] + counts['miss']} correct={counts['hit']} "
        f"wrong={counts['miss']} withheld={counts['withheld']} unavailable={counts['unavailable']} "
        f"max_wall_seconds={maximum:.3f}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        rendered = render(args.inputs)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"beat_this_sidecar_replay: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
