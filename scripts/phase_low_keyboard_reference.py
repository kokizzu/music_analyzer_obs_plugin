"""Causal phase-vocoder evidence for experimental low-note validation."""
import numpy as np
from audit_multiscale_exposure import geometry


def projection(audio,endpoint,g):
    count,hann,total,weights=g
    if endpoint<count:
        return None
    values=np.asarray(audio[endpoint-count:endpoint],dtype=float)
    centered=values-float(hann@values)/total
    rms=np.sqrt(max(0.,float(hann@(centered*centered))/total))
    return (weights@centered)*2/total/max(np.sqrt(2)*rms,1e-12)


def short_support(previous,current,hop_seconds):
    if previous is None or current is None:
        return set()
    frequencies=np.array([440*2**((m-69)/12) for m in range(21,40)])
    frequencies=np.concatenate((frequencies,frequencies*3))
    residual=np.angle(current*np.conj(previous)*np.exp(-2j*np.pi*frequencies*hop_seconds))
    estimated=frequencies+residual/(2*np.pi*hop_seconds)
    cents=1200*np.log2(estimated/frequencies)
    valid=(np.abs(previous)>=.01)&(np.abs(current)>=.01)&np.isfinite(cents)&(np.abs(cents)<=25)
    return {i+21 for i in range(19) if valid[i] or valid[i+19]}
