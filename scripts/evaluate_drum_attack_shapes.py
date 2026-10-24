#!/usr/bin/env python3
"""Screen cheap 100 ms attack/decay features on independent acoustic drums."""
import csv
import hashlib
import json
from pathlib import Path
import wave
import argparse

from evaluate_next_detection import fit_forest

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ["kick", "snare", "hihat", "crash", "tom", "ride", "rim"]


def features(samples, rate):
    import numpy as np
    samples = np.asarray(samples, dtype=float)[:int(rate * .1)]
    if len(samples) < rate * .05 or not np.isfinite(samples).all():
        return None
    samples = samples - samples.mean()
    peak = np.abs(samples).max()
    if peak < 1e-6:
        return None
    samples /= peak
    splits = [samples[int(rate * a):int(rate * b)] for a, b in ((0, .01), (.01, .025), (.025, .05), (.05, .1))]
    rms = [float(np.sqrt(np.mean(part ** 2))) if len(part) else 0. for part in splits]
    zcr = [float(np.mean(np.signbit(part[1:]) != np.signbit(part[:-1]))) if len(part) > 1 else 0. for part in splits]
    def bands(part):
        spectrum = np.abs(np.fft.rfft(part * np.hanning(len(part)))) ** 2
        frequency = np.fft.rfftfreq(len(part), 1 / rate)
        bounds = [0, 80, 180, 400, 1000, 2500, 5000, 8000]
        values = np.array([spectrum[(frequency >= low) & (frequency < high)].sum() for low, high in zip(bounds, bounds[1:])])
        return values / max(values.sum(), 1e-12), spectrum, frequency
    energy, spectrum, frequency = bands(samples)
    early = bands(samples[:max(2, int(rate * .025))])[0]
    late = bands(samples[max(0, int(rate * .05)):])[0]
    usable = spectrum[frequency < 8000] + 1e-12
    flatness = float(np.exp(np.mean(np.log(usable))) / usable.mean())
    centroid = float((spectrum * np.minimum(frequency, 8000)).sum() / max(spectrum.sum(), 1e-12) / 8000)
    nfft = 1 << (2 * len(samples) - 1).bit_length()
    transform = np.fft.rfft(samples, nfft)
    autocorrelation = np.fft.irfft(transform * transform.conj(), nfft)[:len(samples)]
    lower, upper = max(1, rate // 1000), min(len(samples), rate // 60)
    periodicity = float(autocorrelation[lower:upper].max() / max(autocorrelation[0], 1e-12))
    return rms + zcr + energy.tolist() + (late - early).tolist() + [flatness, centroid, periodicity,
                    float(np.argmax(np.abs(samples)) / len(samples))]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def decode_pcm(raw, width, channels):
    import numpy as np
    if width == 1:
        values = (np.frombuffer(raw, dtype="u1").astype(float) - 128) / 128
    elif width == 2:
        values = np.frombuffer(raw, dtype="<i2").astype(float) / 32768
    elif width == 3:
        bytes_ = np.frombuffer(raw, dtype="u1").reshape(-1, 3).astype(np.int32)
        values = bytes_[:, 0] | bytes_[:, 1] << 8 | bytes_[:, 2] << 16
        values = np.where(values & 0x800000, values - 0x1000000, values) / 8388608
    elif width == 4:
        values = np.frombuffer(raw, dtype="<i4").astype(float) / 2147483648
    else:
        raise ValueError("unsupported integer PCM width")
    return values.reshape(-1, channels).mean(axis=1)


def main():
    import numpy as np
    parser = argparse.ArgumentParser()
    parser.add_argument('--spectral', action='store_true')
    args = parser.parse_args()
    configurations = [("training", "build/drum_samples_full", "build/drum_full_exact_attribute_rows.tsv"),
                      ("29k-heldout", "build/InstrumentSamples/29k_samples_drums_samples", "build/29k_samples_drums_primary_attribute_rows.tsv"),
                      ("Virtuosity-heldout", "build/InstrumentSamples/virtuosity_drums_samples", "build/virtuosity_drums_primary_attribute_rows.tsv")]
    data, signatures, audio_hashes = [], {}, {}
    for cohort, folder, baseline in configurations:
        base = ROOT / folder
        manifest = base / "manifest.tsv"
        reference = {row["sample"]: row for row in read_rows(ROOT / baseline)}
        signatures[folder + "/manifest.tsv"] = digest(manifest)
        signatures[baseline] = digest(ROOT / baseline)
        counts = {}
        for row in sorted(read_rows(manifest), key=lambda r: hashlib.sha256(r["path"].encode()).hexdigest()):
            category = row["category"]
            if row["path"] not in reference or (cohort == "training" and counts.get(category, 0) >= 200):
                continue
            counts[category] = counts.get(category, 0) + 1
            path = base / row["path"]
            audio_hashes[str(path.relative_to(ROOT))] = digest(path)
            with wave.open(str(path), "rb") as audio:
                assert audio.getcomptype() == "NONE"
                rate, channels = audio.getframerate(), audio.getnchannels()
                width = audio.getsampwidth()
                raw = audio.readframes(int(rate * .1))
            samples = decode_pcm(raw, width, channels)
            vector = features(samples, rate)
            if vector is not None and args.spectral:
                from native_timbre_reference import cepstra
                spectral = cepstra(samples[:int(rate * .1)], rate)
                vector = vector + spectral if spectral is not None else None
            if vector is not None:
                data.append(dict(cohort=cohort, vector=vector, truth=category, native=reference[row["path"]]["got"]))
    training = [row for row in data if row["cohort"] == "training"]
    x = np.array([row["vector"] for row in training])
    y = np.array([CLASSES.index(row["truth"]) for row in training])
    predict, model = fit_forest(x, y, len(CLASSES))
    probabilities = predict(x)
    cuts = {}
    for index, category in enumerate(CLASSES):
        wrong = (probabilities.argmax(axis=1) == index) & (y != index)
        cuts[category] = max(.90, min(1., float(probabilities[wrong, index].max()) + .01)) if wrong.any() else .90
    metrics = {}
    for row, probability in zip(data, predict(np.array([row["vector"] for row in data]))):
        if row["cohort"] == "training":
            continue
        result = metrics.setdefault(row["cohort"], dict(samples=0, changes=0, gains=0, correct_losses=0, false_changes=0))
        predicted = CLASSES[int(probability.argmax())]
        candidate = predicted if predicted in {"snare", "rim", "ride"} and probability.max() >= cuts[predicted] else row["native"]
        result["samples"] += 1
        result["changes"] += candidate != row["native"]
        result["gains"] += candidate == row["truth"] and row["native"] != row["truth"]
        result["correct_losses"] += row["native"] == row["truth"] and candidate != row["truth"]
        result["false_changes"] += candidate != row["native"] and candidate != row["truth"]
    assert all(digest(ROOT / path) == expected for path, expected in {**signatures, **audio_hashes}.items())
    report = dict(inputs=signatures, audio_sha256=audio_hashes, training_samples=len(training), cutoffs=cuts, metrics=metrics, model=model,
                  script_sha256=digest(Path(__file__)),
                  decision="candidate" if any(row["gains"] for row in metrics.values()) and not any(row["correct_losses"] or row["false_changes"] for row in metrics.values()) else "reject",
                  scope="Offline 100ms PCM attack/decay/periodicity features; exact cached native-primary comparison; independent acoustic corpora; not a live accuracy/latency claim")
    if args.spectral:
        report['inputs']['scripts/native_timbre_reference.py'] = digest(ROOT / 'scripts/native_timbre_reference.py')
    output = ROOT / 'build/next_detection' / ('drum_spectral_shapes.json' if args.spectral else 'drum_attack_shapes.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(metrics=metrics, cutoffs=cuts, training_samples=len(training), decision=report["decision"]), indent=2))


if __name__ == "__main__":
    main()
