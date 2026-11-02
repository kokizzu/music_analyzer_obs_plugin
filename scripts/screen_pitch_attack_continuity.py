#!/usr/bin/env python3
"""Freeze audio-driven continuity decisions before sustain-aware scoring."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
from itertools import groupby
from pathlib import Path
import numpy as np
from audit_keyboard_recovery import coverage
from evaluate_guitar_duplicate_model import lower_probability
from evaluate_keyboard_confirmation import score_acceptances
from joint_pitch_reference import fit
from midi_sustain_reference import read_intervals
from piano_context_features import features
from pitch_attack_continuity import simulate
from pitch_attack_queue import simulate_latest,available_result
from routing_duration_baseline import ROOT,atomic_json,digest
from routing_duration_score import merge
from transfer_real_piano_dictionary import observations


def read(path):
    return json.loads(path.read_text())


def main():
    directory=ROOT/'build/pitch_attack_continuity_screen'
    directory.mkdir(parents=True,exist_ok=True)
    evidence_path=ROOT/'build/pitch_attack_evidence/c2298a7181c716c3/report.json'
    evidence=read(evidence_path)
    requests_path=ROOT/'build/pitch_attack_prefetch_screen/requests.json'
    requests=read(requests_path)
    assert all(digest(ROOT/p)==h for p,h in requests['inputs'].items())
    matrix_path=ROOT/'build/real_piano_dictionary_transfer/cfb32e5534dc943f/dictionary.npz'
    context_path=ROOT/'build/piano_context_model/3b35eca632935a8c/frozen.json'
    matrix=np.load(matrix_path)['dictionary']
    context=read(context_path)
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline=read(baseline_path)
    native_path=ROOT/'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    native=read(native_path)
    trace_path=ROOT/'build/primary_duration_trace/954041e8c8c9eb7f/report.json'
    trace=read(trace_path)
    display=ROOT/'build/pitch_attack_display_native/381fe8745f049c1b'
    replay=read(display/'replay.json')
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (evidence_path,requests_path,matrix_path,context_path,baseline_path,native_path,trace_path,display/'replay.json',Path(__file__))}
    for helper in ('pitch_attack_continuity.py','pitch_attack_queue.py','piano_context_features.py','evaluate_guitar_duplicate_model.py',
                   'transfer_real_piano_dictionary.py','joint_pitch_reference.py','evaluate_keyboard_confirmation.py','routing_duration_score.py',
                   'midi_sustain_reference.py','audit_keyboard_recovery.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    atomic_json(directory/'plan.json',dict(inputs=inputs,policies=['prefetch_only','refresh_overlay','seed_context_latch'],
        context_threshold=context['negative_max']+.001,relative_floor=.8,explained_floor=.3,note_floor=.3,
        maximum_input_age_seconds=.15,maximum_display_seconds=.15,preparation_ms=5.,
        continuation='Seed context latch retains family/relative-dominance eligibility for at most 150 ms; each continued pitch still needs current explained projection >= .3 and fresh neural confidence >= .3',
        scope='Audio-only first-hit/continuation simulation; no blind hold, future outputs, annotation-triggered requests, native integration or latency qualification.'))
    schedules={};interruptions={};native_support={}
    for name,recording in evidence['recordings'].items():
        rate=recording['rate'];hop=round(rate*.05);count=round(rate*.1)
        raw=baseline_path.parent/(name+'.f32')
        feature_path=native_path.parent/(name+'.tsv')
        tracking_path=trace_path.parent/(name+'.trace.tsv')
        frames_path=display/(name+'.tsv')
        captured=evidence_path.parent/(name+'.tsv')
        checks=[(raw,recording['raw_sha256']),(feature_path,native['recordings'][name]['sha256']),
                (tracking_path,trace['recordings'][name]['trace_sha256']),(frames_path,replay['outputs'][name]),(captured,recording['sha256'])]
        for path,checksum in checks:
            assert digest(path)==checksum
            inputs[str(path.relative_to(ROOT))]=checksum
        audio=np.fromfile(raw,dtype='<f4')
        padded=np.pad(audio,(count,0))
        observed=observations(audio.astype(float),rate)
        activation=fit(matrix,observed)
        relative=activation/np.maximum(activation.max(axis=0),1e-12)
        explained=activation/np.maximum(matrix.T@observed,1e-12)
        first_hits={}
        with tracking_path.open() as stream:
            for row in csv.DictReader(stream,delimiter='\t'):
                if float(row['raw'])>0 and float(row['smoothed'])==0 and row['confirmed']=='0' and int(row['hits'])==1 and int(row['misses'])==0:
                    first_hits.setdefault(int(row['end_sample']),set()).add(int(row['midi']))
        with frames_path.open() as stream:
            originals={int(r['end_sample']):r for r in csv.DictReader(stream,delimiter='\t')}
        frames=[];components={}
        with feature_path.open() as stream:
            for index,(end,rows) in enumerate(groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample']))):
                row=next(rows)
                assert end==(index+1)*hop
                probability=0.
                if row['mfcc_valid']=='1':
                    vector=features(padded[end:end+count],rate,[float(row['mfcc'+str(i)]) for i in range(24)])
                    probability=lower_probability(context['model'],vector)
                strong={i+21 for i in range(88) if probability>=context['negative_max']+.001 and relative[i,index]>=.8 and explained[i,index]>=.3}
                original=originals[end]
                frames.append(dict(end_sample=end,strong=strong,continuing={i+21 for i in range(88) if explained[i,index]>=.3},first_hits=first_hits.get(end,set()),
                    visible={int(m) for m in original['keys'].split(',') if m},free_slots=[int(n) for n in original['free_slots'].split(',')]))
                components[end]=dict(probability=probability,relative=relative[:,index].tolist(),explained=explained[:,index].tolist())
        events={}
        with captured.open() as stream:
            for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
                group=list(rows)
                events[end]=dict(wall_ms=float(group[0]['wall_ms']),cpu_ms=float(group[0]['cpu_ms']),notes={int(r['midi']):float(r['edge4_note']) for r in group})
        schedules[name]={policy:simulate(frames,events,set(requests['schedules'][name]['strong_change']),rate,policy=='refresh_overlay',policy=='seed_context_latch')
                         for policy in ('prefetch_only','refresh_overlay','seed_context_latch')}
        selected=set(requests['schedules'][name]['strong_change'])
        original_events=[dict(event,end_sample=end,ready_sample=end+int(np.ceil(rate*.005))) for end,event in events.items() if end in selected]
        queue=simulate_latest(original_events,rate)
        support_lines=[]
        for frame in frames:
            end=frame['end_sample']
            latest=available_result(queue,end,round(rate*.15))
            if latest is None:
                continue
            notes=original_events[latest['event_index']]['notes']
            for midi in range(21,109):
                seed=midi in frame['strong'] and notes[midi]>=.3
                continuing=midi in frame['continuing'] and notes[midi]>=.3
                if seed or continuing:
                    support_lines.append(f'{end}\t{midi}\t{int(seed)}\t{int(continuing)}\n')
        support_path=directory/(name+'-native-support.tsv')
        support_path.write_text(''.join(support_lines))
        native_support[name]=dict(path=str(support_path.relative_to(ROOT)),sha256=digest(support_path),rate=rate,raw=str(raw.relative_to(ROOT)))
        audit=[]
        for seed,row in originals.items():
            native_visible={int(m) for m in row['keys'].split(',') if m}
            recovered={int(m) for m in row['after_keys'].split(',') if m}-native_visible
            for midi in sorted(recovered):
                values=[]
                for offset in range(4):
                    end=seed+offset*hop
                    latest=available_result(queue,end,round(rate*60))
                    c=components[end]
                    age=None if latest is None else (end-latest['model_end_sample'])/rate
                    note=None if latest is None else original_events[latest['event_index']]['notes'][midi]
                    values.append(dict(end_sample=end,context_probability=c['probability'],relative=c['relative'][midi-21],
                        explained=c['explained'][midi-21],model_age_seconds=age,neural_note=note,
                        context_pass=c['probability']>=context['negative_max']+.001,
                        pitch_pass=c['relative'][midi-21]>=.8 and c['explained'][midi-21]>=.3,
                        neural_pass=age is not None and age<=.15 and note>=.3))
                audit.append(dict(seed_end_sample=seed,midi=midi,frames=values))
        interruptions[name]=audit
    # No MIDI is read until every request and admission across all recordings is frozen.
    schedule_path=directory/'schedules.json'
    atomic_json(schedule_path,dict(inputs=inputs,results=schedules))
    atomic_json(directory/'native-support.json',dict(inputs=inputs,recordings=native_support,
        scope='All-pitch seed/continuation support from current audio and completed original-prefetch results; no annotations or first-hit case selection.'))
    atomic_json(directory/'interruptions.json',dict(inputs=inputs,recordings=interruptions,
        scope='Audio gate attribution at actual native recovered notes and the next three endpoints; annotations are not used.'))
    results={}
    for name,policies in schedules.items():
        sample=next(s for s in baseline['selection'] if s['id']==name)
        midi=ROOT/sample['midi']
        assert digest(midi)==sample['midi_sha256']
        inputs[str(midi.relative_to(ROOT))]=digest(midi)
        held={};allowed={}
        for note in read_intervals(midi.read_bytes()):
            if note['channel']!=9:
                held.setdefault(note['midi'],[]).append((note['start'],note['key_end']))
                allowed.setdefault(note['midi'],[]).append((note['start'],note['end']+.3))
        held={m:merge(v) for m,v in held.items()};allowed={m:merge(v) for m,v in allowed.items()}
        for policy,row in policies.items():
            metric=dict(cells=len(row['accepted']),held_seconds=0.,unsupported_seconds=0.)
            for case in row['accepted']:
                start=case['end_sample']/evidence['recordings'][name]['rate'];end=min(60.,start+.05)
                metric['held_seconds']+=coverage(held.get(case['midi'],[]),start,end)
                metric['unsupported_seconds']+=end-start-coverage(allowed.get(case['midi'],[]),start,end)
            result=dict(row,metrics=metric,timing=score_acceptances(name,row['accepted']))
            results.setdefault(policy,{})[name]=result
            print(name,policy,json.dumps({k:v for k,v in result.items() if k not in ('accepted','requests')}),flush=True)
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    atomic_json(directory/'report.json',dict(inputs=inputs,schedules_sha256=digest(schedule_path),results=results,
        scope='Development-only bounded continuity simulation. Five-millisecond preparation remains assumed; first-hit raw trace precedes the native display hook, so a positive screen requires actual native verification.'))
    print(directory.relative_to(ROOT)/'report.json',flush=True)


if __name__=='__main__':
    main()
