#!/usr/bin/env python3
"""Screen native-repeat and uncertainty policies on development only."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
import math
from itertools import groupby
import numpy as np
from detection_validation_store import Store
from midi_sustain_reference import read_intervals
from native_note_candidates import RepeatedStrikeGate,OwnershipHold
from note_onset_score import score_onsets
from pitch_attack_queue import simulate_latest,available_result
from pitch_continuity_control_evidence import audio_gates
from routing_duration_baseline import ROOT,digest
from routing_duration_score import score
from validate_pitch_continuity_calibration import DICTIONARY,CONTEXT


def read(path):
    return json.loads(path.read_text())


def pitches(row,key):
    return {int(m) for m in row[key].split(',') if m}


def main():
    baseline=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267';manifest=read(baseline/'report.json')
    primary=ROOT/'build/routing_consensus_pair/e63350f9b5113f8b';candidate=ROOT/'build/routing_candidate_evidence/42e25eb544a48fc7'
    dense=ROOT/'build/pitch_attack_evidence/c2298a7181c716c3';tools=ROOT/'build/pitch_heldout_tools/06aec4200b7fb541'
    matrix=np.load(DICTIONARY)['dictionary'];context=read(CONTEXT);results={};inputs={}
    for name in ('training-1','training-2','training-3'):
        paths=[baseline/(name+'.f32'),primary/('piano-'+name+'.tsv'),candidate/(name+'.tsv'),dense/(name+'.tsv'),tools/(name+'-features.tsv')]
        for p in paths: inputs[str(p.relative_to(ROOT))]=digest(p)
        assert digest(paths[0])==manifest['recordings'][name]['prefix_sha256']
        assert digest(paths[1])==read(primary/'report.json')['recordings']['piano-'+name]['sha256']
        assert digest(paths[2])==read(candidate/'report.json')['recordings'][name]['sha256']
        assert digest(paths[3])==read(dense/'report.json')['recordings'][name]['sha256']
        rate=manifest['recordings'][name]['rate'];hop=round(rate*.05)
        with paths[1].open() as stream: frames=[dict(r,guitar=r['after_guitar'],voice=r['after_voice']) for r in csv.DictReader(stream,delimiter='\t')]
        with paths[2].open() as stream: debug={end:list(rows) for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample']))}
        gates,requested=audio_gates(paths[0],paths[4],rate,matrix,context);requested=set(requested);events=[]
        with paths[3].open() as stream:
            for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
                rows=list(rows)
                if end in requested:
                    events.append(dict(end_sample=end,ready_sample=end+math.ceil(rate*.005),wall_ms=float(rows[0]['wall_ms']),notes={int(r['midi']):float(r['edge4_note']) for r in rows}))
        queue=simulate_latest(events,rate);repeat=RepeatedStrikeGate(rate,hop);hold=OwnershipHold(hop)
        previous=set();edges=[];repeats=[];uncertain=[];removed_cells=0
        kinds=('bass','guitar','keys','voice','other','ambiguous')
        for frame,(end,strong,_) in zip(frames,gates):
            assert int(frame['end_sample'])==end
            keys=pitches(frame,'keys');edges.extend((m,end/rate) for m in keys-previous);previous=keys
            rows={}
            for row in debug[end]:
                midi=int(row['midi'])
                if midi>=0 and (midi not in rows or float(row['ownership'])>float(rows[midi]['ownership'])): rows[midi]=row
            latest=available_result(queue,end,round(rate*.15))
            event=events[latest['event_index']] if latest else None
            repeats.extend((m,end/rate) for m in repeat.step(end,keys,{m:float(r['onset']) for m,r in rows.items() if m in strong},
                event['notes'] if event else {},event['end_sample'] if event else None,latest['completed_sample'] if latest else None))
            trial={key:pitches(frame,key) for key in kinds}
            for midi,row in rows.items():
                owner=kinds[int(row['owner'])]
                if owner!='ambiguous' and midi in trial[owner] and hold.step(end,midi,owner,float(row['ownership']))=='ambiguous':
                    trial[owner].remove(midi);trial['ambiguous'].add(midi);removed_cells+=1
            uncertain.append(dict(frame,**{k:','.join(map(str,sorted(v))) for k,v in trial.items()}))
        sample=next(s for s in manifest['selection'] if s['id']==name);midi=ROOT/sample['midi'];assert digest(midi)==sample['midi_sha256']
        inputs[str(midi.relative_to(ROOT))]=digest(midi);notes=read_intervals(midi.read_bytes())
        before=score(frames,notes,rate);after=score(uncertain,notes,rate)
        base_events=score_onsets(edges,notes,60.);fused=score_onsets(edges+repeats,notes,60.)
        results[name]=dict(repeat_events=len(repeats),baseline={k:v for k,v in base_events.items() if k!='latency_ms'},
            fused={k:v for k,v in fused.items() if k!='latency_ms'},uncertainty=dict(protected_row_cells_removed=removed_cells,
                correct_keyboard_held_seconds_lost=after['keys']['missing_note_seconds']-before['keys']['missing_note_seconds']))
        print(name,json.dumps(results[name]),flush=True)
    for p in (DICTIONARY,CONTEXT,ROOT/'scripts/native_note_candidates.py',ROOT/'scripts/screen_native_note_candidates.py',ROOT/'scripts/note_onset_score.py'):
        inputs[str(p.relative_to(ROOT))]=digest(p)
    repeat_ok=all(r['fused']['matched']>=r['baseline']['matched'] and r['fused']['unmatched']<=r['baseline']['unmatched'] for r in results.values()) and sum(r['fused']['matched']>r['baseline']['matched'] for r in results.values())>=2
    uncertain_ok=all(r['uncertainty']['protected_row_cells_removed']==0 for r in results.values())
    result=dict(inputs=inputs,recordings=results,repeat_decision='requires_native_and_new_heldout' if repeat_ok else 'cancel_development',
        uncertainty_decision='neutral_cancel' if uncertain_ok else 'cancel_protected_row_loss',
        scope='Known development only. Fixed native onset .5 rising edge, current strict piano gate, fresh neural note .3, 150ms expiry/refractory; adds events to baseline without visibility gaps. Ownership proposal .8 confidence for three consecutive hops, otherwise Ambiguous. No production wiring or reserved-recording reads.')
    with Store() as store: store.evidence('native-note-candidates','development',result)
    print(result['repeat_decision'],result['uncertainty_decision'],flush=True)


if __name__=='__main__': main()
