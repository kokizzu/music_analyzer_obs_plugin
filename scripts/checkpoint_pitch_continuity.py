#!/usr/bin/env python3
"""Verify and publish the bounded-continuity development checkpoint."""
import argparse
import ast
import csv
import json
import subprocess
from pathlib import Path
from audit_keyboard_recovery import coverage
from evaluate_keyboard_confirmation import score_acceptances
from midi_sustain_reference import read_intervals
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,digest
from routing_duration_score import merge

PATHS=['make/pitch_attack_evidence.mk','docs/routing_duration_goal.md','scripts/inspect_routing_replays.py',
       'scripts/pitch_attack_continuity.py','scripts/screen_pitch_attack_continuity.py','tests/test_pitch_attack_continuity.py',
       'src/piano_attack_continuity.hpp','tests/piano_attack_continuity.cpp','scripts/test_piano_attack_display.py',
       'scripts/replay_pitch_attack_continuity.py','scripts/score_pitch_attack_envelope.py','scripts/checkpoint_pitch_continuity.py']


def read(path):
    return json.loads(path.read_text())


def signatures(inputs):
    assert all(digest(ROOT/p)==h for p,h in inputs.items())


def verify():
    identity()
    directory=ROOT/'build/pitch_attack_continuity_screen'
    report=read(directory/'report.json')
    signatures(report['inputs'])
    assert digest(directory/'schedules.json')==report['schedules_sha256']
    schedules=read(directory/'schedules.json')
    signatures(schedules['inputs'])
    support=read(directory/'native-support.json')
    signatures(support['inputs'])
    audit=read(directory/'interruptions.json')
    signatures(audit['inputs'])
    interruptions=[row['frames'][1] for rows in audit['recordings'].values() for row in rows]
    assert all(row['neural_pass'] for row in interruptions)
    assert sum(not r['pitch_pass'] for r in interruptions)==2
    assert sum(not r['context_pass'] for r in interruptions)==1
    baseline=read(ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json')
    for policy,records in report['results'].items():
        assert sum(r['metrics']['cells'] for r in records.values())==(8 if policy=='seed_context_latch' else 6)
        assert sum(r['timing']['isolated_additions'] for r in records.values())==(0 if policy=='seed_context_latch' else 2)
        for name,row in records.items():
            assert schedules['results'][name][policy]['accepted']==row['accepted']
            assert score_acceptances(name,row['accepted'])==row['timing']
            rate=baseline['recordings'][name]['rate']
            sample=next(s for s in baseline['selection'] if s['id']==name)
            midi=ROOT/sample['midi']
            assert digest(midi)==sample['midi_sha256']
            held={};allowed={}
            for note in read_intervals(midi.read_bytes()):
                if note['channel']!=9:
                    held.setdefault(note['midi'],[]).append((note['start'],note['key_end']))
                    allowed.setdefault(note['midi'],[]).append((note['start'],note['end']+.3))
            held={m:merge(v) for m,v in held.items()};allowed={m:merge(v) for m,v in allowed.items()}
            actual_held=actual_wrong=0.
            for c in row['accepted']:
                assert c['model_end_sample']<=c['completed_sample']<=c['end_sample']
                assert c['end_sample']-c['model_end_sample']<=round(rate*.15)
                assert 0<=c['end_sample']-c['born_sample']<round(rate*.15)
                start=c['end_sample']/rate;end=min(60.,start+.05)
                actual_held+=coverage(held.get(c['midi'],[]),start,end)
                actual_wrong+=end-start-coverage(allowed.get(c['midi'],[]),start,end)
            assert abs(actual_held-row['metrics']['held_seconds'])<1e-8
            assert abs(actual_wrong-row['metrics']['unsupported_seconds'])<1e-8
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    for target in ('test-pitch-attack-continuity','test-native-piano-attack-continuity','test-piano-attack-display','test-pitch-attack-queue',
                   'score-pitch-attack-continuity'):
        subprocess.run(['make',target],cwd=ROOT,check=True)
    pointer=read(ROOT/'build/pitch_attack_continuity_native/current.json')
    native_directory=(ROOT/pointer['report']).parent
    native=read(native_directory/'score.json')
    assert native['passed'] and native['benefit'] and native['decision']=='requires_live_worker_validation'
    for name,row in native['results'].items():
        expected={(c['end_sample'],c['midi']) for c in report['results']['seed_context_latch'][name]['accepted']}
        actual={(c['end_sample'],c['midi']) for c in row['additions']}
        assert actual==expected and not row['removals']
        assert row['after']['matched_attacks']-row['before']['matched_attacks']==1
        for key in ('held_removed_seconds','supported_removed_seconds','unsupported_added_seconds','isolated_additions',
                    'unrelated_changed_frames','tempo_changed_frames','surviving_cell_changed_frames'):
            assert abs(row['deltas'][key])<1e-8
    for name in ('analyzer.cpp','analyzer.hpp'):
        assert git('show','HEAD:src/'+name)==git('show','e903cb7:src/'+name)
    print('Verified causal continuity screens, exact native additions and preserved primary analyzer; live-worker/calibration/held-out/latency qualification remains',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',action='store_true')
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    verify()
    if not(args.stage or args.publish):
        return
    _,remote,primary,tip=identity()
    assert git('rev-parse','HEAD').strip()==tip
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS)
    git('add','--',*PATHS)
    git('diff','--cached','--check')
    (ROOT/'build/pitch_continuity_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Add bounded piano attack display continuity with native development preservation'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
