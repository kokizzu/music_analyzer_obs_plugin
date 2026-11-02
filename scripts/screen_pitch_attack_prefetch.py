#!/usr/bin/env python3
"""Schedule inference from causal audio cues, never future native first hits."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
import math
from itertools import groupby
from pathlib import Path
import numpy as np
from evaluate_guitar_duplicate_model import lower_probability
from evaluate_keyboard_confirmation import score_acceptances
from joint_pitch_reference import fit
from piano_context_features import features
from pitch_attack_queue import simulate_latest,available_result
from routing_duration_baseline import ROOT,atomic_json,digest
from screen_piano_attack_rises import rising
from transfer_real_piano_dictionary import observations


def read(path):
    return json.loads(path.read_text())


def main():
    pointer=read(ROOT/'build/pitch_attack_evidence/current.json')
    evidence_path=ROOT/pointer['report']
    evidence=read(evidence_path)
    assert evidence['complete'] and digest(evidence_path)==pointer['sha256']
    model_path=ROOT/'build/real_piano_dictionary_transfer/cfb32e5534dc943f/dictionary.npz'
    transfer_path=model_path.parent/'report.json'
    transfer=read(transfer_path)
    assert digest(model_path)==transfer['dictionary_sha256']
    matrix=np.load(model_path)['dictionary']
    context_path=ROOT/'build/piano_context_model/3b35eca632935a8c/frozen.json'
    context=read(context_path)
    threshold=context['negative_max']+.001
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline=read(baseline_path)
    native_path=ROOT/'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    native=read(native_path)
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (evidence_path,model_path,transfer_path,context_path,baseline_path,native_path,Path(__file__))}
    for helper in ('pitch_attack_queue.py','screen_piano_attack_rises.py','piano_context_features.py','evaluate_guitar_duplicate_model.py',
                   'transfer_real_piano_dictionary.py','joint_pitch_reference.py','evaluate_keyboard_confirmation.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    directory=ROOT/'build/pitch_attack_prefetch_screen'
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',dict(inputs=inputs,request_policies=['rise2','strong_change'],context_threshold=threshold,
        relative_floor=.8,explained_floor=.3,preparation_ms=5.,maximum_request_age_seconds=.15,note_threshold=.3,onset_threshold=.5,
        scope='Request scheduling uses current/past audio features only. Fixed 5 ms preparation assumption is charged before measured inference execution. No analyzer/hardware latency qualification.'))
    schedules={}
    cached={}
    for name,recording in evidence['recordings'].items():
        rate=recording['rate']
        hop,count=round(rate*.05),round(rate*.1)
        raw=baseline_path.parent/(name+'.f32')
        assert digest(raw)==recording['raw_sha256']==baseline['recordings'][name]['prefix_sha256']
        input_path=native_path.parent/(name+'.tsv')
        assert digest(input_path)==native['recordings'][name]['sha256']
        inputs[str(raw.relative_to(ROOT))]=digest(raw)
        inputs[str(input_path.relative_to(ROOT))]=digest(input_path)
        audio=np.fromfile(raw,dtype='<f4')
        padded=np.pad(audio,(count,0))
        x=observations(audio.astype(float),rate)
        activation=fit(matrix,x)
        projection=matrix.T@x
        relative=activation/np.maximum(activation.max(axis=0),1e-12)
        explained=activation/np.maximum(projection,1e-12)
        request={policy:[] for policy in ('rise2','strong_change')}
        previous=set()
        with input_path.open() as stream:
            for index,(end,rows) in enumerate(groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample']))):
                row=next(rows)
                assert end==(index+1)*hop
                strong={i+21 for i in range(88) if relative[i,index]>=.8 and explained[i,index]>=.3}
                new=strong-previous
                previous=strong
                if row['mfcc_valid']!='1':
                    continue
                vector=features(padded[end:end+count],rate,[float(row['mfcc'+str(i)]) for i in range(24)])
                probability=lower_probability(context['model'],vector)
                if probability<threshold:
                    continue
                if index>=3 and any(rising(activation,index,m) for m in strong):
                    request['rise2'].append(end)
                if new:
                    request['strong_change'].append(end)
        schedules[name]=request
        captured_path=evidence_path.parent/(name+'.tsv')
        assert digest(captured_path)==recording['sha256']
        inputs[str(captured_path.relative_to(ROOT))]=digest(captured_path)
        events=[]
        with captured_path.open() as stream:
            for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
                group=list(rows)
                events.append(dict(end_sample=end,ready_sample=end+math.ceil(rate*.005),wall_ms=float(group[0]['wall_ms']),
                    cpu_ms=float(group[0]['cpu_ms']),notes={int(r['midi']):{k:float(r[k]) for k in ('legacy','edge4_note','edge4_onset')} for r in group}))
        cached[name]=events
    # Freeze all request endpoints before consulting first-hit cases/labels.
    atomic_json(directory/'requests.json',dict(inputs=inputs,schedules=schedules))
    audit_path=ROOT/'build/keyboard_confirmation_audit.json'
    audit=read(audit_path)
    inputs[str(audit_path.relative_to(ROOT))]=digest(audit_path)
    results={}
    for name,events in cached.items():
        rate=evidence['recordings'][name]['rate']
        base={(c['end_sample'],c['midi']) for c in transfer['results'][name]['accepted']}
        for policy,ends in schedules[name].items():
            requested=set(ends)
            requests=[e for e in events if e['end_sample'] in requested]
            queue=simulate_latest(requests,rate)
            cost=sum(requests[r['event_index']]['cpu_ms'] for r in queue)/(60*1000)
            for mode in ('legacy','edge4','edge4_onset'):
                accepted=[]
                metrics=dict(cells=0,held_seconds=0.,unsupported_seconds=0.)
                for case in audit['recordings'][name]['cases']:
                    end,midi=case['end_sample'],case['midi']
                    if (end,midi) not in base:
                        continue
                    latest=available_result(queue,end,round(rate*.15))
                    if latest is None:
                        continue
                    note=requests[latest['event_index']]['notes'][midi]
                    allowed=note['legacy']>=.3 if mode=='legacy' else note['edge4_note']>=.3
                    if mode=='edge4_onset':
                        allowed=allowed and note['edge4_onset']>=.5
                    if not allowed:
                        continue
                    assert latest['completed_sample']<=end and latest['model_end_sample']<=end
                    accepted.append(dict(end_sample=end,midi=midi,model_end_sample=latest['model_end_sample'],completed_sample=latest['completed_sample']))
                    metrics['cells']+=1
                    metrics['held_seconds']+=case['held_seconds']
                    metrics['unsupported_seconds']+=case['unsupported_seconds']
                key=policy+'-'+mode
                results.setdefault(key,{})[name]=dict(metrics=metrics,timing=score_acceptances(name,accepted),accepted=accepted,
                    requests=len(requests),processed=len(queue),estimated_worker_core_share=cost)
                print(name,key,json.dumps({k:v for k,v in results[key][name].items() if k!='accepted'}),flush=True)
    decisions={key:dict(attack_gain=sum(r['timing']['matched_attacks']['after']-r['timing']['matched_attacks']['before'] for r in records.values()),
        unsupported_seconds=sum(r['metrics']['unsupported_seconds'] for r in records.values()),
        isolated_additions=sum(r['timing']['isolated_additions'] for r in records.values())) for key,records in results.items()}
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    atomic_json(directory/'report.json',dict(inputs=inputs,results=results,decisions=decisions,requests_sha256=digest(directory/'requests.json'),
        scope='Training-development simulation only. Five-millisecond preparation is assumed, not benchmarked. No first-hit/annotation oracle schedules requests. No native integration or promotion; isolated additions and hardware costs still require verification.'))
    print(json.dumps(decisions,indent=2),flush=True)


if __name__=='__main__':
    main()
