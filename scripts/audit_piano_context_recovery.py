#!/usr/bin/env python3
"""Apply the frozen context model to existing restoration counterexamples."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv
import json
from pathlib import Path
import numpy as np
from evaluate_guitar_duplicate_model import lower_probability
from piano_context_features import features
from routing_duration_baseline import ROOT, atomic_json, digest
from validate_routing_consensus import prepare


def main():
    pointer=json.loads((ROOT/'build/piano_context_model/current.json').read_text())
    model_path=ROOT/pointer['report']
    assert digest(model_path)==pointer['sha256']
    screen=json.loads(model_path.read_text())
    frozen_path=ROOT/screen['frozen']
    assert digest(frozen_path)==screen['frozen_sha256']
    frozen=json.loads(frozen_path.read_text())
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline=json.loads(baseline_path.read_text())
    sources=[]
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (model_path,frozen_path,baseline_path,Path(__file__),ROOT/'scripts/piano_context_features.py')}
    for phase in ('training','calibration'):
        pointer_path=ROOT/('build/joint_body_measurement/current-'+phase+'.json')
        ptr=json.loads(pointer_path.read_text())
        path=ROOT/ptr['report']
        assert digest(path)==ptr['sha256']
        report=json.loads(path.read_text())
        inputs[str(path.relative_to(ROOT))]=digest(path)
        for name,row in report['recordings'].items():
            sources.append((phase,name,path.parent/(name+'.tsv'),row['sha256'],
                            baseline_path.parent/(name+'.f32'),baseline['recordings'][name]['prefix_sha256'],baseline['recordings'][name]['rate']))
    directory=ROOT/'build/joint_body_controls/28eb805570ce51ef'
    plan_path=directory/'plan.json'
    plan=json.loads(plan_path.read_text())
    inputs[str(plan_path.relative_to(ROOT))]=digest(plan_path)
    samples={s['id']:s for s in plan['cases']}
    for shard in range(4):
        path=directory/('report-'+str(shard)+'.json')
        report=json.loads(path.read_text())
        assert report['complete']
        inputs[str(path.relative_to(ROOT))]=digest(path)
        for name,row in report['recordings'].items():
            if row['added']:
                raw,rate=prepare(samples[name],directory)
                assert rate==row['rate']
                sources.append(('controls-'+samples[name]['family'],name,directory/(name+'.tsv'),row['sha256'],
                                raw,row['raw_sha256'],rate))
    results=[]
    for phase,name,path,sha,raw,raw_sha,rate in sources:
        assert digest(path)==sha and digest(raw)==raw_sha
        inputs[str(path.relative_to(ROOT))],inputs[str(raw.relative_to(ROOT))]=sha,raw_sha
        count=round(rate*.1)
        audio=np.pad(np.fromfile(raw,dtype='<f4'),(count,0))
        with path.open() as stream:
            for row in csv.DictReader(stream,delimiter='\t'):
                before,after=({int(v) for v in row[k].split(',') if v} for k in ('keys','after_keys'))
                if not after-before:
                    continue
                endpoint=int(row['end_sample'])
                vector=features(audio[endpoint:endpoint+count],rate)
                probability=0. if vector is None else lower_probability(frozen['model'],vector)
                for midi in sorted(after-before):
                    results.append(dict(phase=phase,sample=name,end_sample=endpoint,midi=midi,
                                        probability=probability,accepted=probability>=frozen['threshold']))
    summary={phase:dict(proposed=sum(r['phase']==phase for r in results),accepted=sum(r['phase']==phase and r['accepted'] for r in results),
                        maximum_probability=max(r['probability'] for r in results if r['phase']==phase)) for phase in sorted({r['phase'] for r in results})}
    output=ROOT/'build/piano_context_recovery/report.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    atomic_json(output,dict(inputs=inputs,threshold=frozen['threshold'],results=results,summary=summary,
        scope='Known restoration proposals only; post-screen usefulness audit, not fresh held-out proof or a native implementation. No threshold tuning.'))
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    main()
