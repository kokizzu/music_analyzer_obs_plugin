#!/usr/bin/env python3
"""Leave-recording-out pitch dictionary adaptation, with frozen family cues."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from capture_joint_note_coverage import causal_windows
from evaluate_keyboard_confirmation import score_acceptances
from joint_pitch_reference import spectrum,fit
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT,atomic_json,digest
from supervised_piano_dictionary import learn_dictionary


def main():
    os.nice(10)
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    prior_path=ROOT/'build/joint_pitch/143d517357f2b5c2/dictionary.json'
    audit_path=ROOT/'build/keyboard_confirmation_audit.json'
    context_path=ROOT/'build/piano_context_empirical_joint_attack_screen/report.json'
    baseline,prior,audit,context=(json.loads(p.read_text()) for p in (baseline_path,prior_path,audit_path,context_path))
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (baseline_path,prior_path,audit_path,context_path,Path(__file__))}
    for helper in ('supervised_piano_dictionary.py','joint_pitch_reference.py','capture_joint_note_coverage.py',
                   'midi_sustain_reference.py','evaluate_keyboard_confirmation.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    assert all(digest(ROOT/p)==h for p,h in audit['inputs'].items())
    assert all(digest(ROOT/p)==h for p,h in context['inputs'].items())
    matrix=np.array(prior['columns']).T
    assert matrix.shape==(2049,88)
    observed,masks={},{}
    for name in ('training-1','training-2','training-3'):
        raw=baseline_path.parent/(name+'.f32')
        assert digest(raw)==baseline['recordings'][name]['prefix_sha256']
        sample=next(s for s in baseline['selection'] if s['id']==name)
        midi=ROOT/sample['midi']
        assert digest(midi)==sample['midi_sha256']
        for p in (raw,midi):
            inputs[str(p.relative_to(ROOT))]=digest(p)
        rate=baseline['recordings'][name]['rate']
        audio=np.fromfile(raw,dtype='<f4').astype(float)
        values=spectrum(causal_windows(audio,rate)).T
        values/=np.maximum(np.linalg.norm(values,axis=0),1e-12)
        observed[name]=values
        times=np.arange(1,values.shape[1]+1)*round(rate*.05)/rate
        mask=np.zeros((88,len(times)),dtype=bool)
        for note in read_intervals(midi.read_bytes()):
            if note['channel']!=9 and 21<=note['midi']<=108:
                mask[note['midi']-21]|=(times>note['start'])&(times-.1<note['end']+.3)
        masks[name]=mask
    protocol=dict(inputs=inputs,epochs=40,activation_updates=4,ridge=1.,inference_updates=80,
                  context_threshold=context['threshold'],joint_floors=[.8,.3],
                  split='Fit spectral bases on two complete training recordings; infer on the third without MIDI masks',
                  limitation='The unchanged family classifier was previously fitted on all three performances. This is a training-only pitch-dictionary cross-validation, not whole-pipeline held-out proof.')
    directory=ROOT/'build/supervised_piano_attack_screen'/hashlib.sha256(json.dumps(protocol,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',protocol)
    report=dict(protocol=protocol,folds={},complete=False)
    for held in observed:
        fitting=sorted(set(observed)-{held})
        assert held not in fitting and len(fitting)==2
        x=np.concatenate([observed[n] for n in fitting],axis=1)
        mask=np.concatenate([masks[n] for n in fitting],axis=1)
        nonempty=mask.any(axis=0)
        learned=learn_dictionary(matrix,x[:,nonempty],mask[:,nonempty])
        model_path=directory/(held+'-dictionary.npz')
        np.savez(model_path,dictionary=learned)
        frozen=dict(fitting_recordings=fitting,rows=int(nonempty.sum()),dictionary_sha256=digest(model_path),
                    plan_sha256=digest(directory/'plan.json'))
        atomic_json(directory/(held+'-frozen.json'),frozen)
        # No MIDI mask, expected pitch, velocity or future audio is supplied to
        # inference. All 88 pitch components compete jointly as in the old fit.
        activation=fit(learned,observed[held])
        projection=learned.T@observed[held]
        relative=activation/np.maximum(activation.max(axis=0),1e-12)
        explained=activation/np.maximum(projection,1e-12)
        probabilities={(p['end_sample'],p['midi']):p['probability'] for p in context['recordings'][held]['probabilities']}
        rate=baseline['recordings'][held]['rate']
        hop=round(rate*.05)
        accepted=[]
        metrics=dict(cells=0,held_seconds=0.,unsupported_seconds=0.)
        for case in audit['recordings'][held]['cases']:
            endpoint,midi=case['end_sample'],case['midi']
            if probabilities.get((endpoint,midi),0.)<context['threshold']:
                continue
            index=endpoint//hop-1
            if relative[midi-21,index]<.8 or explained[midi-21,index]<.3:
                continue
            accepted.append(dict(end_sample=endpoint,midi=midi))
            metrics['cells']+=1
            metrics['held_seconds']+=case['held_seconds']
            metrics['unsupported_seconds']+=case['unsupported_seconds']
        timing=score_acceptances(held,accepted)
        report['folds'][held]=dict(frozen=frozen,metrics=metrics,accepted=accepted,timing=timing)
        atomic_json(directory/'report.json',report)
        print(held,json.dumps({k:v for k,v in report['folds'][held].items() if k!='accepted'}),flush=True)
    passed=sum(f['metrics']['held_seconds'] for f in report['folds'].values())>0 and all(
        f['metrics']['unsupported_seconds']<1e-8 and not f['timing']['isolated_additions'] and
        f['timing']['matched_attacks']['after']>=f['timing']['matched_attacks']['before'] for f in report['folds'].values())
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    report.update(complete=True,decision='requires_independent_native_calibration' if passed else 'reject')
    atomic_json(directory/'report.json',report)
    atomic_json(directory.parent/'current.json',dict(report=str((directory/'report.json').relative_to(ROOT)),sha256=digest(directory/'report.json')))
    print('Supervised dictionary screen:',report['decision'],flush=True)


if __name__=='__main__':
    main()
