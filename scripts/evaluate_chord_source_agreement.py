#!/usr/bin/env python3
"""Screen current/raw/smoothed chord agreement with defining-tone support."""
import csv
import hashlib
import json
from pathlib import Path
from evaluate_next_detection import chord_score, chord_template

ROOT = Path(__file__).resolve().parents[1]


def main():
    base = ROOT / "build/accuracy_goal_chords/production-core-confirmation-1f2e4f1ede05"
    report, changes, inputs = {}, [], {}
    for corpus in ("MAPS", "MAESTRO"):
        path = base / (corpus + ".tsv")
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open() as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        context, pending, repeats = None, None, 0
        counts = dict(frames=len(rows), changes=0, gains=0, correct_losses=0, new_wrong=0)
        for row in rows:
            current_context = (row["recording"], row["anchor_sample"])
            if current_context != context:
                context, pending, repeats = current_context, None, 0
            native = row["global_chord"]
            candidate = row["keyboard_chord"]
            chroma = list(map(float, row["global_chroma"].split(",")))
            supported = (chord_template(candidate) is not None and candidate == row["keyboard_raw"] == row["keyboard_smoothed"] and
                         float(row["keyboard_raw_confidence"]) >= .85 and float(row["keyboard_smoothed_confidence"]) >= .85 and
                         float(row["confidence"]) < .7 and chord_score(candidate, chroma) >= .55 and
                         chord_score(candidate, chroma) - chord_score(native, chroma) >= .2)
            repeats = repeats + 1 if supported and pending == candidate else 1
            pending = candidate if supported else None
            selected = candidate if supported and repeats >= 2 else native
            truth = set(row["expected_chords"].split("/")) - {"", "--"}
            old, new = native.split("=")[0] in truth, selected.split("=")[0] in truth
            counts["changes"] += native != selected
            if truth:
                counts["gains"] += new and not old
                counts["correct_losses"] += old and not new
                counts["new_wrong"] += selected not in ("", "--") and not new and (old or native in ("", "--"))
            if native != selected:
                changes.append(dict(corpus=corpus, recording=row["recording"], anchor=row["anchor_sample"], frame=row["frame"],
                                    actual=native, selected=selected, expected=row["expected_chords"]))
        report[corpus] = counts
    result = dict(results=report, changes=changes, inputs=inputs,
                  decision="candidate" if any(row["gains"] for row in report.values()) and not any(row["correct_losses"] or row["new_wrong"] for row in report.values()) else "reject",
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="Causal two-frame raw/smoothed/current source agreement; historical calibration only; new recording holdout required before promotion")
    output = ROOT / "build/next_detection/chord_source_agreement.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
