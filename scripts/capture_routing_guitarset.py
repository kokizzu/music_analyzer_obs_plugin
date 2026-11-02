#!/usr/bin/env python3
"""Capture actual musical Guitar performances with performer-disjoint cohorts."""
import array
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import wave

from routing_duration_baseline import ROOT, atomic_json, digest, primary_build


def main():
    _, build = primary_build()
    matches = []
    for path in (ROOT / 'build/routing_candidate_evidence').glob('*/report.json'):
        state = json.loads(path.read_text())
        if state['complete'] and state['inputs']['build'] == build:
            matches.append((path, state))
    assert len(matches) == 1
    exporter_path, exporter = matches[0]
    binary = exporter_path.parent / 'replay'
    assert digest(binary) == exporter['binary_sha256']
    selected = []
    for performer, cohort in (('00', 'training'), ('01', 'training'), ('02', 'calibration'), ('05', 'heldout')):
        paths = sorted((ROOT / 'build/guitarset').glob(performer + '_*_comp_mic.wav'), key=lambda p: hashlib.sha256(p.name.encode()).hexdigest())[:4]
        assert len(paths) == 4
        for path in paths:
            selected.append(dict(id=path.stem, cohort=cohort, group='GuitarSet-' + performer,
                                 audio=str(path.relative_to(ROOT)), audio_sha256=digest(path), protect_entire_guitar_row=True))
    assert len({sample['audio_sha256'] for sample in selected}) == len(selected)
    inputs = dict(selection=selected, exporter_sha256=digest(exporter_path), script_sha256=digest(Path(__file__)))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    output = ROOT / 'build/routing_guitarset_controls' / key
    output.mkdir(parents=True, exist_ok=True)
    checkpoint = output / 'report.json'
    report = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False,
        scope='Actual solo-instrument chordal Guitar performances; performers 00/01 fit, 02 calibration, 05 heldout; untouched 03/04 reserved; all Guitar-row pitches conservatively protected')
    assert report['inputs'] == inputs
    atomic_json(checkpoint, report)
    for sample in selected:
        source = ROOT / sample['audio']
        raw, destination = output / (sample['id'] + '.f32'), output / (sample['id'] + '.tsv')
        with wave.open(str(source), 'rb') as audio:
            assert audio.getsampwidth() == 2 and audio.getcomptype() == 'NONE'
            rate, channels = audio.getframerate(), audio.getnchannels()
            values = array.array('h', audio.readframes(min(audio.getnframes(), rate * 10)))
        if sys.byteorder != 'little':
            values.byteswap()
        mono = array.array('f', (sum(values[i:i + channels]) / (32768 * channels) for i in range(0, len(values), channels)))
        assert len(mono) >= rate * 10, 'Need ten seconds of original recording'
        if sys.byteorder != 'little':
            mono.byteswap()
        raw.write_bytes(mono.tobytes())
        if sample['id'] not in report['recordings']:
            subprocess.run([str(binary), str(raw), str(rate), str(destination)], check=True, timeout=180)
        else:
            assert digest(destination) == report['recordings'][sample['id']]['sha256']
        with destination.open() as stream:
            seen = {int(row['end_sample']) for row in csv.DictReader(stream, delimiter='\t')}
        hop = int(rate * .05 + .5)
        assert seen == set(range(hop, len(mono) // hop * hop + 1, hop))
        assert digest(source) == sample['audio_sha256']
        report['recordings'][sample['id']] = dict(sha256=digest(destination), prefix_sha256=digest(raw), rate=rate, windows=len(seen))
        atomic_json(checkpoint, report)
        print(sample['group'], sample['cohort'], len(seen), 'windows', flush=True)
    assert digest(Path(__file__)) == inputs['script_sha256'] and digest(binary) == exporter['binary_sha256']
    report['complete'] = True
    atomic_json(checkpoint, report)
    print(checkpoint.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
