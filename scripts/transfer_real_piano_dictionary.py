#!/usr/bin/env python3
"""Fit on twenty additional performances before any new calibration access."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import csv
import fcntl
import hashlib
import json
from pathlib import Path
import wave
import numpy as np
from capture_joint_note_coverage import causal_windows
from evaluate_keyboard_confirmation import score_acceptances
from joint_pitch_reference import spectrum,fit
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT,atomic_json,digest
from supervised_piano_dictionary import learn_dictionary


def read(path):
    return json.loads(path.read_text())


def label_mask(notes,times):
    mask=np.zeros((88,len(times)),dtype=bool)
    for note in notes:
        if note['channel']!=9 and 21<=note['midi']<=108:
            mask[note['midi']-21]|=(times>note['start'])&(times-.1<note['end']+.3)
    return mask


def observations(audio,rate):
    values=spectrum(causal_windows(audio,rate)).T
    return values/np.maximum(np.linalg.norm(values,axis=0),1e-12)


def main():
    os.nice(10)
    base=ROOT/'build/maestro_real_samples'
    manifest=base/'maestro-v3.0.0.csv'
    with manifest.open() as stream:
        rows=list(csv.DictReader(stream))
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline=read(baseline_path)
    previous_audio={digest(base/r['audio_filename']) for r in rows[:24]}
    previous_midi={digest(base/r['midi_filename']) for r in rows[:24]}
    previous_audio.update(s['audio_sha256'] for s in baseline['selection'])
    previous_midi.update(s['midi_sha256'] for s in baseline['selection'])
    selection=[]
    for number,row in enumerate(rows[24:44],25):
        audio,midi=base/row['audio_filename'],base/row['midi_filename']
        a,m=digest(audio),digest(midi)
        assert a not in previous_audio and m not in previous_midi
        selection.append(dict(id='fit-'+str(number),audio=str(audio.relative_to(ROOT)),midi=str(midi.relative_to(ROOT)),audio_sha256=a,midi_sha256=m))
    assert len(selection)==len({s['audio_sha256'] for s in selection})==len({s['midi_sha256'] for s in selection})==20
    prior_path=ROOT/'build/joint_pitch/143d517357f2b5c2/dictionary.json'
    context_path=ROOT/'build/piano_context_empirical_joint_attack_screen/report.json'
    audit_path=ROOT/'build/keyboard_confirmation_audit.json'
    context,audit=read(context_path),read(audit_path)
    assert all(digest(ROOT/p)==h for p,h in context['inputs'].items())
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (manifest,prior_path,context_path,audit_path,baseline_path,Path(__file__))}
    for helper in ('supervised_piano_dictionary.py','joint_pitch_reference.py','capture_joint_note_coverage.py','midi_sustain_reference.py',
                   'evaluate_keyboard_confirmation.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    protocol=dict(inputs=inputs,selection=selection,seconds=60,fit_hop_seconds=.1,epochs=40,activation_updates=4,
                  ridge_rule='One unit of prior regularization per 2400 nonempty fitting frames',inference_updates=80,
                  context_threshold=context['threshold'],joint_floors=[.8,.3],numpy_version=np.__version__,
                  scope='Performances 25-44 are fitting data. Existing first three performances are development evaluation, not new held-out proof. No access to recordings 45 onward. No native changes.')
    directory=ROOT/'build/real_piano_dictionary_transfer'/hashlib.sha256(json.dumps(protocol,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',protocol)
    print('Frozen twenty-performance fitting selection:',directory.relative_to(ROOT),flush=True)
    with (directory/'capture.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        checkpoint=directory/'report.json'
        state=read(checkpoint) if checkpoint.exists() else dict(plan_sha256=digest(directory/'plan.json'),recordings={},complete=False)
        assert state['plan_sha256']==digest(directory/'plan.json')
        for sample in selection:
            target=directory/(sample['id']+'.npz')
            if sample['id'] in state['recordings']:
                assert digest(target)==state['recordings'][sample['id']]['sha256']
                continue
            audio,midi=ROOT/sample['audio'],ROOT/sample['midi']
            assert digest(audio)==sample['audio_sha256'] and digest(midi)==sample['midi_sha256']
            with wave.open(str(audio),'rb') as stream:
                assert stream.getsampwidth()==2 and stream.getcomptype()=='NONE'
                rate,channels=stream.getframerate(),stream.getnchannels()
                assert channels in (1,2)
                pcm=np.frombuffer(stream.readframes(rate*60),dtype='<i2').reshape(-1,channels)
            mono=(pcm.astype(float).mean(axis=1)/32768).astype(np.float32)
            hop=round(rate*.05)
            mono=mono[:len(mono)//hop*hop]
            assert len(mono)>=rate*20
            values=observations(mono.astype(float),rate)[:,1::2]
            times=np.arange(1,values.shape[1]+1)*2*hop/rate
            mask=label_mask(read_intervals(midi.read_bytes()),times)
            np.savez(target,observed=values,mask=mask)
            state['recordings'][sample['id']]=dict(sha256=digest(target),rate=rate,frames=len(times),labelled_frames=int(mask.any(axis=0).sum()))
            atomic_json(checkpoint,state)
            print(sample['id'],len(times),'fitting frames',flush=True)
        prior=np.array(read(prior_path)['columns']).T
        xs,ms=[],[]
        for sample in selection:
            data=np.load(directory/(sample['id']+'.npz'))
            xs.append(data['observed']);ms.append(data['mask'])
        x,mask=np.concatenate(xs,axis=1),np.concatenate(ms,axis=1)
        nonempty=mask.any(axis=0)
        ridge=float(nonempty.sum())/2400
        model_path=directory/'dictionary.npz'
        if (directory/'frozen.json').exists():
            frozen=read(directory/'frozen.json')
            assert digest(model_path)==frozen['dictionary_sha256'] and frozen['plan_sha256']==digest(directory/'plan.json')
            learned=np.load(model_path)['dictionary']
        else:
            print('Fitting dictionary on',int(nonempty.sum()),'labelled frames',flush=True)
            learned=learn_dictionary(prior,x[:,nonempty],mask[:,nonempty],ridge=ridge)
            np.savez(model_path,dictionary=learned)
            atomic_json(directory/'frozen.json',dict(plan_sha256=digest(directory/'plan.json'),dictionary_sha256=digest(model_path),ridge=ridge))
        results={}
        for name in ('training-1','training-2','training-3'):
            raw=baseline_path.parent/(name+'.f32')
            assert digest(raw)==baseline['recordings'][name]['prefix_sha256']
            rate=baseline['recordings'][name]['rate']
            observed=observations(np.fromfile(raw,dtype='<f4').astype(float),rate)
            activation=fit(learned,observed)
            projection=learned.T@observed
            relative=activation/np.maximum(activation.max(axis=0),1e-12)
            explained=activation/np.maximum(projection,1e-12)
            probabilities={(p['end_sample'],p['midi']):p['probability'] for p in context['recordings'][name]['probabilities']}
            accepted=[]
            metrics=dict(cells=0,held_seconds=0.,unsupported_seconds=0.)
            hop=round(rate*.05)
            for case in audit['recordings'][name]['cases']:
                endpoint,midi=case['end_sample'],case['midi']
                index=endpoint//hop-1
                if probabilities.get((endpoint,midi),0.)<context['threshold'] or relative[midi-21,index]<.8 or explained[midi-21,index]<.3:
                    continue
                accepted.append(dict(end_sample=endpoint,midi=midi))
                metrics['cells']+=1
                metrics['held_seconds']+=case['held_seconds']
                metrics['unsupported_seconds']+=case['unsupported_seconds']
            timing=score_acceptances(name,accepted)
            results[name]=dict(metrics=metrics,timing=timing,accepted=accepted)
            print(name,json.dumps({k:v for k,v in results[name].items() if k!='accepted'}),flush=True)
        assert all(digest(ROOT/p)==h for p,h in inputs.items())
        passed=sum(r['metrics']['held_seconds'] for r in results.values())>0 and all(
            r['metrics']['unsupported_seconds']<1e-8 and not r['timing']['isolated_additions'] and
            r['timing']['matched_attacks']['after']>=r['timing']['matched_attacks']['before'] for r in results.values())
        state.update(complete=True,results=results,decision='requires_new_native_calibration' if passed else 'reject_for_recovery',dictionary_sha256=digest(model_path))
        atomic_json(checkpoint,state)
        atomic_json(directory.parent/'current.json',dict(report=str(checkpoint.relative_to(ROOT)),sha256=digest(checkpoint)))
        print('Twenty-performance transfer:',state['decision'],flush=True)


if __name__=='__main__':
    main()
