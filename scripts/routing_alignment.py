"""Onset-envelope alignment diagnostics; never shift evaluation labels."""
import math


def lag_evidence(audio, midi, step, maximum=.4):
    import numpy as np
    audio, midi = np.asarray(audio, dtype=float), np.asarray(midi, dtype=float)
    if audio.shape != midi.shape or audio.ndim != 1 or len(audio) < 20 or not np.isfinite(audio).all() or not np.isfinite(midi).all():
        raise ValueError('Need equal finite onset envelopes')
    if not math.isfinite(step) or step <= 0 or not math.isfinite(maximum) or maximum < 0:
        raise ValueError('Invalid alignment resolution')
    scores = {}
    for lag in range(-int(maximum / step + .5), int(maximum / step + .5) + 1):
        a, b = (audio[lag:], midi[:len(midi) - lag]) if lag >= 0 else (audio[:len(audio) + lag], midi[-lag:])
        if len(a) < 20:
            continue
        a, b = a - a.mean(), b - b.mean()
        denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denominator > 1e-12:
            scores[lag] = float(np.dot(a, b) / denominator)
    if not scores:
        return dict(valid=False, reason='No onset variation')
    best = max(scores, key=lambda lag: (scores[lag], -abs(lag), -lag))
    return dict(valid=True, audio_lag_ms=round(best * step * 1000, 6),
                best_correlation=scores[best], zero_correlation=scores.get(0),
                boundary_peak=abs(best) == int(maximum / step + .5),
                scope='Positive lag means audio novelty follows MIDI; diagnostic evidence, not an automatic alignment correction')


def envelopes(samples, rate, notes):
    import numpy as np
    samples = np.asarray(samples, dtype=float)
    if not len(samples) or not np.isfinite(samples).all() or not 8000 <= rate <= 192000:
        raise ValueError('Invalid PCM')
    hop = int(rate * .01 + .5)
    size = 1
    while size < rate * .02:
        size *= 2
    padded = np.pad(samples, (size // 2, size // 2))
    windows = np.lib.stride_tricks.sliding_window_view(padded, size)[::hop]
    spectrum = np.abs(np.fft.rfft(windows * np.hanning(size), axis=1))
    frequencies = np.fft.rfftfreq(size, 1 / rate)
    spectrum = spectrum[:, (frequencies >= 40) & (frequencies <= 5000)]
    scale = max(float(np.quantile(spectrum, .95)), 1e-12)
    compressed = np.log1p(spectrum / scale)
    novelty = np.r_[0., np.maximum(np.diff(compressed, axis=0), 0).mean(axis=1)]
    impulses = np.zeros(len(novelty))
    for note in notes:
        if note['channel'] == 9:
            continue
        index = int(note['start'] * rate / hop + .5)
        if 0 <= index < len(impulses):
            impulses[index] += 1
    kernel = np.exp(-.5 * (np.arange(-6, 7) / 2.) ** 2)
    kernel /= kernel.sum()
    return np.convolve(novelty, kernel, mode='same'), np.convolve(impulses, kernel, mode='same'), hop / rate
