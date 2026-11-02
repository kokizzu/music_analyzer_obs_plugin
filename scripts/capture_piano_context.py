#!/usr/bin/env python3
"""Freeze grouped source identities and collect current-window instrument cues."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import csv
import hashlib
import json
from itertools import groupby
from pathlib import Path
import wave

import numpy as np

from midi_sustain_reference import read_intervals
from piano_context_features import features, negative_cohort, nsynth_group
from routing_duration_baseline import ROOT, atomic_json, digest
from validate_routing_consensus import prepare


def load(path):
    with wave.open(str(path), 'rb') as stream:
        assert stream.getsampwidth() == 2 and stream.getcomptype() == 'NONE'
        rate, channels = stream.getframerate(), stream.getnchannels()
        values = np.frombuffer(stream.readframes(stream.getnframes()), dtype='<i2').reshape(-1, channels)
    return (values.astype(float).mean(axis=1) / 32768).astype(np.float32), rate


def collect(audio, rate, sample, output):
    count, hop = round(rate * .1), round(rate * .05)
    padded = np.pad(audio, (count, 0))
    ends = sorted({max(hop, min(len(audio)//hop*hop, round(len(audio)*fraction/hop)*hop)) for fraction in (.1, .25, .5, .75, .9)})
    for end in ends:
        vector = features(padded[end:end+count], rate)
        if vector is not None:
            output.append(dict(sample=sample['id'], group=sample['group'], cohort=sample['cohort'], label=sample['label'],
                               end_sample=end, rate=rate, values=vector))


def main():
    manifest = ROOT / 'build/real_note_samples/manifest.tsv'
    with manifest.open() as stream:
        nsynth = list(csv.DictReader(stream, delimiter='\t'))
    samples, augment, signatures = [], [], {str(manifest.relative_to(ROOT)): digest(manifest)}
    groups = {}
    for row in nsynth:
        acoustic = row['id'].startswith('keyboard_acoustic_004-')
        if row['family'] == 'piano' and not acoustic:
            continue  # Other keyboard timbres are outside this verifier's label scope.
        path = manifest.parent / row['path']
        group = nsynth_group(row['id'])
        sample = dict(id=row['id'], group=group, cohort='calibration' if acoustic else negative_cohort(group),
                      label=0 if acoustic else 1, audio=str(path.relative_to(ROOT)), audio_sha256=digest(path))
        samples.append(sample)
        if not acoustic:
            groups.setdefault(group, []).append(sample)
    # Rate augmentation remains in the same identity cohort. Fixed rank selection
    # is metadata-only and never follows classification outcomes.
    for group, entries in sorted(groups.items()):
        entries = sorted(entries, key=lambda s: s['id'])
        for index in sorted({0, len(entries)//2, len(entries)-1}):
            source = entries[index]
            augment.append(dict(source, id=source['id']+'-48k', target_rate=48000, fresh=True, seconds=4))
    real_sources = []
    nsynth_ids = {r['id'] for r in nsynth}
    for relative in ('build/routing_controls/84b9eb144888ea8d/report.json',
                     'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json',
                     'build/routing_guitarset_controls/9801a45ca6c823e8/report.json'):
        path = ROOT / relative
        source = json.loads(path.read_text())
        signatures[relative] = digest(path)
        for sample in source['inputs']['selection']:
            if sample['id'] in nsynth_ids:
                continue
            raw = path.parent / (sample['id']+'.f32')
            real_sources.append(dict(id=sample['id'], group=sample['group'], cohort=negative_cohort(sample['group']), label=1,
                                     raw=str(raw.relative_to(ROOT)), raw_sha256=digest(raw), rate=source['recordings'][sample['id']]['rate']))
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    native_path = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    baseline, native = (json.loads(p.read_text()) for p in (baseline_path, native_path))
    signatures[str(baseline_path.relative_to(ROOT))], signatures[str(native_path.relative_to(ROOT))] = digest(baseline_path), digest(native_path)
    inputs = dict(nsynth=samples, augmentation=augment, real_negatives=real_sources, signatures=signatures,
                  scripts={p: digest(ROOT / p) for p in ('scripts/capture_piano_context.py', 'scripts/piano_context_features.py',
                           'scripts/native_timbre_reference.py', 'scripts/validate_routing_consensus.py', 'scripts/midi_sustain_reference.py')},
                  features='24 causal cepstral mean/delta values plus three relative segment RMS values; no identity/rate/label features',
                  label_scope='Acoustic piano vs known non-keyboard sources. Other keyboard timbres and mixtures are unscored. All acoustic NSynth identity 004 is calibration-only.',
                  negative_split='SHA256 piano-context-v1:identity modulo10: 0-5 train,6-7 calibration,8-9 heldout', numpy_version=np.__version__)
    directory = ROOT / 'build/piano_context_data' / hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True, exist_ok=True)
    atomic_json(directory / 'plan.json', inputs)
    print('Frozen context identities:', len(samples), 'isolated sources,', len(augment), 'rate augmentations,', len(real_sources), 'real negatives', flush=True)
    data = []
    for index, sample in enumerate(samples, 1):
        audio, rate = load(ROOT / sample['audio'])
        collect(audio, rate, sample, data)
        if index % 200 == 0:
            print(index, '/', len(samples), 'isolated contexts', flush=True)
    for sample in augment:
        raw, rate = prepare(sample, directory)
        collect(np.fromfile(raw, dtype='<f4'), rate, sample, data)
    for sample in real_sources:
        collect(np.fromfile(ROOT / sample['raw'], dtype='<f4'), sample['rate'], sample, data)
    for name in ('training-1', 'training-2', 'training-3', 'training-4'):
        raw = baseline_path.parent / (name+'.f32')
        assert digest(raw) == baseline['recordings'][name]['prefix_sha256']
        rate = baseline['recordings'][name]['rate']
        audio = np.fromfile(raw, dtype='<f4')
        count = round(rate*.1)
        padded = np.pad(audio, (count,0))
        selected = next(s for s in baseline['selection'] if s['id']==name)
        midi = ROOT / selected['midi']
        assert digest(midi) == selected['midi_sha256']
        notes = read_intervals(midi.read_bytes())
        candidates = native_path.parent / (name+'.tsv')
        assert digest(candidates) == native['recordings'][name]['sha256']
        with candidates.open() as stream:
            for endpoint, group in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda r:int(r['end_sample'])):
                row = next(group)
                time = endpoint/rate
                if row['mfcc_valid']!='1' or not any(n['channel']!=9 and n['start']<time and n['end']>time-.1 for n in notes):
                    continue
                vector = features(padded[endpoint:endpoint+count], rate, [float(row['mfcc'+str(i)]) for i in range(24)])
                data.append(dict(sample=name, group='performance-'+name, cohort='calibration' if name=='training-4' else 'training',
                                 label=0, end_sample=endpoint, rate=rate, values=vector))
        print(name, 'piano frame contexts complete', flush=True)
    assert all(digest(ROOT / p)==h for p,h in inputs['scripts'].items())
    report = dict(inputs=inputs, data=data, complete=True, rows=len(data), scope='Feature capture only. No fitting, inference selection, fresh-performance access or native integration.')
    atomic_json(directory / 'report.json', report)
    atomic_json(directory.parent / 'current.json', dict(report=str((directory/'report.json').relative_to(ROOT)),sha256=digest(directory/'report.json')))
    print('Captured', len(data), 'contexts:', (directory/'report.json').relative_to(ROOT), flush=True)


if __name__=='__main__':
    main()
