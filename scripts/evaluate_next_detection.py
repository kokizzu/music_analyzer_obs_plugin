#!/usr/bin/env python3
"""Frozen, label-independent candidate policies; never alter live routing.

Cached captures are screening evidence. Promotion requires current-source replay.
"""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def tempo_grid(items, bpm):
    """Weighted explained onsets minus empty grid cells, normalized by weight."""
    if len(items) < 3 or not 50 <= bpm <= 220:
        return 0.
    period = 60 / bpm
    tolerance = min(.075, period * .12)
    total = sum(max(0, item[1]) for item in items)
    if total <= 0:
        return 0.
    best = 0.
    for anchor in items:
        first = math.ceil((items[0][0] - anchor[0]) / period)
        last = math.floor((items[-1][0] - anchor[0]) / period)
        cells = last - first + 1
        if cells < 3:
            continue
        aligned, filled, previous = 0., set(), None
        direct = 0
        for time, strength, *_ in items:
            cell = math.floor((time - anchor[0]) / period + .5)
            error = abs(time - anchor[0] - cell * period)
            if error <= tolerance:
                aligned += max(0, strength) * (1 - error / tolerance) ** 2
                filled.add(cell)
        for cell in sorted(filled):
            direct += previous is not None and cell == previous + 1
            previous = cell
        coverage = len(filled) / cells
        score = aligned / total * coverage - .25 * (1 - coverage)
        score *= .5 + .5 * direct / max(1, len(filled) - 1)
        best = max(best, score)
    return best


def tempo_candidate(actual, items):
    if actual <= 0:
        return actual
    candidates = [bpm for bpm in (actual / 2, actual, actual * 2) if 50 <= bpm <= 220]
    ranked = sorted(((tempo_grid(items, bpm), bpm) for bpm in candidates), reverse=True)
    score, bpm = ranked[0]
    # Explicit margin over the current interpretation; no annotation input.
    return bpm if score >= .75 and score - tempo_grid(items, actual) >= .2 else actual


def bpm_screen():
    from evaluate_source_tempo_histories import peaks, estimate, close
    directory = ROOT / "build/accuracy_goal_bpm/live-cadence-baseline-20261014"
    result, signatures = {}, {}
    for corpus in ("Ballroom", "FiloBass", "GTZAN-Rhythm"):
        path = directory / (corpus + "-source-history.tsv")
        signatures[str(path.relative_to(ROOT))] = digest(path)
        records = defaultdict(list)
        with path.open() as stream:
            for row in csv.reader(stream, delimiter="\t"):
                records[row[0]].append([float(v) for v in row[1:]])
        counts = dict(recordings=len(records), gains=0, losses=0, alias_before=0, alias_after=0, changes=0)
        for frames in records.values():
            expected, interval, actual = frames[0][:3]
            items = peaks([row[4:] for row in frames], interval, "current")
            assert estimate(items) == actual, "Cached baseline reproduction mismatch"
            candidate = tempo_candidate(actual, items)
            counts["gains"] += close(candidate, expected) and not close(actual, expected)
            counts["losses"] += close(actual, expected) and not close(candidate, expected)
            counts["changes"] += actual != candidate
            for key, value in (("alias_before", actual), ("alias_after", candidate)):
                counts[key] += value > 0 and not close(value, expected) and (close(value * 2, expected) or close(value / 2, expected))
        result[corpus] = counts
    return dict(inputs=signatures, results=result,
                decision="candidate" if sum(r["gains"] for r in result.values()) > 0 and not any(r["losses"] for r in result.values()) else "reject",
                scope="Historical causal onset screening, not final PCM-corrected runtime proof")


def chord_template(label):
    label = label.split("=")[0]
    match = re.fullmatch(r"([A-G])([#b]?)(m|dim|aug|pow|sus2|sus4)?", label)
    if not match:
        return None
    letter, accidental, quality = match.groups()
    root = ({"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[letter] + {"": 0, "#": 1, "b": -1}[accidental]) % 12
    intervals = {None: (0, 4, 7), "m": (0, 3, 7), "dim": (0, 3, 6), "aug": (0, 4, 8),
                 "pow": (0, 7), "sus2": (0, 2, 7), "sus4": (0, 5, 7)}[quality]
    return [(root + interval) % 12 for interval in intervals]


def chord_score(label, chroma):
    template = chord_template(label)
    total = sum(chroma)
    if template is None or total <= 0:
        return -1.
    inside = sum(chroma[i] for i in template) / total
    # Penalize a candidate whose defining third/suspension is absent.
    core = min(chroma[i] for i in template) / max(max(chroma), 1e-9)
    return inside - .5 * (1 - core)


def chord_screen():
    directory = ROOT / "build/accuracy_goal_chords/production-core-confirmation-1f2e4f1ede05"
    result, inputs = {}, {}
    for corpus in ("MAPS", "MAESTRO"):
        path = directory / (corpus + ".tsv")
        inputs[str(path.relative_to(ROOT))] = digest(path)
        counts = dict(frames=0, gains=0, losses=0, new_wrong=0, changes=0)
        prior_context, pending, repeats = None, None, 0
        for row in rows(path):
            context = (row["recording"], row["anchor_sample"])
            if context != prior_context:
                pending, repeats = None, 0
                prior_context = context
            actual = row["global_chord"]
            chroma = list(map(float, row["global_chroma"].split(",")))
            labels = {row[key] for key in ("global_chord", "keyboard_chord", "guitar_chord")}
            ranked = sorted(((chord_score(label, chroma), label) for label in labels), reverse=True)
            score, label = ranked[0]
            eligible = float(row["confidence"]) < .7 and score > .3 and score - chord_score(actual, chroma) > .2
            repeats = repeats + 1 if eligible and pending == label else 1
            pending = label if eligible else None
            candidate = label if eligible and repeats >= 2 else actual
            truth = set(row["expected_chords"].split("/")) - {"", "--"}
            old, new = actual.split("=")[0] in truth, candidate.split("=")[0] in truth
            counts["frames"] += 1
            counts["changes"] += candidate != actual
            if truth:
                counts["gains"] += new and not old
                counts["losses"] += old and not new
                counts["new_wrong"] += candidate not in ("", "--") and not new and (old or actual in ("", "--"))
        result[corpus] = counts
    return dict(inputs=inputs, results=result,
                decision="candidate" if sum(r["gains"] for r in result.values()) > 0 and not any(r["losses"] or r["new_wrong"] for r in result.values()) else "reject",
                scope="Causal two-frame chroma/core reranking of existing source candidates; no future labels in selection")


def fit_classifier(x, y, classes):
    import numpy as np
    mean, scale = x.mean(axis=0), np.maximum(x.std(axis=0), .01)
    x = np.column_stack([np.ones(len(x)), (x - mean) / scale])
    weights = np.zeros((x.shape[1], classes))
    target = np.eye(classes)[y]
    balanced = 1 / np.maximum(np.bincount(y, minlength=classes)[y], 1)
    balanced /= balanced.sum()
    for _ in range(400):
        logits = x @ weights
        logits -= logits.max(axis=1, keepdims=True)
        prediction = np.exp(logits)
        prediction /= prediction.sum(axis=1, keepdims=True)
        gradient = x.T @ ((prediction - target) * balanced[:, None])
        gradient[1:] += .01 * weights[1:]
        weights -= .2 * gradient
    def predict(values):
        logits = np.column_stack([np.ones(len(values)), (values - mean) / scale]) @ weights
        logits -= logits.max(axis=1, keepdims=True)
        result = np.exp(logits)
        return result / result.sum(axis=1, keepdims=True)
    return predict, dict(mean=mean.tolist(), scale=scale.tolist(), weights=weights.tolist())


def fit_forest(x, y, classes):
    """Small deterministic forest; bounded comparisons per native candidate."""
    import numpy as np
    rng = np.random.default_rng(20261024)
    balance = 1 / np.maximum(np.bincount(y, minlength=classes), 1)
    def build(indices, depth):
        counts = np.bincount(y[indices], minlength=classes) * balance
        distribution = (counts + 1e-6) / (counts.sum() + classes * 1e-6)
        if depth == 8 or len(indices) < 24 or np.count_nonzero(counts) == 1:
            return distribution.tolist()
        best = None
        for feature in rng.choice(x.shape[1], size=max(2, int(math.sqrt(x.shape[1]))), replace=False):
            values = x[indices, feature]
            for threshold in np.unique(np.quantile(values, [.2, .4, .6, .8])):
                left = indices[values <= threshold]
                right = indices[values > threshold]
                if min(len(left), len(right)) < 8:
                    continue
                score = 0.
                for part in (left, right):
                    frequencies = np.bincount(y[part], minlength=classes) * balance
                    score += frequencies.sum() - (frequencies ** 2).sum() / frequencies.sum()
                if best is None or score < best[0]:
                    best = (score, int(feature), float(threshold), left, right)
        if best is None:
            return distribution.tolist()
        _, feature, threshold, left, right = best
        return dict(feature=feature, threshold=threshold, left=build(left, depth + 1), right=build(right, depth + 1))
    trees = [build(rng.integers(0, len(x), min(len(x), 6000)), 0) for _ in range(24)]
    def predict(values):
        result = np.zeros((len(values), classes))
        for tree in trees:
            for index, value in enumerate(values):
                node = tree
                while isinstance(node, dict):
                    node = node["left"] if value[node["feature"]] <= node["threshold"] else node["right"]
                result[index] += node
        return result / len(trees)
    return predict, dict(trees=trees, max_depth=8)


def classifier_screen(drums=False, forest=False):
    import numpy as np
    if drums:
        paths = [ROOT / "build" / name for name in ("drum_full_exact_attribute_rows.tsv", "29k_samples_drums_primary_attribute_rows.tsv", "virtuosity_drums_primary_attribute_rows.tsv")]
        features = ["energy_low", "energy_mid", "energy_high", "kick_body", "snare_body", "tom_body", "snare_crack", "upper_tom_body"]
        features += [name + suffix for name in ("snare", "rim", "ride", "hihat", "tom", "crash") for suffix in ("_band", "_seg", "_shape_score")]
        labels = ["kick", "snare", "hihat", "crash", "tom", "ride", "rim"]
        training = rows(paths[0])
        held = [dict(row, cohort=path.stem) for path in paths[1:] for row in rows(path)]
        def truth(row): return row["expected"]
        def baseline(row): return row["got"]
    else:
        paths = [ROOT / "build/real_note_full_mix_attributes.tsv"]
        features = ["onset_strength", "decay_rate", "pitch_stability", "simultaneous_onset", "spectral_level", "pitch_confidence", "periodicity", "harmonicity", "fit_error", "centroid", "slope", "noise", "partial1", "partial2", "partial3", "partial4", "partial5"]
        labels = ["bass", "guitar", "piano", "vocals", "other", "reject"]
        data = [row for row in rows(paths[0]) if row["debug_midi"] and row["family"] in labels]
        # Hold out instrument identities, not adjacent frames of the same note.
        def held_out(row):
            group = row["sample_id"].rsplit("-", 2)[0]
            return int(hashlib.sha256(group.encode()).hexdigest()[:8], 16) % 4 == 0
        training = [row for row in data if not held_out(row)]
        held = [dict(row, cohort="instrument-identity-holdout") for row in data if held_out(row)]
        def truth(row): return row["family"] if row["debug_midi"] == row["expected_midi"] else "reject"
        def baseline(row): return {"vocal": "vocals", "amb": "reject", "ambiguous": "reject"}.get(row["debug_owner"], row["debug_owner"])
    training = [r for r in training if truth(r) in labels]
    held = [r for r in held if truth(r) in labels]
    def vector(row):
        values = [max(0., float(row[key] or 0)) for key in features]
        logged = [math.log1p(value) for value in values]
        # Scale-independent attack/band/partial contrast, rather than source IDs.
        total = sum(values) + 1e-9
        return logged + [value / total for value in values]
    x = np.array([vector(row) for row in training])
    y = np.array([labels.index(truth(row)) for row in training])
    predict, model = (fit_forest if forest else fit_classifier)(x, y, len(labels))
    probability = predict(x)
    predicted_training = probability.argmax(axis=1)
    # Calibrate each target independently: an uncertain catch-all class must
    # not determine the threshold for every named instrument/articulation.
    cutoffs = {}
    for index, label in enumerate(labels):
        wrong = (predicted_training == index) & (y != index)
        cutoffs[label] = max(.90, min(1., float(probability[wrong, index].max()) + .01)) if wrong.any() else .90
    predictions = predict(np.array([vector(row) for row in held]))
    result = {}
    for row, probability in zip(held, predictions):
        counts = result.setdefault(row["cohort"], dict(rows=0, changes=0, gains=0, losses=0, false_changes=0))
        actual = baseline(row)
        predicted = labels[int(probability.argmax())]
        targets = {"snare", "rim", "ride"} if drums else {"guitar", "vocals"}
        candidate = predicted if predicted in targets and probability.max() >= cutoffs[predicted] else actual
        expected = truth(row)
        counts["rows"] += 1
        counts["changes"] += candidate != actual
        counts["gains"] += candidate == expected and actual != expected
        counts["losses"] += candidate != expected and actual == expected
        counts["false_changes"] += candidate != actual and candidate != expected
    return dict(inputs={str(path.relative_to(ROOT)): digest(path) for path in paths},
                results=result, training_rows=len(training), cutoffs=cutoffs, features=features,
                method="forest-24-depth8" if forest else "linear-log-ratio",
                model=model, decision="candidate" if sum(r["gains"] for r in result.values()) > 0 and not any(r["losses"] or r["false_changes"] for r in result.values()) else "reject",
                scope="Historical cached feature screen; native-owner classification, not integrated display accuracy; no live promotion")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["bpm", "chord", "timbre", "drum"])
    parser.add_argument("--forest", action="store_true")
    args = parser.parse_args()
    if args.forest and args.kind not in ("timbre", "drum"):
        parser.error("forest applies only to timbre/drum classifiers")
    result = bpm_screen() if args.kind == "bpm" else chord_screen() if args.kind == "chord" else classifier_screen(args.kind == "drum", args.forest)
    result["script_sha256"] = digest(Path(__file__))
    directory = ROOT / "build/next_detection"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (args.kind + ("-forest" if args.forest else "") + ".json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "model"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
