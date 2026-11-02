#!/usr/bin/env python3
"""Freeze an acoustic-piano context screen before evaluating held identities."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import hashlib
import json
from pathlib import Path
import numpy as np
from evaluate_next_detection import fit_forest
from evaluate_guitar_duplicate_model import lower_probability
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    pointer = json.loads((ROOT/'build/piano_context_data/current.json').read_text())
    path = ROOT/pointer['report']
    assert digest(path) == pointer['sha256']
    captured = json.loads(path.read_text())
    assert captured['complete']
    data = captured['data']
    cohorts = {name: [r for r in data if r['cohort']==name] for name in ('training','calibration','heldout')}
    groups = {name: {r['group'] for r in rows} for name,rows in cohorts.items()}
    assert all(not groups[a]&groups[b] for a,b in (('training','calibration'),('training','heldout'),('calibration','heldout')))
    train = cohorts['training']
    _, model = fit_forest(np.array([r['values'] for r in train]), np.array([r['label'] for r in train]), 2)
    negatives = [r for name in ('training','calibration') for r in cohorts[name] if r['label']==1]
    negative_max = max(lower_probability(model,r['values']) for r in negatives)
    # An impossible cutoff rejects the experiment; never clamp to admit a known
    # negative at probability one.
    threshold = max(.99, negative_max+.001)
    inputs = dict(data=pointer, scripts={p:digest(ROOT/p) for p in (
        'scripts/evaluate_piano_context.py','scripts/evaluate_next_detection.py','scripts/evaluate_guitar_duplicate_model.py')},
        rule='24 depth-eight trees; class zero acoustic piano; cutoff max(.99, fitting/calibration negative maximum+.001)',
        scope='Frame classification only; no native runtime or note-recovery promotion')
    frozen = dict(inputs=inputs,model=model,threshold=threshold,negative_max=negative_max)
    directory = ROOT/'build/piano_context_model'/hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    frozen_path = directory/'frozen.json'
    atomic_json(frozen_path,frozen)
    frozen_hash = digest(frozen_path)
    metrics = {}
    for name, rows in cohorts.items():
        predictions = [(r,lower_probability(model,r['values'])) for r in rows]
        accepted = [(r,p) for r,p in predictions if p>=threshold]
        metrics[name] = dict(rows=len(rows),groups=len(groups[name]),
            piano_rows=sum(r['label']==0 for r in rows),negative_rows=sum(r['label']==1 for r in rows),
            accepted_piano=sum(r['label']==0 for r,p in accepted),accepted_negative=sum(r['label']==1 for r,p in accepted),
            maximum_negative=max((p for r,p in predictions if r['label']==1),default=None),
            accepted_groups=sorted({r['group'] for r,p in accepted}),
            negative_failures=[dict(sample=r['sample'],group=r['group'],end_sample=r['end_sample'],rate=r['rate'],probability=p)
                               for r,p in accepted if r['label']==1])
        print(name,json.dumps(metrics[name]),flush=True)
    passed = threshold<=1 and metrics['calibration']['accepted_piano']>0 and not metrics['heldout']['accepted_negative']
    report = dict(inputs=inputs,frozen=str(frozen_path.relative_to(ROOT)),frozen_sha256=frozen_hash,
                  threshold=threshold,metrics=metrics,decision='requires_note_replay' if passed else 'reject',
                  limitation='No held-out positive performances in this screen. Five sampled contexts per negative clip are not continuous replay coverage. No latency or native parity claim.')
    assert digest(frozen_path)==frozen_hash and digest(path)==pointer['sha256']
    atomic_json(directory/'report.json',report)
    atomic_json(directory.parent/'current.json',dict(report=str((directory/'report.json').relative_to(ROOT)),sha256=digest(directory/'report.json')))
    print('Context screen:',report['decision'],str((directory/'report.json').relative_to(ROOT)),flush=True)


if __name__=='__main__':
    main()
