#!/usr/bin/env python3
"""Separate stale smoothing tails from current detections using training MIDI."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
from pathlib import Path
import numpy as np
from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT, atomic_json, digest
from routing_duration_score import merge


def metric():
    return dict(cells=0,held_seconds=0.,pedal_only_seconds=0.,tolerance_only_seconds=0.,unsupported_seconds=0.)


def stale_tail(row,relative,explained):
    # A final note with no raw hit can have been introduced after smoothing.
    # Its tracking miss count does not describe a decaying display envelope.
    return (float(row['raw'])<=0 and float(row['smoothed'])>0 and float(row['final'])>0 and
            row['confirmed']=='1' and float(row['envelope'])>0 and int(row['misses'])>=2 and
            np.isfinite(relative) and np.isfinite(explained) and relative<.01 and explained<.01)


def main():
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    trace_path=ROOT/'build/primary_duration_trace/954041e8c8c9eb7f/report.json'
    fit_path=ROOT/'build/joint_note_coverage/017a9ad67bd36e7d/report.json'
    baseline,trace,fit=(json.loads(p.read_text()) for p in (baseline_path,trace_path,fit_path))
    assert trace['complete'] and fit['complete']
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (baseline_path,trace_path,fit_path,Path(__file__))}
    for helper in ('audit_keyboard_recovery.py','midi_sustain_reference.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    results={}
    for name,recording in trace['recordings'].items():
        assert name in ('training-1','training-2','training-3')
        sample=next(s for s in baseline['selection'] if s['id']==name)
        midi_path=ROOT/sample['midi']
        assert digest(midi_path)==sample['midi_sha256']
        intervals=[{} for _ in range(3)]
        for note in read_intervals(midi_path.read_bytes()):
            if note['channel']==9:
                continue
            for table,end in zip(intervals,(note['key_end'],note['end'],note['end']+.3)):
                table.setdefault(note['midi'],[]).append((note['start'],end))
        held,pedal,allowed=({m:merge(v) for m,v in table.items()} for table in intervals)
        path=trace_path.parent/(name+'.trace.tsv')
        arrays_path=fit_path.parent/(name+'.npz')
        assert digest(path)==recording['trace_sha256'] and digest(arrays_path)==fit['recordings'][name]['sha256']
        inputs.update({str(p.relative_to(ROOT)):digest(p) for p in (path,arrays_path,midi_path)})
        arrays=np.load(arrays_path)
        activation,projection=arrays['activation'],arrays['projection']
        relative=activation/np.maximum(activation.max(axis=0),1e-12)
        explained=activation/np.maximum(projection,1e-12)
        rate=baseline['recordings'][name]['rate']
        hop=round(rate*.05)
        groups={}
        proposals=[]
        with path.open() as stream:
            for row in csv.DictReader(stream,delimiter='\t'):
                if float(row['raw'])>0 or float(row['final'])<=0:
                    continue
                midi,endpoint=int(row['midi']),int(row['end_sample'])
                start,end=endpoint/rate,min(60.,endpoint/rate+.05)
                if end<=start:
                    continue
                index=endpoint//hop-1
                h,p,a=(coverage(table.get(midi,[]),start,end) for table in (held,pedal,allowed))
                delta=dict(cells=1,held_seconds=h,pedal_only_seconds=max(0.,p-h),tolerance_only_seconds=max(0.,a-p),unsupported_seconds=max(0.,end-start-a))
                missing=int(row['misses'])
                smoothed=float(row['smoothed'])>0
                eligible=stale_tail(row,relative[midi-21,index],explained[midi-21,index])
                bucket=str(missing) if missing<=3 else '4-6' if missing<=6 else '7-13' if missing<=13 else 'over-13'
                origin='smoothing-tail' if smoothed else 'postprocess-addition'
                for category in ('raw-absent-final',origin,origin+'-misses-'+bucket) + (('two-misses-no-joint-support',) if eligible else ()):
                    value=groups.setdefault(category,metric())
                    for key,number in delta.items():
                        value[key]+=number
                if eligible:
                    proposals.append(dict(end_sample=endpoint,midi=midi,misses=missing,relative=float(relative[midi-21,index]),
                        explained=float(explained[midi-21,index]),**delta))
        results[name]=dict(groups=groups,proposals=proposals)
        print(name,json.dumps({k:v for k,v in groups.items() if k in ('smoothing-tail','postprocess-addition','two-misses-no-joint-support')}),flush=True)
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    directory=ROOT/'build/keyboard_release_tail_audit'
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/'report.json',dict(inputs=inputs,recordings=results,numpy_version=np.__version__,
        rule='Current raw absent, smoothed and final visible, confirmed positive envelope, at least two native misses, joint relative and explained activation both below .01',
        scope='Training-only attribution and single fixed removal hypothesis. Key-held, CC64-only, tolerance-only and unsupported time reported separately. No calibration, held-out access or native behavior change.'))


if __name__=='__main__':
    main()
