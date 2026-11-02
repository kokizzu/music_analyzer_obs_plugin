import csv
import json
from itertools import groupby
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from evaluate_guitar_duplicate_model import FEATURES, eligible, features, lower_probability
from evaluate_guitar_music_model import frame_context
from routing_duration_baseline import digest

model_path = ROOT / 'models/piano_guitar_verifier.json'
state = json.loads(model_path.read_text())
vectors = json.loads((ROOT / 'tests/piano_guitar_vectors.json').read_text())
assert vectors['model_sha256'] == digest(model_path)
assert digest(model_path) in (ROOT / 'src/piano_guitar_model_data.hpp').read_text()
cases = list(vectors['cases'])
if '--full' in sys.argv:
    for path, checksum in state['inputs'].items():
        if not path.endswith('.tsv'):
            continue
        assert digest(ROOT / path) == checksum
        with (ROOT / path).open() as stream:
            for _, frame in groupby(csv.DictReader(stream, delimiter='\t'), key=lambda row: row['end_sample']):
                rows = list(frame)
                context = frame_context(rows)
                for row in rows:
                    if eligible(row):
                        cases.append(dict(raw=[float(row[name]) for name in FEATURES] + context,
                                          probability=lower_probability(state['model'], features(row) + context)))
directory = ROOT / 'build/piano_guitar_verifier_parity'
directory.mkdir(exist_ok=True)
input_path, output_path = directory / 'input.tsv', directory / 'output.tsv'
expected = []
lines = []
for case in cases:
    for profile in (0, 1):
        lines.append('\t'.join(map(repr, case['raw'] + [profile])) + '\n')
        expected.append((case['probability'], not profile and case['probability'] >= state['threshold']))
input_path.write_text(''.join(lines))
subprocess.run([str(ROOT / 'build/piano_guitar_verifier'), str(input_path), str(output_path)], check=True)
actual = output_path.read_text().splitlines()
assert len(actual) == len(expected)
for line, (probability, remove) in zip(actual, expected):
    value, decision = line.split('\t')
    assert abs(float(value) - probability) < 1e-12
    assert bool(int(decision)) == remove
assert any(remove for probability, remove in expected)
print('Native Guitar duplicate verifier:', len(expected), 'probability/profile parity cases passed')
