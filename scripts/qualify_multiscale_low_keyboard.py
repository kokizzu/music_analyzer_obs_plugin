#!/usr/bin/env python3
"""Recompute completed preservation and latency evidence without promotion."""
import csv
import json
from pathlib import Path
from routing_duration_baseline import ROOT, atomic_json, digest
from validate_low_keyboard_controls import inspect


def read(path):
    return json.loads(path.read_text())


def main():
    frozen_path=ROOT/'build/multiscale_low_keyboard_fresh/frozen-8a1371232dc7af1a.json'
    frozen=read(frozen_path)
    build_path=ROOT/frozen['build']
    assert digest(build_path)==frozen['build_sha256']
    build=read(build_path)
    assert digest(build_path.parent/'pair')==build['binary_sha256']
    directory=ROOT/'build/multiscale_low_keyboard_controls/02e823638e79b6e3'
    plan_path=directory/'plan.json'
    plan=read(plan_path)
    assert plan['build_sha256']==digest(build_path) and plan['frozen_sha256']==digest(frozen_path)
    assert plan['script_sha256']==digest(ROOT/'scripts/validate_multiscale_controls.py')
    assert all(digest(ROOT/p)==h for p,h in plan['helpers'].items())
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (frozen_path,build_path,plan_path,Path(__file__))}
    for helper in ('routing_duration_baseline.py','validate_low_keyboard_controls.py','midi_sustain_reference.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    totals=dict(cases=0,windows=0,removed=0,added=0,correct_any_losses=0,correct_keyboard_losses=0,
                unrelated_changes=0,tempo_changes=0,survivor_changes=0,deadline_misses=0)
    failures=[]
    piano_performances={}
    removed_by_family={}
    isolated_keyboard_wrong_pitches_removed=0
    for shard in range(4):
        path=directory/('report-'+str(shard)+'.json')
        report=read(path)
        assert report['complete'] and report['plan_sha256']==digest(plan_path)
        inputs[str(path.relative_to(ROOT))]=digest(path)
        selected=plan['cases'][shard::4]
        assert set(report['recordings'])=={s['id'] for s in selected}
        shard_passed=True
        for sample in selected:
            row=report['recordings'][sample['id']]
            path=directory/(sample['id']+'.tsv')
            assert digest(path)==row['sha256']
            # Read the ingested PCM without regenerating or overwriting it.
            raw=directory/(sample['id']+'.f32') if sample['fresh'] else ROOT/sample['raw']
            rate=row['rate']
            if sample['fresh']:
                assert digest(ROOT/sample['audio'])==sample['audio_sha256']
                if sample.get('target_rate'):
                    assert rate==sample['target_rate']
            else:
                assert rate==sample['rate'] and digest(raw)==sample['raw_sha256']
            assert rate==row['rate'] and digest(raw)==row['raw_sha256']
            assert raw.stat().st_size//4//int(rate*.05+.5)==row['windows']
            expected=None
            if 'reference' in sample:
                reference=ROOT/sample['reference']
                assert digest(reference)==sample['reference_sha256']
                with reference.open() as stream:
                    expected={r['end_sample']:r for r in csv.DictReader(stream,delimiter='\t')}
            actual=inspect(path,sample,rate,expected)
            assert all(actual[k]==row[k] for k in actual)
            with path.open() as stream:
                assert sum(r['survivor_changed']!='0' for r in csv.DictReader(stream,delimiter='\t'))==row['survivor_changes']
            totals['cases']+=1
            for key in ('windows','removed','added','correct_any_losses','correct_keyboard_losses','unrelated_changes','tempo_changes','survivor_changes'):
                totals[key]+=row[key]
            totals['deadline_misses']+=row['after_ms']['deadline_misses']
            removed_by_family[sample['family']]=removed_by_family.get(sample['family'],0)+row['removed']
            if sample['family']=='piano' and 'expected_midi' in sample:
                isolated_keyboard_wrong_pitches_removed+=row['removed']-row['correct_keyboard_losses']
            if sample['family']=='piano' and 'midi' in sample:
                piano_performances[sample['id']]=dict(removed=row['removed'],correct_losses=row['correct_keyboard_losses'])
            failed=any(row[k] for k in ('added','correct_any_losses','correct_keyboard_losses','unrelated_changes','tempo_changes','survivor_changes')) or row['after_ms']['deadline_misses']
            if failed:
                failures.append(sample['id'])
                shard_passed=False
        assert report['passed']==shard_passed
    assert totals['cases']==1154 and totals['windows']==94834
    latency=[]
    parent=ROOT/'build/multiscale_low_keyboard_latency'
    for path in sorted(parent.glob('*/report.json')):
        report=read(path)
        if report['inputs']['build_sha256']==digest(build_path):
            latency.append((path,report))
    assert len(latency)<=1,'Do not choose a favorable latency repetition'
    latency_passed=False
    if latency:
        path,report=latency[0]
        assert report['complete'] and report['inputs']['script_sha256']==digest(ROOT/'scripts/benchmark_multiscale_low_keyboard.py')
        assert report['inputs']['gates']==dict(after_wall_p99_ms=50.,after_cpu_max_ms=50.,mean_added_cpu_ms=1.,p99_added_cpu_ms=2.)
        inputs[str(path.relative_to(ROOT))]=digest(path)
        delta,wall,cpu=[],[],[]
        assert len(report['repetitions'])==5
        for i,rep in enumerate(report['repetitions']):
            trace=path.parent/('pass-'+str(i)+'.tsv')
            assert digest(trace)==rep['sha256']
            with trace.open() as stream:
                rows=list(csv.DictReader(stream,delimiter='\t'))
            assert len(rows)==rep['windows']==200
            for row in rows:
                assert not row['unrelated_difference'] and row['bpm_changed']==row['survivor_changed']=='0'
                delta.append(float(row['after_cpu_ms'])-float(row['before_cpu_ms']))
                wall.append(float(row['after_ms']));cpu.append(float(row['after_cpu_ms']))
        actual=dict(windows=len(wall),after_wall_p99_ms=sorted(wall)[int((len(wall)-1)*.99)],after_wall_max_ms=max(wall),
                    after_cpu_max_ms=max(cpu),mean_added_cpu_ms=sum(delta)/len(delta),p99_added_cpu_ms=sorted(delta)[int((len(delta)-1)*.99)],
                    wall_deadline_misses=sum(v>50 for v in wall))
        assert actual==report['metrics']
        latency_passed=all(actual[k]<limit for k,limit in report['inputs']['gates'].items())
        assert report['passed']==latency_passed
    fresh_gain=0.
    for sample in frozen['selection']:
        path=frozen_path.parent/frozen_path.stem/sample['id']/'report.json'
        report=read(path)
        assert report['complete'] and report['frozen_sha256']==digest(frozen_path)
        inputs[str(path.relative_to(ROOT))]=digest(path)
        fresh_gain+=report['deltas']['unsupported_removed']
    output=ROOT/'build/multiscale_low_keyboard_qualification/report.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    result=dict(inputs=inputs,preservation=totals,preservation_passed=not failures,failures=failures,
                piano_performances=piano_performances,
                removed_by_family=removed_by_family,isolated_keyboard_wrong_pitches_removed=isolated_keyboard_wrong_pitches_removed,
                latency_run=bool(latency),latency_passed=latency_passed,fresh_unsupported_removed_seconds=fresh_gain,
                promote=False,scope='Frozen experimental trial only. Fresh-recording benefit remains unproven; no production integration.')
    atomic_json(output,result)
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'},indent=2),flush=True)


if __name__=='__main__':
    main()
