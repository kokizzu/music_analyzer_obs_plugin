#!/usr/bin/env python3
"""Independent vectorized reference for the native causal cepstral summary."""
import math


def cepstra(samples, rate):
    import numpy as np
    samples = np.asarray(samples, dtype=np.float32).astype(float)
    samples = samples[-min(len(samples), int(rate * .1 + .5)):]
    if not 8000 <= rate <= 192000 or not len(samples) or not np.isfinite(samples).all() or np.max(np.abs(samples)) < 1e-7:
        return None
    size = 1
    while size < int(rate * .032 + .5):
        size *= 2
    if len(samples) < size:
        return None
    mel = lambda frequency: 2595 * np.log10(1 + frequency / 700)
    edges = 700 * (10 ** (np.linspace(mel(20), mel(min(8000, rate * .49)), 28) / 2595) - 1)
    frequency = np.fft.rfftfreq(size, 1 / rate)
    weights = np.stack([np.maximum(0, np.minimum((frequency - edges[i]) / (edges[i + 1] - edges[i]),
                       (edges[i + 2] - frequency) / (edges[i + 2] - edges[i + 1]))) for i in range(26)])
    denominator = np.maximum(weights.sum(axis=1), 1e-12)
    dct = np.sqrt(2 / 26) * np.cos(np.pi * np.arange(1, 13)[:, None] * (np.arange(26)[None, :] + .5) / 26)
    frames = []
    for start in sorted({0, (len(samples) - size) // 2, len(samples) - size}):
        frame = samples[start:start + size]
        power = np.abs(np.fft.rfft((frame - frame.mean()) * np.hanning(size))) ** 2
        energy = weights @ power / denominator
        if energy.sum() < 1e-20:
            continue
        frames.append(dct @ np.log(np.maximum(energy / energy.sum(), 1e-8)))
    if not frames:
        return None
    return np.concatenate((np.mean(frames, axis=0), frames[-1] - frames[0])).tolist()
