#!/usr/bin/env python3
"""Publish explicit, validated routing/duration goal checkpoints on primary."""
import ast
import json
from pathlib import Path
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, digest

PATHS = ['make/routing_duration.mk', 'docs/routing_duration_goal.md',
         'scripts/routing_duration_score.py', 'scripts/routing_duration_baseline.py',
         'scripts/capture_routing_candidates.py', 'scripts/manage_routing_duration_goal.py',
         'tests/test_routing_duration_score.py', 'tests/routing_candidate_replay.cpp']
PATHS += ['scripts/capture_routing_controls.py', 'scripts/capture_routing_polycontrols.py',
          'scripts/capture_routing_guitarset.py', 'scripts/routing_alignment.py',
          'scripts/audit_routing_alignment.py', 'tests/test_routing_alignment.py',
          'scripts/evaluate_guitar_duplicate_model.py', 'scripts/evaluate_guitar_context_veto.py',
          'scripts/evaluate_guitar_music_model.py', 'scripts/export_piano_guitar_model.py',
          'scripts/build_piano_guitar_trial.py', 'scripts/measure_piano_guitar_trial.py',
          'src/piano_guitar_features.hpp', 'src/piano_guitar_verifier.hpp', 'src/piano_guitar_model_data.hpp',
          'src/experimental_piano_guitar_hook.inc', 'models/piano_guitar_verifier.json',
          'tests/piano_guitar_vectors.json', 'tests/piano_guitar_verifier.cpp',
          'tests/test_piano_guitar_verifier.py', 'tests/piano_guitar_pair.cpp', 'tests/test_guitar_music_context.py']


def main():
    branch, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == tip
    assert not git('diff', '--cached', '--name-only').strip(), 'Preserve staged work'
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    for target in ('test-routing-duration-score', 'test-routing-alignment', 'test-guitar-music-context',
                   'test-piano-guitar-verifier', 'test-measure-analyzer-patterns-target', 'test-analyzer-internal'):
        subprocess.run(['make', target], cwd=ROOT, check=True)
    # Confirm the checkpoint cited in the report is complete, not an old local
    # engine run. Source-tree identity permits reuse across docs-only commits.
    baseline_path = ROOT / 'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline = json.loads(baseline_path.read_text())
    assert baseline['complete'] and len(baseline['recordings']) == 8
    build = baseline['build']
    assert build['inputs']['source_tree'] == git('rev-parse', 'HEAD:src').strip()
    assert build['inputs']['vendor_tree'] == git('rev-parse', 'HEAD:third_party').strip()
    directory = ROOT / baseline['build_directory']
    assert digest(directory / 'replay') == build['binary_sha256']
    assert all(digest(ROOT / p) == value for p, value in baseline['inputs'].items())
    for name, recording in baseline['recordings'].items():
        assert digest(baseline_path.parent / (name + '.tsv')) == recording['frames_sha256']
    evidence_path = ROOT / 'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    evidence = json.loads(evidence_path.read_text())
    assert evidence['complete'] and len(evidence['recordings']) == 8
    assert evidence['inputs']['baseline_sha256'] == digest(baseline_path)
    assert evidence['inputs']['source_sha256'] == digest(ROOT / 'tests/routing_candidate_replay.cpp')
    assert evidence['inputs']['script_sha256'] == digest(ROOT / 'scripts/capture_routing_candidates.py')
    for name, recording in evidence['recordings'].items():
        assert digest(evidence_path.parent / (name + '.tsv')) == recording['sha256']
        assert recording['windows'] == 1200
    native_build_path = ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38/build.json'
    native_build = json.loads(native_build_path.read_text())
    native_directory = native_build_path.parent
    assert digest(native_directory / 'pair') == native_build['binary_sha256']
    assert all(digest(ROOT / p) == checksum for p, checksum in native_build['inputs']['assets'].items())
    for relative in ('build/piano_guitar_pair/67994976db4bc16f/report.json', 'build/piano_guitar_pair/6d370d0731dc86a1/report.json'):
        result_path = ROOT / relative
        result = json.loads(result_path.read_text())
        assert result['complete'] and result['passed']
        assert result['inputs']['build_sha256'] == digest(native_build_path)
        assert result['inputs']['model_sha256'] == digest(ROOT / 'models/piano_guitar_verifier.json')
        assert all(not entry['correct_guitar_losses'] and not entry['protected_guitar_row_changes'] and not entry['after_ms']['deadline_misses'] for entry in result['recordings'].values())
        assert all(digest(result_path.parent / (name + '.tsv')) == entry['sha256'] for name, entry in result['recordings'].items())
    include = 'include make/routing_duration.mk\n'
    base = git('show', 'HEAD:Makefile')
    contents = {p: (ROOT / p).read_text() for p in PATHS}
    contents['Makefile'] = base if include in base else base + include
    # Publish only the tested hook on primary source, preserving older dirty
    # worktree changes. The candidate flag remains false, pending broader gates.
    original = git('show', 'HEAD:src/analyzer.cpp')
    header = git('show', 'HEAD:src/analyzer.hpp')
    if 'experimental_piano_guitar_filter' not in header:
        expected_cpp = original.replace('#include "analyzer.hpp"', '#include "analyzer.hpp"\n#include "piano_guitar_features.hpp"', 1)
        anchor = '\n\t// Keep the expensive high-tempo hypothesis outside the phase path.'
        assert expected_cpp.count(anchor) == 1
        expected_cpp = expected_cpp.replace(anchor, '\n' + (ROOT / 'src/experimental_piano_guitar_hook.inc').read_text() + anchor, 1)
        expected_header = header.replace('\tint tempo_debug_probe_bpm = 0;', '\tint tempo_debug_probe_bpm = 0;\n\tbool experimental_piano_guitar_filter = false;', 1)
        assert (native_directory / 'src/analyzer.cpp').read_text() == expected_cpp
        assert (native_directory / 'src/analyzer.hpp').read_text() == expected_header
        assert digest(native_directory / 'src/analyzer.cpp') == native_build['cpp_sha256']
        assert digest(native_directory / 'src/analyzer.hpp') == native_build['hpp_sha256']
        contents['src/analyzer.cpp'] = expected_cpp
        contents['src/analyzer.hpp'] = expected_header
    changed = {}
    for p, content in contents.items():
        tracked = git('ls-files', '--stage', '--', p).split()
        if tracked and git('show', 'HEAD:' + p) == content:
            continue
        changed[p] = content
        mode = tracked[0] if tracked else '100644'
        blob = git('hash-object', '-w', '--stdin', data=content).strip()
        git('update-index', '--add', '--cacheinfo', mode + ',' + blob + ',' + p)
    assert set(git('diff', '--cached', '--name-only').splitlines()) == set(changed)
    git('diff', '--cached', '--check')
    for p, content in changed.items():
        assert git('show', ':' + p) == content
    print(git('diff', '--cached', '--stat'))
    print(git('commit', '-m', 'Add validated experimental native Piano/Guitar duplicate verifier'))
    print(git('push', remote, 'HEAD:' + primary))
    assert identity()[3] == git('rev-parse', 'HEAD').strip()
    print('Published', git('rev-parse', '--short', 'HEAD').strip())


if __name__ == '__main__':
    main()
