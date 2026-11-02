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


def main():
    branch, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == tip
    assert not git('diff', '--cached', '--name-only').strip(), 'Preserve staged work'
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    subprocess.run(['make', 'test-routing-duration-score'], cwd=ROOT, check=True)
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
    include = 'include make/routing_duration.mk\n'
    base = git('show', 'HEAD:Makefile')
    contents = {p: (ROOT / p).read_text() for p in PATHS}
    contents['Makefile'] = base if include in base else base + include
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
    print(git('commit', '-m', 'Establish primary routing and causal note-duration baselines'))
    print(git('push', remote, 'HEAD:' + primary))
    assert identity()[3] == git('rev-parse', 'HEAD').strip()
    print('Published', git('rev-parse', '--short', 'HEAD').strip())


if __name__ == '__main__':
    main()
