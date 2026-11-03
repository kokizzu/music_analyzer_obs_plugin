#!/usr/bin/env python3
"""Partition known-development Keyboard misses without proposing new admissions."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
from collections import defaultdict
from itertools import groupby
from pathlib import Path
import numpy as np
from audit_keyboard_recovery import coverage
from evaluate_guitar_duplicate_model import lower_probability
from midi_sustain_reference import read_intervals
from piano_context_features import features
from routing_duration_baseline import ROOT,atomic_json,digest
from routing_duration_score import merge,score

ROWS=('guitar','voice','bass','other','ambiguous')


def pitches(row,key):
    return {int(v) for v in row[key].split(',') if v}


def partition_attacks(frames,notes,rate,tracking,debug):
    hop=round(rate*.05);horizon=int(frames[-1]['end_sample'])/rate
    predictions=defaultdict(list);attacks=defaultdict(list)
    for row in frames:
        start=int(row['end_sample'])/rate;end=min(horizon,start+hop/rate)
        for midi in pitches(row,'keys'):
            predictions[midi].append((start,end))
    predictions={m:merge(v) for m,v in predictions.items()}
    for note in notes:
        deadline=min(note['key_end'],note['start']+.15)
        if note['channel']!=9 and note['start']<horizon and deadline<=horizon:
            attacks[note['midi']].append((note['start'],deadline))
    missed=[];matched=0
    for midi,expected in attacks.items():
        candidates=[start for start,end in predictions.get(midi,[])];used=set()
        for start,deadline in sorted(expected):
            match=next((i for i,value in enumerate(candidates) if i not in used and start-1e-12<=value<=deadline+1e-12),None)
            if match is not None:
                used.add(match);matched+=1;continue
            window=[row for row in frames if start-1e-12<=int(row['end_sample'])/rate<=deadline+1e-12]
            prior=any(a<start-1e-12 and b>start+1e-12 for a,b in predictions.get(midi,[]))
            elsewhere={key for key in ROWS if any(midi in pitches(row,key) for row in window)}
            raw=any(tracking.get((int(row['end_sample']),midi),(False,False,False))[0] for row in window)
            debug_seen=any((int(row['end_sample']),midi) in debug for row in window)
            category=('keyboard_already_visible_at_onset' if prior else 'guitar_or_voice_visible_by_deadline' if elsewhere&{'guitar','voice'} else
                'other_row_visible_by_deadline' if elsewhere else 'raw_keyboard_seen_by_deadline' if raw else
                'debug_candidate_only_by_deadline' if debug_seen else 'no_observation_by_deadline')
            previous_notes=[n for n in notes if n['channel']!=9 and n['midi']==midi and n['start']<start-1e-12]
            prior_sounding=any(n['end']>start+1e-12 for n in previous_notes)
            prior_grace=any(n['end']+.3>start+1e-12 for n in previous_notes)
            missed.append(dict(midi=midi,start=start,deadline=deadline,category=category,other_rows=sorted(elsewhere),
                prior_note_sounding_at_onset=prior_sounding,prior_note_release_grace_at_onset=prior_grace))
    counts={key:sum(row['category']==key for row in missed) for key in sorted({r['category'] for r in missed})}
    prior=[r for r in missed if r['category']=='keyboard_already_visible_at_onset']
    contexts=dict(prior_note_sounding=sum(r['prior_note_sounding_at_onset'] for r in prior),
        prior_release_grace_only=sum(r['prior_note_release_grace_at_onset'] and not r['prior_note_sounding_at_onset'] for r in prior),
        no_prior_annotation_support=sum(not r['prior_note_release_grace_at_onset'] for r in prior))
    return dict(matched=matched,missed=len(missed),categories=counts,prior_visibility_context=contexts,cases=missed)


def main():
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    candidate_path=ROOT/'build/routing_candidate_evidence/42e25eb544a48fc7/report.json'
    trace_path=ROOT/'build/primary_duration_trace/954041e8c8c9eb7f/report.json'
    primary_path=ROOT/'build/routing_consensus_pair/e63350f9b5113f8b/report.json'
    context_path=ROOT/'build/piano_context_model/3b35eca632935a8c/frozen.json'
    baseline,candidate,trace,primary,context=(json.loads(p.read_text()) for p in (baseline_path,candidate_path,trace_path,primary_path,context_path))
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (baseline_path,candidate_path,trace_path,primary_path,context_path,Path(__file__))}
    for helper in ('routing_duration_score.py','midi_sustain_reference.py','audit_keyboard_recovery.py','piano_context_features.py','evaluate_guitar_duplicate_model.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    recordings={}
    for name in ('training-1','training-2','training-3'):
        sample=next(s for s in baseline['selection'] if s['id']==name);rate=baseline['recordings'][name]['rate']
        paths=[primary_path.parent/('piano-'+name+'.tsv'),candidate_path.parent/(name+'.tsv'),trace_path.parent/(name+'.trace.tsv'),baseline_path.parent/(name+'.f32'),ROOT/sample['midi']]
        hashes=[primary['recordings']['piano-'+name]['sha256'],candidate['recordings'][name]['sha256'],trace['recordings'][name]['trace_sha256'],baseline['recordings'][name]['prefix_sha256'],sample['midi_sha256']]
        for path,checksum in zip(paths,hashes):
            assert digest(path)==checksum;inputs[str(path.relative_to(ROOT))]=checksum
        with paths[0].open() as stream:
            frames=[dict(r,guitar=r['after_guitar'],voice=r['after_voice']) for r in csv.DictReader(stream,delimiter='\t')]
        with paths[2].open() as stream:
            tracking={(int(r['end_sample']),int(r['midi'])):(float(r['raw'])>0,float(r['smoothed'])>0,r['confirmed']=='1') for r in csv.DictReader(stream,delimiter='\t')}
        debug={};probabilities={}
        audio=np.fromfile(paths[3],dtype='<f4');count=round(rate*.1);padded=np.pad(audio,(count,0))
        with paths[1].open() as stream:
            for index,(end,rows) in enumerate(groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample']))):
                group=list(rows);row=group[0]
                assert end==int(frames[index]['end_sample']) and row['keys']==frames[index]['keys']
                for r in group:
                    if int(r['midi'])>=0:
                        debug[end,int(r['midi'])]=int(r['owner'])
                probabilities[end]=0.
                if row['mfcc_valid']=='1':
                    vector=features(padded[end:end+count],rate,[float(row['mfcc'+str(i)]) for i in range(24)])
                    probabilities[end]=lower_probability(context['model'],vector)
        notes=read_intervals(paths[4].read_bytes())
        held=defaultdict(list)
        for note in notes:
            if note['channel']!=9:
                held[note['midi']].append((note['start'],min(60.,note['key_end'])))
        held={m:merge(v) for m,v in held.items()}
        stages={};patterns=defaultdict(float);owners=defaultdict(float)
        warmup=sum(coverage(v,0.,round(rate*.05)/rate) for v in held.values())
        for frame in frames:
            end_sample=int(frame['end_sample']);start=end_sample/rate;end=min(60.,start+.05)
            visible=pitches(frame,'keys')
            for midi,intervals in held.items():
                missing=coverage(intervals,start,end) if midi not in visible else 0.
                if missing<=0:
                    continue
                raw,smoothed,confirmed=tracking.get((end_sample,midi),(False,False,False))
                stage='postprocess' if smoothed else ('smoothing_selection' if confirmed else 'confirmation') if raw else 'raw_keyboard_absent'
                metric=stages.setdefault(stage,dict(missing_held_seconds=0.,guitar_or_voice_visible_seconds=0.,any_other_row_visible_seconds=0.,piano_context_pass_seconds=0.,guitar_or_voice_and_piano_context_seconds=0.))
                elsewhere={key for key in ROWS if midi in pitches(frame,key)}
                metric['missing_held_seconds']+=missing
                metric['guitar_or_voice_visible_seconds']+=missing*bool(elsewhere&{'guitar','voice'})
                metric['any_other_row_visible_seconds']+=missing*bool(elsewhere)
                metric['piano_context_pass_seconds']+=missing*(probabilities[end_sample]>=context['negative_max']+.001)
                metric['guitar_or_voice_and_piano_context_seconds']+=missing*(bool(elsewhere&{'guitar','voice'}) and probabilities[end_sample]>=context['negative_max']+.001)
                patterns['+'.join(sorted(elsewhere)) or 'none']+=missing
                if not raw and (end_sample,midi) in debug:
                    owners['owner_code_'+str(debug[end_sample,midi])]+=missing
        expected=score(frames,notes,rate)['keys']
        assert abs(sum(v['missing_held_seconds'] for v in stages.values())+warmup-expected['missing_note_seconds'])<1e-7
        attacks=partition_attacks(frames,notes,rate,tracking,debug)
        assert attacks['matched']==expected['matched_attacks'] and attacks['missed']==expected['missed_attacks']
        recordings[name]=dict(stages=stages,warmup_missing_seconds=warmup,wrong_row_patterns=dict(patterns),raw_absent_debug_owners=dict(owners),attacks=attacks)
        print(name,json.dumps(dict(stages=stages,attacks={k:v for k,v in attacks.items() if k!='cases'})),flush=True)
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    atomic_json(ROOT/'build/keyboard_routing_gap_audit.json',dict(inputs=inputs,recordings=recordings,
        scope='Known development only. Observational partitions, not proof of acoustic cause or safe rerouting. Subcounts within each stage overlap. No held-out reads, new admission rule, threshold tuning or runtime change.'))


if __name__=='__main__':
    main()
