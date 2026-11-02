#!/usr/bin/env python3
"""Current-input inference quality bound, explicitly not an availability replay."""
import csv
import json
import math
from itertools import groupby
from pathlib import Path
from evaluate_keyboard_confirmation import score_acceptances
from routing_duration_baseline import ROOT,atomic_json,digest


def read(path):
    return json.loads(path.read_text())


def main():
    pointer=read(ROOT/'build/pitch_attack_evidence/current.json')
    path=ROOT/pointer['report']
    evidence=read(path)
    assert evidence['complete'] and digest(path)==pointer['sha256']
    parent_path=ROOT/'build/real_piano_dictionary_transfer/cfb32e5534dc943f/report.json'
    parent=read(parent_path)
    audit_path=ROOT/'build/keyboard_confirmation_audit.json'
    audit=read(audit_path)
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (path,parent_path,audit_path,Path(__file__))}
    for helper in ('evaluate_keyboard_confirmation.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    directory=ROOT/'build/pitch_attack_ondemand_bound'
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',dict(inputs=inputs,modes=['legacy','edge4','edge4_onset'],note_threshold=.3,onset_threshold=.5,
        scope='Same-input model quality upper bound only. Current inference finishes after the analysis endpoint. No claim of cached-result availability, bounded analyzer wait or production latency.'))
    results={}
    for name,recording in evidence['recordings'].items():
        target=path.parent/(name+'.tsv')
        assert digest(target)==recording['sha256']
        inputs[str(target.relative_to(ROOT))]=digest(target)
        events={}
        with target.open() as stream:
            for end,group in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
                rows=list(group)
                events[end]=dict(wall_ms=float(rows[0]['wall_ms']),cpu_ms=float(rows[0]['cpu_ms']),
                    notes={int(r['midi']):{k:float(r[k]) for k in ('legacy','edge4_note','edge4_onset')} for r in rows})
        base={(c['end_sample'],c['midi']) for c in parent['results'][name]['accepted']}
        requested={end for end,midi in base if end in events}
        cost=sum(events[end]['cpu_ms'] for end in requested)/(60*1000)
        for mode in ('legacy','edge4','edge4_onset'):
            accepted=[]
            metrics=dict(cells=0,held_seconds=0.,unsupported_seconds=0.)
            for case in audit['recordings'][name]['cases']:
                end,midi=case['end_sample'],case['midi']
                if (end,midi) not in base or end not in events:
                    continue
                event=events[end]
                note=event['notes'][midi]
                allowed=note['legacy']>=.3 if mode=='legacy' else note['edge4_note']>=.3
                if mode=='edge4_onset':
                    allowed=allowed and note['edge4_onset']>=.5
                if not allowed:
                    continue
                completed=end+math.ceil(event['wall_ms']*recording['rate']/1000)
                assert completed>end
                accepted.append(dict(end_sample=end,midi=midi,model_end_sample=end,completed_sample=completed))
                metrics['cells']+=1
                metrics['held_seconds']+=case['held_seconds']
                metrics['unsupported_seconds']+=case['unsupported_seconds']
            timing=score_acceptances(name,accepted)
            results.setdefault(mode,{})[name]=dict(metrics=metrics,timing=timing,accepted=accepted,
                requests=len(requested),estimated_worker_core_share=cost)
            print(name,mode,json.dumps({k:v for k,v in results[mode][name].items() if k!='accepted'}),flush=True)
    summary={mode:dict(attack_gain=sum(r['timing']['matched_attacks']['after']-r['timing']['matched_attacks']['before'] for r in records.values()),
                       unsupported_seconds=sum(r['metrics']['unsupported_seconds'] for r in records.values()),
                       cells=sum(r['metrics']['cells'] for r in records.values())) for mode,records in results.items()}
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    atomic_json(directory/'report.json',dict(inputs=inputs,results=results,summary=summary,
        scope='Unavailable-at-endpoint quality bound. Single-hop endpoint scores are optimistic and do not include model wait. A real bounded-wait native trial and timestamp-aware verification are still required before any gain claim or promotion.'))
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    main()
