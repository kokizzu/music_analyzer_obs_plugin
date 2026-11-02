#!/usr/bin/env python3
"""Gate existing development proposals with independent causal neural pitch."""
import csv
import json
from itertools import groupby
from pathlib import Path
from evaluate_keyboard_confirmation import score_acceptances
from pitch_attack_queue import simulate_latest,available_result
from routing_duration_baseline import ROOT,atomic_json,digest


def read(path):
    return json.loads(path.read_text())


def main():
    pointer=read(ROOT/'build/pitch_attack_evidence/current.json')
    evidence_path=ROOT/pointer['report']
    evidence=read(evidence_path)
    assert digest(evidence_path)==pointer['sha256'] and evidence['complete']
    parent_path=ROOT/'build/real_piano_dictionary_transfer/cfb32e5534dc943f/report.json'
    parent=read(parent_path)
    assert parent['complete']
    audit_path=ROOT/'build/keyboard_confirmation_audit.json'
    audit=read(audit_path)
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (evidence_path,parent_path,audit_path,Path(__file__))}
    for helper in ('pitch_attack_queue.py','evaluate_keyboard_confirmation.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    modes=['legacy','edge4','edge4_onset']
    directory=ROOT/'build/pitch_attack_model_screen'
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',dict(inputs=inputs,cadences=['primary_500ms','dense_50ms'],modes=modes,
        note_threshold=.3,onset_threshold=.5,maximum_request_age_seconds=.15,
        availability='Latest pending single-worker simulation; measured execution rounded upward to input samples; consume only completed results'))
    results={}
    for name,recording in evidence['recordings'].items():
        path=evidence_path.parent/(name+'.tsv')
        assert digest(path)==recording['sha256']
        inputs[str(path.relative_to(ROOT))]=digest(path)
        rate=recording['rate']
        hop=round(rate*.05)
        events=[]
        with path.open() as stream:
            for end,group in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
                rows=list(group)
                assert len(rows)==88
                events.append(dict(end_sample=end,wall_ms=float(rows[0]['wall_ms']),cpu_ms=float(rows[0]['cpu_ms']),
                                   notes={int(r['midi']):{k:float(r[k]) for k in ('legacy','edge4_note','edge4_onset')} for r in rows}))
        base={(c['end_sample'],c['midi']) for c in parent['results'][name]['accepted']}
        for cadence in ('primary_500ms','dense_50ms'):
            requests=events if cadence=='dense_50ms' else [e for e in events if (e['end_sample']-events[0]['end_sample'])%(10*hop)==0]
            queue=simulate_latest(requests,rate)
            cost=sum(requests[r['event_index']]['cpu_ms'] for r in queue)/(events[-1]['end_sample']/rate*1000)
            for mode in modes:
                accepted=[]
                metrics=dict(cells=0,held_seconds=0.,unsupported_seconds=0.,without_available_model=0)
                for case in audit['recordings'][name]['cases']:
                    endpoint,midi=case['end_sample'],case['midi']
                    if (endpoint,midi) not in base:
                        continue
                    latest=available_result(queue,endpoint,round(rate*.15))
                    if latest is None:
                        metrics['without_available_model']+=1
                        continue
                    note=requests[latest['event_index']]['notes'][midi]
                    allowed=note['legacy']>=.3 if mode=='legacy' else note['edge4_note']>=.3
                    if mode=='edge4_onset':
                        allowed=allowed and note['edge4_onset']>=.5
                    if not allowed:
                        continue
                    assert latest['completed_sample']<=endpoint and latest['model_end_sample']<=endpoint
                    accepted.append(dict(end_sample=endpoint,midi=midi,model_end_sample=latest['model_end_sample'],completed_sample=latest['completed_sample']))
                    metrics['cells']+=1
                    metrics['held_seconds']+=case['held_seconds']
                    metrics['unsupported_seconds']+=case['unsupported_seconds']
                timing=score_acceptances(name,accepted)
                key=cadence+'-'+mode
                results.setdefault(key,{})[name]=dict(metrics=metrics,timing=timing,accepted=accepted,
                    queue=dict(requests=len(requests),processed=len(queue),dropped=len(requests)-len(queue),estimated_worker_core_share=cost))
                print(name,key,json.dumps({k:v for k,v in results[key][name].items() if k!='accepted'}),flush=True)
    decisions={}
    for mode,records in results.items():
        gain=sum(r['timing']['matched_attacks']['after']-r['timing']['matched_attacks']['before'] for r in records.values())
        unsupported=sum(r['metrics']['unsupported_seconds'] for r in records.values())
        decisions[mode]=dict(attack_gain=gain,unsupported_seconds=unsupported,
            isolated_additions=sum(r['timing']['isolated_additions'] for r in records.values()),
            decision='requires_native_envelope_verification' if gain>0 and unsupported<1e-8 else 'reject_or_no_attack_gain')
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    atomic_json(directory/'report.json',dict(inputs=inputs,results=results,decisions=decisions,
        scope='Training-development only, hypothetical single-hop additions. Isolated additions are not waived as a runtime gate. Measured inference cost drives a queue simulation, not hardware-paced analyzer/worker latency qualification. No calibration, new held-out access or native behavior changes.'))
    print(json.dumps(decisions,indent=2),flush=True)


if __name__=='__main__':
    main()
