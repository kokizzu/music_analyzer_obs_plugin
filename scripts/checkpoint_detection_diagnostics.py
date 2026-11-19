#!/usr/bin/env python3
"""Verify and publish only tested detection diagnostics; no runtime promotion."""
import argparse
import ast
import json
import subprocess
from detection_validation_store import Store
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,digest

PATHS=['make/pitch_continuity_controls.mk','docs/routing_duration_goal.md',
    'scripts/note_onset_score.py','tests/test_note_onset_score.py',
    'scripts/detection_validation_store.py','tests/test_detection_validation_store.py',
    'scripts/screen_routing_onset_proposals.py','scripts/analyzer_diagnostic.py','tests/test_analyzer_diagnostic.py',
    'scripts/benchmark_detection_worker.py','tests/detection_worker_latency.cpp','scripts/checkpoint_detection_diagnostics.py']


def evidence(store,key):
    row=store.connection.execute('select payload from evidence where id=?',(key,)).fetchone()
    assert row,key+' missing'
    value=json.loads(store.get(row[0]))
    assert all(digest(ROOT/p)==h for p,h in value['inputs'].items())
    return value


def verify():
    identity()
    for target in ('test-note-onset-score','test-detection-validation-store','test-analyzer-diagnostic'):
        subprocess.run(['make',target],cwd=ROOT,check=True)
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    with Store() as store:
        screen=evidence(store,'routing-onset-screen');worker=evidence(store,'worker-latency')
    assert set(screen['recordings'])=={'training-1','training-2','training-3'}
    assert screen['routing_decision']==screen['onset_decision']=='reject_development'
    assert screen['recordings']['training-3']['routing']['unsupported_seconds_delta']>0
    assert worker['submitted']==worker['observed_results']==100 and worker['unobserved_or_replaced']==0
    assert worker['passed_worker_budget'] and worker['completion_p99_ms']<45 and worker['completion_max_ms']<50 and worker['submit_p99_ms']<1
    subprocess.run(['make','verify-pitch-controls'],cwd=ROOT,check=True)
    for name in ('analyzer.cpp','analyzer.hpp'):
        assert git('show','HEAD:src/'+name)==git('show','e903cb7:src/'+name)
    print('Verified: rejected admission proposals, passing worker budget, tested diagnostic storage/replay. No runtime promotion.',flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('verify','stage','publish'));args=parser.parse_args()
    verify()
    if args.mode=='verify':
        return
    _,remote,primary,tip=identity();assert git('rev-parse','HEAD').strip()==tip
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS),'Preserve unrelated staged work'
    git('add','--',*PATHS);git('diff','--cached','--check')
    patch=git('diff','--cached')
    with Store() as store:
        store.evidence('publication-review','diff',dict(paths=PATHS,head=tip,patch=patch))
    print(git('diff','--cached','--stat'),flush=True)
    if args.mode=='stage':
        return
    print(git('commit','-m','Add tested diagnostic replay and reject unsafe note admission proposals'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
