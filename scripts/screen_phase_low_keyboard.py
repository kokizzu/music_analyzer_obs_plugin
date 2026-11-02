#!/usr/bin/env python3
"""Training-only fixed phase/long-window union; no held-out parameter search."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
from pathlib import Path
import numpy as np
from phase_low_keyboard_reference import geometry,projection,short_support
from screen_multiscale_low_keyboard import OriginalHistory
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT,atomic_json,digest
from routing_duration_score import score


def main():
    source_path=ROOT/'build/keyboard_stage_trace/034803c68151329e/report.json'
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    source,baseline=(json.loads(p.read_text()) for p in (source_path,baseline_path))
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (source_path,baseline_path,Path(__file__))}
    for helper in ('phase_low_keyboard_reference.py','audit_multiscale_exposure.py','screen_multiscale_low_keyboard.py','midi_sustain_reference.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    recordings={}
    for name,entry in source['recordings'].items():
        assert name in ('training-1','training-2','training-3')
        raw=baseline_path.parent/(name+'.f32')
        frames_path=source_path.parent/(name+'.frames.tsv')
        assert digest(raw)==baseline['recordings'][name]['prefix_sha256'] and digest(frames_path)==entry['frames_sha256']
        for p in (raw,frames_path):
            inputs[str(p.relative_to(ROOT))]=digest(p)
        sample=next(s for s in baseline['selection'] if s['id']==name)
        midi=ROOT/sample['midi']
        assert digest(midi)==sample['midi_sha256']
        inputs[str(midi.relative_to(ROOT))]=digest(midi)
        notes=read_intervals(midi.read_bytes())
        audio=np.fromfile(raw,dtype='<f4')
        rate=baseline['recordings'][name]['rate']
        hop=round(rate*.05)
        geometries={t:geometry(rate,t) for t in (.1,.4)}
        cases={}
        for case in entry['low_cases']:
            cases.setdefault(case['end_sample'],{})[case['midi']]=case
        with frames_path.open() as stream:
            frames=list(csv.DictReader(stream,delimiter='\t'))
        history=OriginalHistory()
        previous=None
        proposed=[]
        removed=[]
        metrics=dict(cells=0,held_removed_seconds=0.,supported_removed_seconds=0.,unsupported_removed_seconds=0.)
        for index,row in enumerate(frames,1):
            endpoint=int(row['end_sample'])
            assert endpoint==index*hop
            current=projection(audio,endpoint,geometries[.1])
            short=short_support(previous,current,hop/rate)
            previous=current
            long=projection(audio,endpoint,geometries[.4])
            supported=short|({m+21 for m in range(19) if max(abs(long[m]),abs(long[m+19]))>=.01} if long is not None else set())
            original={int(v) for v in row['keys'].split(',') if v}
            rejected=history.finish({m for m in original if 21<=m<40},supported,endpoint>=round(rate*.4))
            selected=rejected&cases.get(endpoint,{}).keys()
            proposed.append(dict(row,keys=','.join(str(m) for m in sorted(original-selected))))
            for m in selected:
                case=cases[endpoint][m]
                metrics['cells']+=1
                for key in ('held_seconds','supported_seconds','unsupported_seconds'):
                    metrics[key.replace('_seconds','_removed_seconds')]+=case[key]
                removed.append(dict(end_sample=endpoint,midi=m,held_seconds=case['held_seconds'],supported_seconds=case['supported_seconds']))
        before,after=(score(rows,notes,rate)['keys'] for rows in (frames,proposed))
        recordings[name]=dict(metrics=metrics,removed=removed,before_attacks=before['matched_attacks'],after_attacks=after['matched_attacks'])
        print(name,json.dumps({k:v for k,v in recordings[name].items() if k!='removed'}),flush=True)
    aggregate={key:sum(r['metrics'][key] for r in recordings.values()) for key in metrics}
    passed=aggregate['unsupported_removed_seconds']>0 and aggregate['supported_removed_seconds']<1e-8 and all(r['after_attacks']>=r['before_attacks'] for r in recordings.values())
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    directory=ROOT/'build/phase_low_keyboard_screen'
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'report.json',dict(inputs=inputs,recordings=recordings,aggregate=aggregate,
        parameters=dict(amplitude_floor=.01,phase_cents=25,short_seconds=.1,long_seconds=.4,previous_visible=3),
        decision='requires_native_calibration' if passed else 'reject',
        scope='Single fixed training-only hypothesis. Two adjacent causal short windows must have amplitude support and phase-derived frequency within 25 cents; long-window support unchanged. No calibration or new held-out access, parameter search or runtime changes.'))
    print('Phase screen:',json.dumps(aggregate),'passed',passed,flush=True)


if __name__=='__main__':
    main()
