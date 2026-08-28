#!/usr/bin/env python3
"""Summarize note annotations in the compact IDMT bass corpus."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ElementTree


ROOT = Path(__file__).resolve().parent.parent / "build/InstrumentSamples/idmt_smt_bass_single_track/source/annotation"


def main() -> int:
    files = sorted(ROOT.glob("*.xml"))
    if not files:
        print("no IDMT bass annotations found")
        return 1
    tags: Counter[str] = Counter()
    attributes: Counter[str] = Counter()
    examples: list[str] = []
    pitches: list[int] = []
    durations: list[float] = []
    strings: Counter[str] = Counter()
    excitations: Counter[str] = Counter()
    expressions: Counter[str] = Counter()
    for path in files:
        tree = ElementTree.parse(path)
        for element in tree.iter():
            tags[element.tag] += 1
            attributes.update(element.attrib)
            if element.tag != "event":
                continue
            values = {child.tag: (child.text or "").strip() for child in element}
            if len(examples) < 12:
                examples.append(f"{path.name}: {values}")
            try:
                pitches.append(int(values["pitch"]))
                durations.append(float(values["offsetSec"]) - float(values["onsetSec"]))
            except (KeyError, ValueError):
                pass
            strings[values.get("stringNumber", "unknown")] += 1
            excitations[values.get("excitationStyle", "unknown")] += 1
            expressions[values.get("expressionStyle", "unknown")] += 1
    print(f"files: {len(files)}")
    print("tags:")
    for tag, count in sorted(tags.items()):
        print(f"  {tag}: {count}")
    print("attributes:")
    for attribute, count in sorted(attributes.items()):
        print(f"  {attribute}: {count}")
    if pitches:
        print(f"midi pitch range: {min(pitches)}-{max(pitches)}")
    if durations:
        print(f"duration seconds: min={min(durations):.3f} median={sorted(durations)[len(durations) // 2]:.3f} max={max(durations):.3f}")
    print("strings:")
    for value, count in sorted(strings.items()):
        print(f"  {value}: {count}")
    print("excitation styles:")
    for value, count in sorted(excitations.items()):
        print(f"  {value}: {count}")
    print("expression styles:")
    for value, count in sorted(expressions.items()):
        print(f"  {value}: {count}")
    print("examples:")
    for example in examples:
        print(f"  {example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
