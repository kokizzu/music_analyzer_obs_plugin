#!/usr/bin/env python3
"""Unit checks for annotated URMP saxophone fixture selection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fixture", ROOT / "scripts" / "prepare_urmp_sax_exact_fixture.py"
)
assert SPEC and SPEC.loader
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)


def main() -> int:
    assert fixture.midi_from_frequency(440.0) == 69
    assert fixture.midi_from_frequency(233.082) == 58
    assert fixture.note_name(51) == "D#3"
    first_stem = Path("piece") / "Notes_01_sax_alto.txt"
    second_stem = Path("piece") / "Notes_01_sax_tenor.txt"
    assert fixture.probe_id(first_stem, 0) != fixture.probe_id(second_stem, 0)
    events = [(float(index), 40 + index, 0.20) for index in range(6)]
    assert fixture.spread(events, 3) == [events[0], events[2], events[5]]
    assert fixture.spread(events, 1) == [events[3]]
    with tempfile.TemporaryDirectory() as temporary:
        notes = Path(temporary) / "Notes_2_sax_demo.txt"
        notes.write_text("0.0 440.0 0.20\n1.0 0.0 0.20\n2.0 233.082 0.10\n", encoding="utf-8")
        assert fixture.note_events(notes, 0.14) == [(0.0, 69, 0.20)]
    print("prepare_urmp_sax_exact_fixture tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
