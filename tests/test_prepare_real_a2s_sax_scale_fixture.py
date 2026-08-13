#!/usr/bin/env python3
"""Unit checks for Real A2S **kern timing and pitch parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fixture", ROOT / "scripts" / "prepare_real_a2s_sax_scale_fixture.py")
assert SPEC and SPEC.loader
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)


def main() -> int:
    assert fixture.parse_kern_token("8fL") == (0.5, 65)
    assert fixture.parse_kern_token("8bb-J") == (0.5, 82)
    assert fixture.parse_kern_token("8B-L") == (0.5, 58)
    assert fixture.parse_kern_token("2f") == (2.0, 65)
    assert fixture.note_name(51) == "D#3"
    print("prepare_real_a2s_sax_scale_fixture tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
