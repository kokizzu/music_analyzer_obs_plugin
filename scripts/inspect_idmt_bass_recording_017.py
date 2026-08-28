#!/usr/bin/env python3
"""Print global and note annotation values for the anomalous IDMT recording 017."""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ElementTree


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "build/InstrumentSamples/idmt_smt_bass_single_track/source/annotation/017.xml"


def main() -> int:
    root = ElementTree.parse(SOURCE).getroot()
    for child in root:
        if child.tag == "transcription":
            continue
        print(f"{child.tag}: {(child.text or '').strip()}")
    for index, event in enumerate(root.iter("event"), start=1):
        values = {child.tag: (child.text or "").strip() for child in event}
        if index > 12:
            break
        print(f"event {index}: {values}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
