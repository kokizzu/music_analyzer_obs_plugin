"""Independent nonnegative joint spectral fit for training diagnostics."""
import numpy as np


def fit(dictionary, observations, iterations=80):
    assert dictionary.ndim == observations.ndim == 2 and dictionary.shape[0] == observations.shape[0]
    assert np.isfinite(dictionary).all() and np.isfinite(observations).all()
    assert (dictionary >= 0).all() and (observations >= 0).all()
    gram = dictionary.T @ dictionary
    projection = dictionary.T @ observations
    activations = np.maximum(projection, 1e-12)
    for _ in range(iterations):
        activations *= projection / np.maximum(gram @ activations, 1e-12)
    return activations


def spectrum(values):
    assert values.shape[-1] == 1600 and np.isfinite(values).all()
    centered = values - values.mean(axis=-1, keepdims=True)
    result = np.abs(np.fft.rfft(centered * np.hanning(1600), n=4096, axis=-1))
    # The same fixed three-bin smoothing tolerates modest tuning differences
    # in references and current frames. No learned/held-out frequency weights.
    return (np.pad(result, ((0, 0), (1, 1)), mode='constant')[:, :-2] + 2 * result +
            np.pad(result, ((0, 0), (1, 1)), mode='constant')[:, 2:]) / 4
