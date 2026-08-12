#!/usr/bin/env python3

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_pitch_shifted_violin_samples as fixture


def row(identifier, midi, source="violin", family="other"):
    return {
        "id": identifier,
        "family": family,
        "nsynth_family": "strings",
        "source": source,
        "midi": str(midi),
        "note": fixture.midi_note(midi),
        "path": f"audio/{identifier}.wav",
        "qualities": "forte,arco-normal",
    }


def main():
    source = []
    for midi in range(55, 60):
        source.extend(row(f"violin_{midi}_{index}", midi) for index in range(4))
    source.append(row("cello_55", 55, source="cello"))
    selected = fixture.select_rows(source, 4)
    if len(selected) != 20 or {int(item["midi"]) for item in selected} != set(range(55, 60)):
        raise AssertionError(f"unexpected selected rows: {selected}")
    derived = fixture.output_row(selected[0])
    if derived["midi"] != "43" or derived["note"] != "G2":
        raise AssertionError(f"wrong octave-down label: {derived}")
    if derived["source"] != "violin-pitch-shifted-octave-down":
        raise AssertionError(f"missing explicit provenance: {derived}")
    if "source-midi-55" not in derived["qualities"]:
        raise AssertionError(f"missing source MIDI provenance: {derived}")
    print("prepare_pitch_shifted_violin_samples tests passed")


if __name__ == "__main__":
    main()
