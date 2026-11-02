#!/usr/bin/env python3
"""Apply the unchanged context verifier to existing first-hit attack cases."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse
import json
from pathlib import Path
import numpy as np
from evaluate_guitar_duplicate_model import lower_probability
from evaluate_keyboard_confirmation import score_acceptances
from piano_context_features import features
from routing_duration_baseline import ROOT,atomic_json,digest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--joint',action='store_true')
    parser.add_argument('--empirical-cutoff',action='store_true')
    args=parser.parse_args()
    model_path=ROOT/'build/piano_context_model/3b35eca632935a8c/frozen.json'
    audit_path=ROOT/'build/keyboard_confirmation_audit.json'
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    model,audit,baseline=(json.loads(p.read_text()) for p in (model_path,audit_path,baseline_path))
    assert all(digest(ROOT/p)==h for p,h in audit['inputs'].items())
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (model_path,audit_path,baseline_path,Path(__file__))}
    threshold=model['negative_max']+.001 if args.empirical_cutoff else model['threshold']
    for helper in ('piano_context_features.py','evaluate_keyboard_confirmation.py','evaluate_guitar_duplicate_model.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    joint=None
    if args.joint:
        pointer=json.loads((ROOT/'build/joint_pitch/current.json').read_text())
        path=ROOT/pointer['report']
        assert digest(path)==pointer['sha256']
        captured=json.loads(path.read_text())
        assert captured['complete'] and captured['inputs']['audit_sha256']==digest(audit_path)
        inputs[str(path.relative_to(ROOT))]=digest(path)
        joint={(name,c['end_sample'],c['midi']):c for name,r in captured['recordings'].items() for c in r['cases']}
    recordings={}
    prefix='piano_context_'+('empirical_' if args.empirical_cutoff else '')+('joint_' if args.joint else '')+'attack_screen'
    directory=ROOT/'build'/prefix
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',dict(inputs=inputs,threshold=threshold,joint_floors=[.8,.3] if args.joint else None,
        cutoff_rule='Original fitting/calibration negative maximum + .001' if args.empirical_cutoff else 'Original frozen .99 cutoff'))
    for name,recording in audit['recordings'].items():
        assert name in ('training-1','training-2','training-3')
        raw=baseline_path.parent/(name+'.f32')
        assert digest(raw)==baseline['recordings'][name]['prefix_sha256']
        inputs[str(raw.relative_to(ROOT))]=digest(raw)
        rate=baseline['recordings'][name]['rate']
        count=round(rate*.1)
        audio=np.pad(np.fromfile(raw,dtype='<f4'),(count,0))
        accepted=[]
        probabilities=[]
        metric=dict(candidates=len(recording['cases']),accepted=0,held_recovery_seconds=0.,unsupported_added_seconds=0.)
        for case in recording['cases']:
            row=case['candidate']
            if row['mfcc_valid']!='1':
                continue
            endpoint=case['end_sample']
            vector=features(audio[endpoint:endpoint+count],rate,[float(row['mfcc'+str(i)]) for i in range(24)])
            probability=lower_probability(model['model'],vector)
            probabilities.append(dict(end_sample=endpoint,midi=case['midi'],probability=probability,held_seconds=case['held_seconds']))
            if probability<threshold:
                continue
            if joint is not None:
                cue=joint[name,endpoint,case['midi']]
                if cue['relative_activation']<.8 or cue['explained_projection']<.3:
                    continue
            metric['accepted']+=1
            metric['held_recovery_seconds']+=case['held_seconds']
            metric['unsupported_added_seconds']+=case['unsupported_seconds']
            accepted.append(dict(end_sample=endpoint,midi=case['midi'],probability=probability))
        timing=score_acceptances(name,accepted)
        recordings[name]=dict(metrics=metric,accepted=accepted,timing=timing,
                              maximum_probability=max(p['probability'] for p in probabilities),probabilities=probabilities)
        print(name,json.dumps({k:v for k,v in recordings[name].items() if k!='probabilities'}),flush=True)
    passed=sum(r['metrics']['held_recovery_seconds'] for r in recordings.values())>0 and all(
        r['metrics']['unsupported_added_seconds']<1e-8 and not r['timing']['isolated_additions'] and
        r['timing']['matched_attacks']['after']>=r['timing']['matched_attacks']['before'] for r in recordings.values())
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    atomic_json(directory/'report.json',dict(inputs=inputs,recordings=recordings,threshold=threshold,joint_floors=[.8,.3] if args.joint else None,
        decision='requires_native_confirmation_trial' if passed else 'reject',
        scope='Existing context model, training first-hit cases only. Original cutoff or predeclared negative-max formula, not a first-hit label search. No refitting, new calibration/held-out access, native change or promotion.'))


if __name__=='__main__':
    main()
