#!/usr/bin/env python3
"""Verify default-on native routing and publish only tested primary source blobs."""
import argparse
import ast
import csv
import hashlib
import json
import subprocess

from build_routing_consensus_trial import candidate_sources
from measure_routing_consensus import inspect_frames
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

BUILD = 'build/routing_consensus_trial/398797777fb6e1fa/build.json'
ROLLOUT = 'build/routing_consensus_rollout/682b938120772cd4/report.json'
EXTENSIONS = 'build/routing_consensus_extensions/3aa507e9ead66390'
PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md',
         'src/routing_duplicate_consensus.hpp', 'src/native_piano_consensus_hook.inc',
         'src/native_piano_consensus_cached_hook.inc', 'src/keyboard_alias_visibility_guard.inc',
         'tests/routing_duplicate_consensus.cpp', 'tests/routing_consensus_pair.cpp',
         'tests/routing_consensus_latency.cpp', 'tests/routing_cepstral_cache.cpp',
         'tests/keyboard_alias_visibility.cpp', 'tests/keyboard_alias_visibility_pair.cpp',
         'tests/routing_consensus_default.cpp', 'scripts/build_routing_consensus_trial.py',
         'scripts/measure_routing_consensus.py', 'scripts/validate_routing_consensus.py',
         'scripts/benchmark_routing_consensus.py', 'scripts/test_keyboard_alias_visibility.py',
         'scripts/build_keyboard_alias_trial.py', 'scripts/measure_keyboard_alias_trial.py',
         'scripts/prepare_routing_consensus_rollout.py', 'scripts/publish_native_routing_consensus.py']


def read(relative):
    return json.loads((ROOT / relative).read_text())


def verified_sources():
    build, rollout = read(BUILD), read(ROLLOUT)
    directory = (ROOT / BUILD).parent
    staged = (ROOT / ROLLOUT).parent
    assert digest(directory / 'pair') == build['binary_sha256']
    assert all(digest(ROOT / p) == checksum for p, checksum in build['inputs']['assets'].items())
    assert all(digest(ROOT / p) == checksum for p, checksum in build['inputs']['objects'].items())
    assert rollout['passed'] and rollout['windows'] == 1200
    assert rollout['inputs']['build_sha256'] == digest(ROOT / BUILD)
    assert rollout['inputs']['source_sha256'] == digest(ROOT / 'tests/routing_consensus_default.cpp')
    assert rollout['inputs']['script_sha256'] == digest(ROOT / 'scripts/prepare_routing_consensus_rollout.py')
    assert digest(staged / 'replay') == rollout['binary_sha256']
    assert digest(staged / 'default.tsv') == rollout['frames_sha256']
    cpp, header = candidate_sources(git('show', 'HEAD:src/analyzer.cpp'), git('show', 'HEAD:src/analyzer.hpp'))
    header = header.replace('\tbool native_piano_duplicate_consensus = false;', '\tbool native_piano_duplicate_consensus = true;', 1)
    assert cpp == (staged / 'src/analyzer.cpp').read_text()
    assert header == (staged / 'src/analyzer.hpp').read_text()
    assert hashlib.sha256(cpp.encode()).hexdigest() == rollout['cpp_sha256'] == build['cpp_sha256']
    assert hashlib.sha256(header.encode()).hexdigest() == rollout['hpp_sha256']
    assert 'experimental_keyboard_alias_visibility_guard' not in header
    return {'src/analyzer.cpp': cpp, 'src/analyzer.hpp': header}


def verify():
    identity()
    contents = verified_sources()
    baseline = read('build/routing_duration_baseline/f3c7f7a446eed267/report.json')
    source_reports = {
        'single': ROOT / 'build/routing_controls/84b9eb144888ea8d/report.json',
        'poly': ROOT / 'build/routing_polycontrols/8fc4e60bf6c3a79b/report.json',
        'music': ROOT / 'build/routing_guitarset_controls/9801a45ca6c823e8/report.json',
        'piano': ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'}
    references = {kind: (path, json.loads(path.read_text())) for kind, path in source_reports.items()}
    total_windows = 0
    for relative in ('build/routing_consensus_pair/e63350f9b5113f8b/report.json',
                     'build/routing_consensus_pair/31e4706686b5b160/report.json'):
        path, report = ROOT / relative, read(relative)
        assert report['complete'] and report['passed'] and report['inputs']['build_sha256'] == digest(ROOT / BUILD)
        assert report['inputs']['script_sha256'] == digest(ROOT / 'scripts/measure_routing_consensus.py')
        assert all(digest(ROOT / p) == value for p, value in report['inputs']['helpers'].items())
        assert all(digest(ROOT / p) == value for p, value in report['inputs']['sources'].items())
        for name, entry in report['recordings'].items():
            kind, identifier = name.split('-', 1)
            source_path, source = references[kind]
            sample = next((s for s in source['inputs'].get('selection', []) if s['id'] == identifier), None)
            rate = baseline['recordings'][identifier]['rate'] if kind == 'piano' else source['recordings'][identifier]['rate']
            actual = inspect_frames(path.parent / (name + '.tsv'), rate, sample, kind in ('poly', 'music'))
            assert all(actual[key] == entry[key] for key in actual)
            assert not actual['protected_guitar_changes'] and not actual['protected_voice_changes'] and not actual['after_ms']['deadline_misses']
            total_windows += actual['windows']
    plan = read(EXTENSIONS + '/plan.json')
    assert plan['build_sha256'] == digest(ROOT / BUILD)
    assert plan['script_sha256'] == digest(ROOT / 'scripts/validate_routing_consensus.py')
    assert plan['helper_sha256'] == digest(ROOT / 'scripts/measure_routing_consensus.py')
    assert all(digest(ROOT / p) == checksum for p, checksum in plan['provenance'].items())
    assert len(plan['cases']) == 260 and sum(sample['fresh'] for sample in plan['cases']) == 96
    seen = set()
    for shard in range(2):
        report = read(EXTENSIONS + '/report-' + str(shard) + '.json')
        assert report['complete'] and report['passed'] and report['inputs_sha256'] == digest(ROOT / EXTENSIONS / 'plan.json')
        assert set(report['recordings']) == {sample['id'] for sample in plan['cases'][shard::2]}
        for sample in plan['cases'][shard::2]:
            entry = report['recordings'][sample['id']]
            actual = inspect_frames(ROOT / EXTENSIONS / (sample['id'] + '.tsv'), entry['rate'], poly=sample['protect_guitar'])
            if sample['protect_voice']:
                actual['protected_voice_changes'] = actual['voice_removed']
            assert all(actual[key] == entry[key] for key in actual)
            assert not actual['protected_guitar_changes'] and not actual['protected_voice_changes'] and not actual['after_ms']['deadline_misses']
            raw = ROOT / EXTENSIONS / (sample['id'] + '.f32') if sample['fresh'] else ROOT / sample['raw']
            assert digest(raw) == entry['raw_sha256']
            if sample['fresh']:
                assert digest(ROOT / sample['audio']) == sample['audio_sha256']
            seen.add(sample['id'])
            total_windows += actual['windows']
    assert len(seen) == 260 and total_windows == 52594
    latency_path = ROOT / 'build/routing_consensus_latency/33f4c14f94b8e79e/report.json'
    latency = json.loads(latency_path.read_text())
    assert latency['complete'] and latency['passed'] and latency['inputs']['build_sha256'] == digest(ROOT / BUILD)
    assert latency['inputs']['source_sha256'] == digest(ROOT / 'tests/routing_consensus_latency.cpp')
    assert latency['inputs']['script_sha256'] == digest(ROOT / 'scripts/benchmark_routing_consensus.py')
    for index, entry in enumerate(latency['repetitions']):
        assert digest(latency_path.parent / ('pass-' + str(index) + '.tsv')) == entry['sha256']
    assert all(latency['metrics'][key] < value for key, value in latency['inputs']['gates'].items())
    duration = read('build/keyboard_alias_measurement/5bcd43eafc4fc573/report.json')
    assert duration['complete'] and not duration['passed']
    assert all(not row['deltas']['removed_cells'] and not row['deltas']['added_cells'] for row in duration['recordings'].values())
    assert duration['inputs']['script_sha256'] == digest(ROOT / 'scripts/measure_keyboard_alias_trial.py')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    print('Verified', total_windows, 'paired native endpoints, 96 fresh cases, default-on output parity and unchanged latency gates')
    return contents


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    contents = verify()
    if not args.publish:
        return
    _, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == tip and not git('diff', '--cached', '--name-only').strip()
    for target in ('test-native-routing-consensus', 'test-routing-cepstral-cache', 'test-routing-consensus',
                   'test-piano-guitar-verifier', 'test-routing-duration-score', 'test-analyzer-internal'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    contents.update({path: (ROOT / path).read_text() for path in PATHS})
    changed = {}
    for path, content in contents.items():
        tracked = git('ls-files', '--stage', '--', path).split()
        if tracked and git('show', 'HEAD:' + path) == content:
            continue
        changed[path] = content
        blob = git('hash-object', '-w', '--stdin', data=content).strip()
        git('update-index', '--add', '--cacheinfo', (tracked[0] if tracked else '100644') + ',' + blob + ',' + path)
    assert set(git('diff', '--cached', '--name-only').splitlines()) == set(changed)
    git('diff', '--cached', '--check')
    for path, content in changed.items():
        assert git('show', ':' + path) == content
    print(git('diff', '--cached', '--stat'))
    print(git('diff', '--cached', '--', 'src/analyzer.cpp', 'src/analyzer.hpp'))
    print(git('commit', '-m', 'Enable corroborated native Piano duplicate routing after disjoint validation'))
    print(git('push', remote, 'HEAD:' + primary))
    assert identity()[3] == git('rev-parse', 'HEAD').strip()
    assert git('show', 'HEAD:src/analyzer.cpp') == contents['src/analyzer.cpp']
    assert git('show', 'HEAD:src/analyzer.hpp') == contents['src/analyzer.hpp']
    print('Published primary', git('rev-parse', '--short', 'HEAD').strip())


if __name__ == '__main__':
    main()
