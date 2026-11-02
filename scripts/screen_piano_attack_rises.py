#!/usr/bin/env python3
"""Test a fixed causal activation rise using the twenty-performance dictionary."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json
from pathlib import Path
import numpy as np
from evaluate_keyboard_confirmation import score_acceptances
from joint_pitch_reference import fit
from routing_duration_baseline import ROOT,atomic_json,digest
from transfer_real_piano_dictionary import observations


def rising(activation,index,midi):
    return index>=3 and activation[midi-21,index]>=2*max(1e-12,float(activation[midi-21,index-3:index].max()))


def main():
    pointer=json.loads((ROOT/'build/real_piano_dictionary_transfer/current.json').read_text())
    path=ROOT/pointer['report']
    parent=json.loads(path.read_text())
    assert digest(path)==pointer['sha256'] and parent['complete']
    model_path=path.parent/'dictionary.npz'
    assert digest(model_path)==parent['dictionary_sha256']
    matrix=np.load(model_path)['dictionary']
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    audit_path=ROOT/'build/keyboard_confirmation_audit.json'
    context_path=ROOT/'build/piano_context_empirical_joint_attack_screen/report.json'
    baseline,audit,context=(json.loads(p.read_text()) for p in (baseline_path,audit_path,context_path))
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (path,model_path,baseline_path,audit_path,context_path,Path(__file__))}
    for helper in ('transfer_real_piano_dictionary.py','joint_pitch_reference.py','evaluate_keyboard_confirmation.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    directory=ROOT/'build/piano_attack_rise_screen'
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',dict(inputs=inputs,ratio=2,previous_hops=3,relative_floor=.8,explained_floor=.3,context_threshold=context['threshold']))
    results={}
    for name in ('training-1','training-2','training-3'):
        raw=baseline_path.parent/(name+'.f32')
        assert digest(raw)==baseline['recordings'][name]['prefix_sha256']
        rate=baseline['recordings'][name]['rate']
        observed=observations(np.fromfile(raw,dtype='<f4').astype(float),rate)
        activation=fit(matrix,observed)
        projection=matrix.T@observed
        relative=activation/np.maximum(activation.max(axis=0),1e-12)
        explained=activation/np.maximum(projection,1e-12)
        base={(c['end_sample'],c['midi']) for c in parent['results'][name]['accepted']}
        accepted=[]
        metrics=dict(cells=0,held_seconds=0.,unsupported_seconds=0.)
        for case in audit['recordings'][name]['cases']:
            endpoint,midi=case['end_sample'],case['midi']
            if (endpoint,midi) not in base:
                continue
            index=endpoint//round(rate*.05)-1
            assert relative[midi-21,index]>=.8 and explained[midi-21,index]>=.3
            if not rising(activation,index,midi):
                continue
            accepted.append(dict(end_sample=endpoint,midi=midi))
            metrics['cells']+=1
            metrics['held_seconds']+=case['held_seconds']
            metrics['unsupported_seconds']+=case['unsupported_seconds']
        timing=score_acceptances(name,accepted)
        results[name]=dict(metrics=metrics,accepted=accepted,timing=timing)
        print(name,json.dumps(results[name]),flush=True)
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    safe=all(r['metrics']['unsupported_seconds']<1e-8 and r['timing']['matched_attacks']['after']>=r['timing']['matched_attacks']['before'] for r in results.values())
    gain=sum(r['timing']['matched_attacks']['after']-r['timing']['matched_attacks']['before'] for r in results.values())
    atomic_json(directory/'report.json',dict(inputs=inputs,results=results,attack_gain=gain,
        decision='investigate_native_confirmation_envelope' if safe and gain>0 else 'reject',
        scope='Training-development assay only. Fixed doubling relative to the preceding three causal joint activations. Single-hop display additions do not simulate native confirmation envelopes; isolated additions remain reported, not waived as a production gate. No calibration, new held-out access or native changes.'))


if __name__=='__main__':
    main()
