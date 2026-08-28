#!/usr/bin/env python3
"""Print annotated MDB hi-hat window records and their trigger evidence."""

from pathlib import Path
import re


EXPECTED_RE = re.compile(r"expected ([^:]+):")
HIHAT_LEVEL_RE = re.compile(r"HIHAT=([0-9.]+)(\*)?")
HIHAT_EVIDENCE_RE = re.compile(
    r"HIHAT band=([0-9.]+) seg=([0-9.]+) shape=[0-9.]+ trig=([0-9.]+)/([0-9.]+)"
)


def main() -> None:
    path = Path("build/mdb_drums_windows.log")
    if not path.exists():
        raise SystemExit(f"Missing {path}; run analyze-mdb-drum-windows first.")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    expected_hats = []
    active_hats = []
    for line in lines:
        expected_match = EXPECTED_RE.search(line)
        level_match = HIHAT_LEVEL_RE.search(line)
        evidence_match = HIHAT_EVIDENCE_RE.search(line)
        if not expected_match or not level_match or not evidence_match:
            continue
        expected = {item.strip().lower() for item in expected_match.group(1).split(",")}
        if "hihat" not in expected:
            continue
        level, active = level_match.groups()
        band, segment, score, threshold = evidence_match.groups()
        row = {
            "level": float(level),
            "active": active == "*",
            "band": float(band),
            "segment": float(segment),
            "ratio": float(score) / float(threshold),
            "line": line,
        }
        expected_hats.append(row)
        if row["active"]:
            active_hats.append(row)
    print(f"annotated_hihat_windows={len(expected_hats)} active={len(active_hats)}")
    if active_hats:
        weakest = min(active_hats, key=lambda row: row["band"])
        print(
            "active_min_band="
            f"{weakest['band']:.6f} level={weakest['level']:.2f} ratio={weakest['ratio']:.3f}"
        )
        print(weakest["line"])
    for row in sorted(expected_hats, key=lambda item: item["band"])[:10]:
        print(
            f"band={row['band']:.6f} active={int(row['active'])} level={row['level']:.2f} "
            f"ratio={row['ratio']:.3f} {row['line'].split(' levels ', 1)[0]}"
        )


if __name__ == "__main__":
    main()
