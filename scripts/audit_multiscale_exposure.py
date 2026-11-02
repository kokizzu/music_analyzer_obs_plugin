#!/usr/bin/env python3
"""Explain frozen multiwindow decisions without fitting another detector."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
import math
from pathlib import Path
import numpy as np
from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge
from screen_multiscale_low_keyboard import OriginalHistory


def geometry(rate,seconds):
    count=round(rate*seconds)
    hann=np.hanning(count)
    frequency=np.array([440*2**((m-69)/12) for m in range(21,40)])
    times=np.arange(count)/rate
    weights=np.exp(-2j*np.pi*np.concatenate((frequency,frequency*3))[:,None]*times)*hann
    return count,hann,float(hann.sum()),weights


def project(audio,endpoint,g):
    count,hann,total,weights=g
    if endpoint<count:
        return None
    values=np.asarray(audio[endpoint-count:endpoint],dtype=float)
    centered=values-float(hann@values)/total
    rms=math.sqrt(max(0.,float(hann@(centered*centered))/total))
    return np.abs(weights@centered)*2/total/max(math.sqrt(2)*rms,1e-12)


def main():
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    frozen_path=ROOT/'build/multiscale_low_keyboard_fresh/frozen-8a1371232dc7af1a.json'
    baseline,frozen=(json.loads(p.read_text()) for p in (baseline_path,frozen_path))
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (baseline_path,frozen_path,Path(__file__))}
    for helper in ('screen_multiscale_low_keyboard.py','audit_keyboard_recovery.py','midi_sustain_reference.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    sources=[]
    for phase,ptr in frozen['phases'].items():
        path=ROOT/ptr['report']
        assert digest(path)==ptr['sha256']
        inputs[str(path.relative_to(ROOT))]=digest(path)
        report=json.loads(path.read_text())
        for name,row in report['recordings'].items():
            sample=next(s for s in baseline['selection'] if s['id']==name)
            sources.append(dict(name=name,phase=phase,frames=path.parent/(name+'.tsv'),frames_sha256=row['sha256'],
                raw=baseline_path.parent/(name+'.f32'),raw_sha256=baseline['recordings'][name]['prefix_sha256'],
                rate=baseline['recordings'][name]['rate'],sample=sample))
    for sample in frozen['selection']:
        directory=frozen_path.parent/frozen_path.stem/sample['id']
        path=directory/'report.json'
        report=json.loads(path.read_text())
        assert report['complete'] and report['frozen_sha256']==digest(frozen_path)
        assert all(digest(ROOT/p)==h for p,h in report['artifacts'].items())
        inputs[str(path.relative_to(ROOT))]=digest(path)
        sources.append(dict(name=sample['id'],phase='fresh',frames=directory/'pair.tsv',frames_sha256=digest(directory/'pair.tsv'),
            raw=directory/'prefix.f32',raw_sha256=digest(directory/'prefix.f32'),rate=report['rate'],sample=sample))
    recordings={}
    for source in sources:
        assert digest(source['frames'])==source['frames_sha256'] and digest(source['raw'])==source['raw_sha256']
        sample=source['sample']
        midi=ROOT/sample['midi']
        assert digest(midi)==sample['midi_sha256']
        for path in (source['frames'],source['raw'],midi):
            inputs[str(path.relative_to(ROOT))]=digest(path)
        allowed={}
        for note in read_intervals(midi.read_bytes()):
            if note['channel']!=9:
                allowed.setdefault(note['midi'],[]).append((note['start'],note['end']+.3))
        allowed={m:merge(v) for m,v in allowed.items()}
        rate=source['rate']
        audio=np.fromfile(source['raw'],dtype='<f4')
        geometries={seconds:geometry(rate,seconds) for seconds in (.1,.4)}
        history=OriginalHistory()
        origins={}
        totals=dict(low_cells=0,low_unsupported_seconds=0.,eligible_unsupported_seconds=0.,actual_removed=0,
                    would_reject_but_not_removed=0,removed_unsupported_seconds=0.)
        protected={}
        with source['frames'].open() as stream:
            for row in csv.DictReader(stream,delimiter='\t'):
                endpoint=int(row['end_sample'])
                current={int(v) for v in row['keys'].split(',') if v and 21<=int(v)<40}
                origins={m:v for m,v in origins.items() if m in current}
                supported=set()
                needed=current-history.latched
                if needed:
                    for seconds,g in geometries.items():
                        values=project(audio,endpoint,g)
                        if values is None:
                            continue
                        for m in needed:
                            for harmonic,offset in ((1,0),(3,19)):
                                if values[m-21+offset]>=.01:
                                    supported.add(m)
                                    origins.setdefault(m,str(seconds)+'s-harmonic-'+str(harmonic))
                                    break
                ready=endpoint>=round(rate*.4)
                stable={m for m in current if ready and history.stable.get(m,0)>=3}
                rejected=history.finish(current,supported,ready)
                before,after=({int(v) for v in row[k].split(',') if v} for k in ('keys','after_keys'))
                removed=before-after
                assert removed<=rejected,'Offline evidence failed to explain native removal'
                totals['actual_removed']+=len(removed)
                totals['would_reject_but_not_removed']+=len(rejected-removed)
                start,end=endpoint/rate,min(len(audio)/rate,endpoint/rate+.05)
                for m in current:
                    unsupported=max(0.,end-start-coverage(allowed.get(m,[]),start,end))
                    totals['low_cells']+=1
                    totals['low_unsupported_seconds']+=unsupported
                    if m in stable:
                        totals['eligible_unsupported_seconds']+=unsupported
                        if m not in rejected:
                            origin=origins[m]
                            protected[origin]=protected.get(origin,0.)+unsupported
                    if m in removed:
                        totals['removed_unsupported_seconds']+=unsupported
        recordings[source['name']]=dict(phase=source['phase'],metrics=totals,protected_unsupported_seconds_by_first_evidence=protected)
        print(source['name'],json.dumps(recordings[source['name']]),flush=True)
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    directory=ROOT/'build/multiscale_exposure_audit'
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'report.json',dict(inputs=inputs,recordings=recordings,
        scope='Post-evaluation explanation of fitting/calibration and already evaluated fresh recordings only. No threshold changes, new held-out access or detector integration. Eligibility here covers all low display cells; actual native removal additionally requires late low-note insertion.'))


if __name__=='__main__':
    main()
