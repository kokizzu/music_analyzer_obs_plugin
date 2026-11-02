#!/usr/bin/env python3
"""Training-only short/long causal support for late low-note insertions."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from routing_duration_baseline import ROOT, atomic_json, digest


class OriginalHistory:
    def __init__(self):
        self.stable={}
        self.latched=set()

    def finish(self,current,supported,ready):
        self.latched.intersection_update(current)
        self.latched.update(current & supported)
        rejected={m for m in current if ready and self.stable.get(m,0)>=3 and m not in self.latched}
        self.stable={m:min(3,self.stable.get(m,0)+1) for m in current}
        return rejected


def main():
    source_path=ROOT/'build/keyboard_stage_trace/034803c68151329e/report.json'
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    source,baseline=(json.loads(p.read_text()) for p in (source_path,baseline_path))
    assert source['complete']
    inputs=dict(trace_sha256=digest(source_path),baseline_sha256=digest(baseline_path),script_sha256=digest(Path(__file__)),
                helper_sha256=digest(ROOT/'scripts/routing_duration_baseline.py'),windows=[.1,.4],floor=.01,
                rule='Union of exact fundamental or third-harmonic support, latched only while original pitch remains visible; three prior original visible hops and .4 s warmup before removal',
                numpy_version=np.__version__)
    directory=ROOT/'build/multiscale_low_keyboard'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'plan.json',inputs)
    results={}
    for name,recording in source['recordings'].items():
        assert name in ('training-1','training-2','training-3')
        raw=baseline_path.parent/(name+'.f32')
        frames_path=source_path.parent/(name+'.frames.tsv')
        assert digest(raw)==baseline['recordings'][name]['prefix_sha256']
        assert digest(frames_path)==recording['frames_sha256']
        rate=baseline['recordings'][name]['rate']
        audio=np.fromfile(raw,dtype='<f4').astype(float)
        geometry={}
        frequencies=np.array([440*2**((m-69)/12) for m in range(21,40)])
        for seconds in inputs['windows']:
            count=round(seconds*rate)
            hann=np.hanning(count)
            times=np.arange(count)/rate
            weights=np.exp(-2j*np.pi*np.concatenate((frequencies,frequencies*3))[:,None]*times)*hann
            geometry[seconds]=(count,hann,float(hann.sum()),weights)
        candidates={}
        for case in recording['low_cases']:
            candidates.setdefault(case['end_sample'],{})[case['midi']]=case
        history=OriginalHistory()
        metrics=dict(cells=0,held_removed_seconds=0.,supported_removed_seconds=0.,unsupported_removed_seconds=0.)
        removed=[]
        with frames_path.open() as stream:
            for frame in csv.DictReader(stream,delimiter='\t'):
                endpoint=int(frame['end_sample'])
                current={int(v) for v in frame['keys'].split(',') if v and 21<=int(v)<40}
                supported=set()
                needed=current-history.latched
                for count,hann,total,weights in geometry.values():
                    if endpoint<count or not needed:
                        continue
                    values=audio[endpoint-count:endpoint]
                    centered=values-float(hann@values)/total
                    rms=math.sqrt(max(0.,float(hann@(centered*centered))/total))
                    indices=sorted(needed)
                    rows=[m-21 for m in indices]+[m-21+19 for m in indices]
                    projection=np.abs(weights[rows]@centered)*2/total/max(math.sqrt(2)*rms,1e-12)
                    supported.update(m for i,m in enumerate(indices) if max(projection[i],projection[i+len(indices)])>=inputs['floor'])
                rejected=history.finish(current,supported,endpoint>=round(.4*rate))
                for midi in sorted(rejected & candidates.get(endpoint,{}).keys()):
                    case=candidates[endpoint][midi]
                    metrics['cells']+=1
                    for key in ('held_seconds','supported_seconds','unsupported_seconds'):
                        metrics[key.replace('_seconds','_removed_seconds')]+=case[key]
                    removed.append(dict(end_sample=endpoint,midi=midi,held_seconds=case['held_seconds'],supported_seconds=case['supported_seconds']))
        results[name]=dict(metrics=metrics,removed=removed,raw_sha256=digest(raw),frames_sha256=digest(frames_path))
        print(name,json.dumps(metrics),flush=True)
    aggregate={k:sum(r['metrics'][k] for r in results.values()) for k in next(iter(results.values()))['metrics']}
    passed=aggregate['unsupported_removed_seconds']>0 and aggregate['supported_removed_seconds']<1e-8
    atomic_json(directory/'report.json',dict(inputs=inputs,recordings=results,aggregate=aggregate,
        decision='requires_native_calibration' if passed else 'reject',
        scope='Training-only original-display replay of one fixed multiwindow hypothesis. No calibration, held-out, controls or latency claim. No native changes.'))
    atomic_json(directory.parent/'current.json',dict(report=str((directory/'report.json').relative_to(ROOT)),sha256=digest(directory/'report.json')))
    print(json.dumps(aggregate),str((directory/'report.json').relative_to(ROOT)),flush=True)


if __name__=='__main__':
    main()
