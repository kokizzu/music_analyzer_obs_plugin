#!/usr/bin/env python3
"""Verify and publish the frozen calibration result without runtime promotion."""
import argparse
import ast
import json
import subprocess
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,digest
from validate_pitch_continuity_calibration import load

PATHS=['make/pitch_attack_evidence.mk','make/pitch_continuity_validation.mk','docs/routing_duration_goal.md',
       'scripts/validate_pitch_continuity_calibration.py','scripts/checkpoint_pitch_calibration.py','scripts/inspect_routing_replays.py']


def read(path):
    return json.loads(path.read_text())


def verify():
    identity()
    directory,plan=load()
    development=read((ROOT/plan['native_build']).parent/'evidence.json')
    for fixed in ('build/piano_context_model/3b35eca632935a8c/frozen.json',
                  'build/real_piano_dictionary_transfer/cfb32e5534dc943f/dictionary.npz'):
        assert plan['inputs'][fixed]==development['inputs'][fixed]
    old_capture=read(ROOT/'build/pitch_attack_evidence/c2298a7181c716c3/report.json')
    assert old_capture['inputs']['build_sha256']==plan['inputs'][plan['model_build']]
    original_support=digest(directory/'support.json')
    subprocess.run(['make','prepare-pitch-continuity-calibration'],cwd=ROOT,check=True)
    assert digest(directory/'support.json')==original_support
    subprocess.run(['make','score-pitch-continuity-calibration'],cwd=ROOT,check=True)
    result=read(directory/'score.json')
    assert result['passed'] and result['decision']=='requires_fresh_heldout_and_live_worker'
    assert len(result['additions'])==1 and not result['removals']
    added=result['additions'][0]
    assert (added['end_sample'],added['midi'])==(1752975,53)
    assert abs(added['held_seconds']-.05)<1e-8 and not added['unsupported_seconds'] and not added['isolated']
    assert result['before']['matched_attacks']==result['after']['matched_attacks']==123
    assert abs(result['before']['onset_gap_seconds']-result['after']['onset_gap_seconds']-.05)<1e-8
    for metric in ('removed_cells','supported_removed_seconds','unsupported_added_seconds','isolated_additions',
                   'unrelated_changed_frames','tempo_changed_frames','surviving_cell_changed_frames'):
        assert abs(result['deltas'][metric])<1e-8
    assert plan['sample']['id']=='training-4' and plan['display_hops']==3
    assert (plan['relative_floor'],plan['explained_floor'],plan['note_floor'],plan['maximum_request_age_seconds'])==(.8,.3,.3,.15)
    capture=read(directory/'capture.json')
    assert capture['captures']==1161 and digest(directory/'model.tsv')==capture['sha256']
    for name in ('analyzer.cpp','analyzer.hpp'):
        assert git('show','HEAD:src/'+name)==git('show','e903cb7:src/'+name)
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    print('Verified frozen separate calibration, repeatable causal support, 1200 exact primary endpoints and 50 ms onset-gap recovery; no held-out/live-worker/promotion claim',flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');parser.add_argument('--publish',action='store_true')
    args=parser.parse_args();verify()
    if not(args.stage or args.publish):
        return
    _,remote,primary,tip=identity()
    assert git('rev-parse','HEAD').strip()==tip
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS)
    git('add','--',*PATHS);git('diff','--cached','--check')
    (ROOT/'build/pitch_calibration_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Validate frozen piano attack continuity on a separate calibration recording'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
