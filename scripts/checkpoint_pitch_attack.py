#!/usr/bin/env python3
"""Validate and publish only the causal model-evidence checkpoint."""
import argparse
import ast
import json
import subprocess
from pathlib import Path
from checkpoint_attack_dictionary import check_admissions,signatures
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,digest

PATHS=['make/keyboard_attack.mk','make/pitch_attack_evidence.mk','docs/routing_duration_goal.md',
       'scripts/capture_pitch_attack_evidence.py','scripts/inspect_routing_replays.py',
       'scripts/test_pitch_attack_history.py','scripts/pitch_attack_queue.py',
       'scripts/screen_pitch_attack_evidence.py','scripts/screen_pitch_attack_ondemand.py',
       'scripts/screen_pitch_attack_prefetch.py','scripts/checkpoint_pitch_attack.py',
       'tests/pitch_attack_evidence.cpp','tests/pitch_attack_history_parity.cpp','tests/test_pitch_attack_queue.py',
       'scripts/replay_pitch_attack_envelope.py','scripts/score_pitch_attack_envelope.py','tests/pitch_attack_replay_support.hpp']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    audit=read(ROOT/'build/keyboard_confirmation_audit.json')
    pointer=read(ROOT/'build/pitch_attack_evidence/current.json')
    evidence_path=ROOT/pointer['report']
    evidence=read(evidence_path)
    assert digest(evidence_path)==pointer['sha256'] and evidence['complete']
    for name,row in evidence['recordings'].items():
        assert row['captures']==1161
        assert digest(evidence_path.parent/(name+'.tsv'))==row['sha256']
    for directory in ('pitch_attack_model_screen','pitch_attack_ondemand_bound','pitch_attack_prefetch_screen'):
        report=read(ROOT/'build'/directory/'report.json')
        signatures(report['inputs'])
        for mode,records in report['results'].items():
            for name,row in records.items():
                check_admissions(name,row['accepted'],row['metrics'],row['timing'],audit)
                for cell in row['accepted']:
                    if directory=='pitch_attack_ondemand_bound':
                        assert cell['completed_sample']>cell['end_sample']
                    else:
                        assert cell['model_end_sample']<=cell['completed_sample']<=cell['end_sample']
                        assert cell['end_sample']-cell['model_end_sample']<=round(evidence['recordings'][name]['rate']*.15)
            if 'decisions' in report:
                decision=report['decisions'][mode]
                assert decision['attack_gain']==sum(r['timing']['matched_attacks']['after']-r['timing']['matched_attacks']['before'] for r in records.values())
                assert abs(decision['unsupported_seconds']-sum(r['metrics']['unsupported_seconds'] for r in records.values()))<1e-9
                assert decision['isolated_additions']==sum(r['timing']['isolated_additions'] for r in records.values())
        if directory=='pitch_attack_prefetch_screen':
            assert digest(ROOT/'build'/directory/'requests.json')==report['requests_sha256']
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    for target in ('test-pitch-attack-queue','test-pitch-attack-history','score-pitch-attack-envelope'):
        subprocess.run(['make',target],cwd=ROOT,check=True)
    pointer=read(ROOT/'build/pitch_attack_envelope_native/current.json')
    native=read((ROOT/pointer['report']).parent/'score.json')
    assert not native['passed'] and native['decision']=='reject_native_confirmation'
    assert abs(sum(r['deltas']['held_removed_seconds'] for r in native['results'].values())-.05)<1e-8
    for name in ('analyzer.cpp','analyzer.hpp'):
        assert git('show','HEAD:src/'+name)==git('show','e903cb7:src/'+name)
    print('Verified actual model evidence, completion-time guards, admission scores and unchanged production analyzer',flush=True)


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
    (ROOT/'build/pitch_attack_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Reject early native pitch confirmation after paired preservation regressions'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
