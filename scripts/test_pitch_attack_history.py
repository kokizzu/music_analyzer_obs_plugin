#!/usr/bin/env python3
"""Prove the isolated request cadence does not change the model waveform."""
import hashlib
import json
from pathlib import Path
import subprocess
from publish_next_detection import git
from routing_duration_baseline import ROOT,atomic_json,digest


def main():
    pointer=json.loads((ROOT/'build/pitch_attack_evidence_native/current.json').read_text())
    build_path=ROOT/pointer['build']
    built=json.loads(build_path.read_text())
    assert digest(build_path)==pointer['sha256']
    primary={name:git('show','HEAD:src/'+name) for name in ('basic_pitch_pcm_history.hpp','basic_pitch_pcm_history.cpp')}
    assert all(hashlib.sha256(text.encode()).hexdigest()==built['inputs']['sources'][name] for name,text in primary.items())
    inputs=dict(build_sha256=digest(build_path),script_sha256=digest(Path(__file__)),test_sha256=digest(ROOT/'tests/pitch_attack_history_parity.cpp'),
                dense_sources={n:digest(build_path.parent/n) for n in primary})
    directory=ROOT/'build/pitch_attack_history_parity'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    for name in ('basic_pitch_onnx_runtime.hpp','basic_pitch_pcm_history.hpp','basic_pitch_pcm_history.cpp'):
        (directory/name).write_bytes((build_path.parent/name).read_bytes())
    for name,text in primary.items():
        text=text.replace('BasicPitchPcmHistory','PrimaryPitchPcmHistory').replace('"basic_pitch_pcm_history.hpp"','"basic_pitch_pcm_history_primary.hpp"')
        (directory/name.replace('history.','history_primary.')).write_text(text)
    binary=directory/'parity'
    subprocess.run(['g++','-O2','-std=c++17','-I'+str(directory),str(ROOT/'tests/pitch_attack_history_parity.cpp'),
                    str(directory/'basic_pitch_pcm_history.cpp'),str(directory/'basic_pitch_pcm_history_primary.cpp'),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
    atomic_json(directory/'report.json',dict(inputs=inputs,binary_sha256=digest(binary),passed=True,rates=[16000,44100,48000]))
    atomic_json(directory.parent/'current.json',dict(report=str((directory/'report.json').relative_to(ROOT)),sha256=digest(directory/'report.json')))


if __name__=='__main__':
    main()
