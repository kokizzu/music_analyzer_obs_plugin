#!/usr/bin/env python3
"""Regression test for parentheses in source/device labels."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "visualizer_renderer.cpp"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    expected = {
        "'(':": ("00100", "01000", "10000", "10000", "10000", "01000", "00100"),
        "')':": ("00100", "00010", "00001", "00001", "00001", "00010", "00100"),
    }
    for case, rows in expected.items():
        result = "{" + ", ".join(f'"{row}"' for row in rows) + "};"
        marker = f"case {case}\n\t\treturn {result}"
        if marker not in text:
            raise SystemExit(f"missing bitmap glyph for {case}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
