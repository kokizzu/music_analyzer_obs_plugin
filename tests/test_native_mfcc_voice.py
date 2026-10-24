#!/usr/bin/env python3
"""Check frozen vectors and optional full capture against native inference."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from evaluate_native_mfcc_voice import transformed, lower_probability

source = ROOT / 'models/native_mfcc_voice.json'
state = json.loads(source.read_text())
golden = json.loads((ROOT / 'tests/native_mfcc_voice_vectors.json').read_text())
assert golden['model_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
vectors = golden['vectors']
if '--full' in sys.argv:
    capture = next(ROOT / p for p in state['inputs'] if p.endswith('candidates.tsv'))
    assert hashlib.sha256(capture.read_bytes()).hexdigest() == state['inputs'][str(capture.relative_to(ROOT))]
    with capture.open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            if row['mfcc_valid'] == '1':
                vectors.append(dict(raw=[float(row[key]) for key in state['features']],
                                    score=lower_probability(state['model'], transformed(row, state['features']))))
directory = ROOT / 'build/native_mfcc_voice_parity'
directory.mkdir(exist_ok=True)
input_path, output_path = directory / 'input.tsv', directory / 'output.tsv'
input_path.write_text(''.join('\t'.join(map(repr, row['raw'])) + '\n' for row in vectors))
subprocess.run([str(ROOT / 'build/native_mfcc_voice'), str(input_path), str(output_path)], check=True)
scores = list(map(float, output_path.read_text().splitlines()))
assert len(scores) == len(vectors)
for actual, row in zip(scores, vectors):
    assert abs(actual - row['score']) < 1e-12
    assert (actual >= state['threshold']) == (row['score'] >= state['threshold'])
    if row.get('protected'):
        assert actual < state['threshold']
assert sum(row.get('protected', False) for row in vectors) == 8
assert any(value >= state['threshold'] for value in scores)
assert any(value < state['threshold'] for value in scores)
print('Native spectral verifier:', len(scores), 'parity cases passed')
