#!/usr/bin/env python3
"""Learn a narrowly gated Voice-bleed veto; preserve singer-disjoint positives."""
import csv
import hashlib
import json
import math
from pathlib import Path

from audit_keyboard_voice_separation import supported_keyboard
from evaluate_next_detection import fit_forest

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["onset", "decay", "pitch_stability", "simultaneous_onset", "pitch", "periodicity",
            "fit", "centroid", "slope", "noise", "partial2", "partial3", "partial4", "partial5"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main():
    import numpy as np
    matches = []
    for path in (ROOT / "build/next_piano_timbre").glob("*/checkpoint.json"):
        state = json.loads(path.read_text())
        if any(row.get("family") == "vocals" for row in state["selection"]):
            if all(digest(ROOT / p) == checksum for p, checksum in state["signatures"].items()):
                matches.append((path, state))
    assert len(matches) == 1, "Need one current singer-disjoint timbre capture"
    checkpoint, state = matches[0]
    directory = checkpoint.parent
    assert digest(directory / "candidates.tsv") == state["candidates_sha256"]
    selection = {row["id"]: row for row in state["selection"]}
    data = []
    for row in rows(directory / "candidates.tsv"):
        sample = selection[row["sample_id"]]
        visible = row["visible_voice"] == "1"
        if not visible:
            continue
        row["owner_name"] = {"2": "piano"}.get(row["owner"], "")
        row["correct"] = sample["family"] == "vocals" and int(row["midi"]) == sample["midi"]
        row["cohort"] = sample["family"] + "-" + sample["cohort"]
        data.append(row)
    legacy = ROOT / "build/real_note_full_mix_attributes.tsv"
    mapping = {"onset": "onset_strength", "decay": "decay_rate", "pitch": "pitch_confidence", "fit": "fit_error"}
    for old in rows(legacy):
        if not old["debug_midi"] or not any(value.split(":")[0] == old["debug_note"] for value in old["vocal_visual_notes"].split(",")):
            continue
        row = {key: old[mapping.get(key, key)] for key in FEATURES}
        row.update(owner_name=old["debug_owner"], keyboard_score=old["keyboard_score"], guitar_score=old["guitar_score"],
                   vocal_score=old["vocal_score"], profile=old["vocal_tone_profile"], sample_id=old["sample_id"],
                   correct=old["family"] == "vocals" and old["debug_midi"] == old["expected_midi"], cohort="legacy-calibration")
        data.append(row)
    def eligible(row):
        return supported_keyboard(row["owner_name"], float(row["keyboard_score"]), float(row["guitar_score"]),
                                  float(row["vocal_score"]), row["profile"] == "1", float(row["pitch"]), float(row["periodicity"]))
    def vector(row):
        values = [float(row[key]) for key in FEATURES]
        assert all(math.isfinite(value) for value in values)
        return [math.copysign(math.log1p(abs(value)), value) for value in values]
    training = [row for row in data if "heldout" not in row["cohort"] and eligible(row)]
    assert sum(row["correct"] for row in training) >= 5
    assert any(row["correct"] and "heldout" in row["cohort"] for row in data)
    x = np.array([vector(row) for row in training])
    y = np.array([int(row["correct"]) for row in training])
    predict, model = fit_forest(x, y, 2)
    probabilities = predict(x)[:, 0]
    threshold = max(.90, min(1., float(probabilities[y == 1].max()) + .01))
    metrics = {}
    for row in data:
        result = metrics.setdefault(row["cohort"], dict(visible_voice_cells=0, eligible=0,
                    protected_correct_cells=0, correct_losses=0, wrong_removed=0))
        result["visible_voice_cells"] += 1
        result["protected_correct_cells"] += row["correct"]
        if not eligible(row):
            continue
        result["eligible"] += 1
        remove = float(predict(np.array([vector(row)]))[0, 0]) >= threshold
        result["correct_losses"] += remove and row["correct"]
        result["wrong_removed"] += remove and not row["correct"]
    held_gains = sum(r["wrong_removed"] for name, r in metrics.items() if "heldout" in name)
    decision = "candidate" if held_gains and not any(r["correct_losses"] for r in metrics.values()) else "reject"
    report = dict(metrics=metrics, threshold=threshold, training_rows=len(training), features=FEATURES, model=model,
                  decision=decision, inputs={str(p.relative_to(ROOT)): digest(p) for p in
                    (checkpoint, directory / "candidates.tsv", legacy, Path(__file__), ROOT / "scripts/evaluate_next_detection.py", ROOT / "scripts/audit_keyboard_voice_separation.py")},
                  scope="Offline gated Voice suppression; calibration on MAPS and legacy controls, independent MAESTRO/singer-heldout VocalSet; no production promotion")
    output = ROOT / "build/next_detection/keyboard_voice_classifier.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "model"}, indent=2))


if __name__ == "__main__":
    main()
