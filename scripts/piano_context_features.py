"""Causal acoustic-piano context features; identities and labels are not inputs."""
import hashlib
import numpy as np
from native_timbre_reference import cepstra


def negative_cohort(group):
    bucket = int(hashlib.sha256(('piano-context-v1:' + group).encode()).hexdigest()[:8], 16) % 10
    return 'training' if bucket < 6 else 'calibration' if bucket < 8 else 'heldout'


def nsynth_group(identifier):
    return 'NSynth-' + identifier.removesuffix('-48k').removesuffix('-original').rsplit('-', 2)[0]


def features(samples, rate, cached=None):
    samples = np.asarray(samples, dtype=np.float32)
    values = cepstra(samples, rate) if cached is None else cached
    if values is None:
        return None
    used = samples[-min(len(samples), round(rate * .1)):].astype(float)
    rms = np.sqrt(np.mean(used * used))
    shape = [float(np.sqrt(np.mean(used[i*len(used)//3:(i+1)*len(used)//3] ** 2)) / max(rms, 1e-12)) for i in range(3)]
    result = list(values) + shape
    assert len(result) == 27 and np.isfinite(result).all()
    return result
