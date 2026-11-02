#!/usr/bin/env python3
"""Capture all observed protected-row failures, without altering model cutoffs."""
import csv
import json
from pathlib import Path
import subprocess

from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    exporter_directory = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7'
    exporter_report = json.loads((exporter_directory / 'report.json').read_text())
    binary = exporter_directory / 'replay'
    assert digest(binary) == exporter_report['binary_sha256']
    directory = ROOT / 'build/routing_regression_evidence'
    directory.mkdir(parents=True, exist_ok=True)
    results = {}
    reports = [ROOT / 'build/piano_guitar_extensions/93a449f0b4f656bd/report.json']
    reports += list((ROOT / 'build/piano_voice_extensions').glob('*/report.json'))
    for report_path in reports:
        report = json.loads(report_path.read_text())
        for name, entry in report['recordings'].items():
            if not entry.get('protected_voice_losses', entry.get('correct_or_protected_losses', 0)):
                continue
            source = report_path.parent / (name + '.tsv')
            assert digest(source) == entry['sha256']
            with source.open() as stream:
                expected = {row['end_sample']: row for row in csv.DictReader(stream, delimiter='\t')}
            if 'piano_voice_extensions' in str(report_path):
                raw = report_path.parent / (name + '.f32')
            else:
                suffix = '.derived.f32' if name.endswith('-48k') else '.original.f32'
                raw = report_path.parent / (name + suffix)
            destination = directory / (name + '.tsv')
            subprocess.run([str(binary), str(raw), str(entry['rate']), str(destination)], check=True, timeout=1800)
            seen = set()
            with destination.open() as stream:
                for row in csv.DictReader(stream, delimiter='\t'):
                    endpoint = row['end_sample']
                    assert all(row[key] == expected[endpoint][key] for key in ('bass', 'guitar', 'keys', 'voice', 'other', 'ambiguous', 'chord', 'bpm', 'confidence', 'drums'))
                    seen.add(endpoint)
            assert seen == set(expected)
            results[name] = dict(sha256=digest(destination), source_sha256=digest(source), report_sha256=digest(report_path),
                                 raw_sha256=digest(raw), rate=entry['rate'], windows=len(seen))
            print(name, len(seen), 'windows; exact disabled-native parity', flush=True)
    atomic_json(directory / 'report.json', dict(exporter_sha256=digest(binary), script_sha256=digest(Path(__file__)), recordings=results,
                scope='Diagnostic capture of every currently observed protected-row failure; no model/threshold fitting or promotion'))


if __name__ == '__main__':
    main()
