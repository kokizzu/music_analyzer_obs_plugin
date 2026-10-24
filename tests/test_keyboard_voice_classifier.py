#!/usr/bin/env python3
"""Verify native forest parity, conservatism and profile/ownership vetoes."""
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
model_path = ROOT / "models/keyboard_voice_classifier.json"
state = json.loads(model_path.read_text())
header = (ROOT / "src/keyboard_voice_model_data.hpp").read_text()
assert hashlib.sha256(model_path.read_bytes()).hexdigest() in header
if "--full" in sys.argv:
    capture = next(ROOT / p for p in state["inputs"] if p.endswith("candidates.tsv"))
    with capture.open() as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
else:
    vectors = [
        [0, 0, 1, 0, .916992, .766809, .0769555, .162099, .252619, .0435353, .0462996, .198722, .0548322, .010761],
        [0, 0, 1, 0, .914065, .756749, .0887792, .153092, .256884, .0364221, .0163619, .210707, .0336348, .0167455],
        [0.] * 14, [1.] * 14,
    ]
    rows = [dict(zip(state["features"], map(str, values)), keyboard_score="1", guitar_score="0", vocal_score="0", owner="2", profile="0") for values in vectors]


def tree_score(tree, values, conservative):
    if isinstance(tree, list):
        return tree[0]
    value = values[tree["feature"]]
    epsilon = abs(value) * 1e-5 if conservative else 0.
    if value + epsilon <= tree["threshold"]:
        return tree_score(tree["left"], values, conservative)
    if value - epsilon > tree["threshold"]:
        return tree_score(tree["right"], values, conservative)
    return min(tree_score(tree["left"], values, conservative), tree_score(tree["right"], values, conservative))


directory = ROOT / "build/keyboard_voice_classifier_test"
directory.mkdir(parents=True, exist_ok=True)
cases, expected = [], []
for row in rows:
    raw = [float(row[key]) for key in state["features"]]
    values = [math.copysign(math.log1p(abs(value)), value) for value in raw]
    score = sum(tree_score(tree, values, True) for tree in state["model"]["trees"]) / 24
    original = sum(tree_score(tree, values, False) for tree in state["model"]["trees"]) / 24
    assert score <= original + 1e-12
    keys, guitar, voice = map(float, (row["keyboard_score"], row["guitar_score"], row["vocal_score"]))
    owner, profile = row["owner"] == "2", row["profile"] == "1"
    eligible = owner and not profile and keys >= .9 and guitar <= .05 and voice <= .05 and raw[4] >= .7 and raw[5] >= .5
    cases.append(raw + [keys, guitar, voice, int(owner), int(profile)])
    expected.append((score, eligible and score >= state["threshold"]))
    # Corroborated Vocal profile and non-Keyboard ownership always veto, even
    # if the model itself gives high probability.
    if score >= state["threshold"] and raw[4] >= .7 and raw[5] >= .5:
        cases += [raw + [1, 0, 0, 1, 1], raw + [1, 0, 0, 0, 0], raw + [1, .06, 0, 1, 0]]
        expected += [(score, False)] * 3
input_path, output_path = directory / "input.tsv", directory / "output.tsv"
input_path.write_text("".join("\t".join(map(repr, values)) + "\n" for values in cases))
subprocess.run([str(ROOT / "build/keyboard_voice_classifier"), str(input_path), str(output_path)], check=True)
lines = output_path.read_text().splitlines()
assert len(lines) == len(expected)
for line, (score, suppression) in zip(lines, expected):
    raw_score, raw_suppression = line.split("\t")
    assert abs(float(raw_score) - score) < 1e-12
    assert bool(int(raw_suppression)) == suppression
print("Native Keyboard/Voice model:", len(expected), "parity/veto cases passed; conservative predictions", sum(flag for _, flag in expected))
assert sum(flag for _, flag in expected) > 0
