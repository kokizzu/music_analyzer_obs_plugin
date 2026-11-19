#!/usr/bin/env python3
"""Development-only counterfactual screen; never changes analyzer behavior."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
import math
from itertools import groupby
import numpy as np
from detection_validation_store import Store
from midi_sustain_reference import read_intervals
from note_onset_score import score_onsets
from pitch_attack_queue import simulate_latest,available_result
from pitch_continuity_control_evidence import audio_gates
from routing_duration_baseline import ROOT,digest
from routing_duration_score import score
from validate_pitch_continuity_calibration import DICTIONARY,CONTEXT


def read(path):
    return json.loads(path.read_text())


def main():
    baseline=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267';manifest=read(baseline/'report.json')
    primary=ROOT/'build/routing_consensus_pair/e63350f9b5113f8b';primary_report=read(primary/'report.json')
    dense=ROOT/'build/pitch_attack_evidence/c2298a7181c716c3';dense_report=read(dense/'report.json')
    tools=ROOT/'build/pitch_heldout_tools/06aec4200b7fb541'
    matrix=np.load(DICTIONARY)['dictionary'];context=read(CONTEXT);results={}
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (DICTIONARY,CONTEXT,baseline/'report.json',primary/'report.json',dense/'report.json')}
    inputs.update({'scripts/'+name:digest(ROOT/'scripts'/name) for name in
        ('screen_routing_onset_proposals.py','note_onset_score.py','pitch_continuity_control_evidence.py','pitch_attack_queue.py')})
    # Fixed existing gates, no threshold search and no reserved-cohort reads.
    for name in ('training-1','training-2','training-3'):
        raw=baseline/(name+'.f32');rate=manifest['recordings'][name]['rate']
        assert digest(raw)==manifest['recordings'][name]['prefix_sha256']
        path=primary/('piano-'+name+'.tsv')
        assert digest(path)==primary_report['recordings']['piano-'+name]['sha256']
        model=dense/(name+'.tsv');assert digest(model)==dense_report['recordings'][name]['sha256']
        with path.open() as stream:
            frames=[dict(r,guitar=r['after_guitar'],voice=r['after_voice']) for r in csv.DictReader(stream,delimiter='\t')]
        gates,requests=audio_gates(raw,tools/(name+'-features.tsv'),rate,matrix,context)
        events=[];requested=set(requests)
        with model.open() as stream:
            for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
                group=list(rows)
                if end in requested:
                    events.append(dict(end_sample=end,ready_sample=end+math.ceil(rate*.005),wall_ms=float(group[0]['wall_ms']),
                        note={int(r['midi']):float(r['edge4_note']) for r in group},
                        onset={int(r['midi']):float(r['edge4_onset']) for r in group}))
        queue=simulate_latest(events,rate);trial=[];new_events=[];edges=[];previous=set();previous_neural=set();last={};seen=-1
        for row,(end,strong,continuing) in zip(frames,gates):
            assert int(row['end_sample'])==end
            keys={int(m) for m in row['keys'].split(',') if m}
            edges.extend((m,end/rate) for m in keys-previous);previous=keys
            latest=available_result(queue,end,round(rate*.15));added=set()
            if latest is not None:
                event=events[latest['event_index']]
                other={int(m) for key in ('guitar','voice') for m in row[key].split(',') if m}
                added={m for m in (other&strong)-keys if event['note'].get(m,0)>=.3}
                if latest['event_index']!=seen:
                    seen=latest['event_index'];active={m for m,p in event['onset'].items() if p>=.3 and event['note'][m]>=.3 and m in strong}
                    for midi in active-previous_neural:
                        if end/rate-last.get(midi,-1) >= .15:
                            new_events.append((midi,end/rate));last[midi]=end/rate
                    previous_neural=active
            trial.append(dict(row,keys=','.join(map(str,sorted(keys|added)))))
        sample=next(s for s in manifest['selection'] if s['id']==name)
        assert digest(ROOT/sample['midi'])==sample['midi_sha256']
        notes=read_intervals((ROOT/sample['midi']).read_bytes());before=score(frames,notes,rate);after=score(trial,notes,rate)
        onset_before=score_onsets(edges,notes,60.);onset_after=score_onsets(new_events,notes,60.)
        route=dict(added_cells=sum(len(set(t['keys'].split(','))-{''})-len(set(r['keys'].split(','))-{''}) for r,t in zip(frames,trial)),
            held_seconds_recovered=before['keys']['missing_note_seconds']-after['keys']['missing_note_seconds'],
            unsupported_seconds_delta=after['keys']['annotation_unsupported_note_seconds']-before['keys']['annotation_unsupported_note_seconds'])
        results[name]=dict(routing=route,onset_baseline=onset_before,onset_proposal=onset_after)
        for p in (raw,path,model,tools/(name+'-features.tsv'),ROOT/sample['midi']):
            inputs[str(p.relative_to(ROOT))]=digest(p)
        print(name,json.dumps(dict(routing=route,onset_before={k:v for k,v in onset_before.items() if k!='latency_ms'},
            onset_after={k:v for k,v in onset_after.items() if k!='latency_ms'})),flush=True)
    route_ok=all(r['routing']['unsupported_seconds_delta']<=1e-8 for r in results.values()) and sum(r['routing']['held_seconds_recovered'] for r in results.values())>0
    onset_ok=all(r['onset_proposal']['matched']>=r['onset_baseline']['matched'] and r['onset_proposal']['unmatched']<=r['onset_baseline']['unmatched'] for r in results.values()) and any(r['onset_proposal']['matched']>r['onset_baseline']['matched'] for r in results.values())
    result=dict(inputs=inputs,recordings=results,routing_decision='requires_native_validation' if route_ok else 'reject_development',
        onset_decision='requires_native_validation' if onset_ok else 'reject_development',
        scope='Known development only. Hypothesis: current Guitar/Voice pitch + frozen strict piano seed gates; separate onset hypothesis: fresh neural .3 rising edge with .15s refractory. Captured timing with assumed 5ms preparation, not live performance. No production change or tuning on failed controls.')
    with Store() as store:
        store.evidence('routing-onset-screen','development',result)
    print(result['routing_decision'],result['onset_decision'],flush=True)


if __name__=='__main__':
    main()
