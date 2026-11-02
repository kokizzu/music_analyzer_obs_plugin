#!/usr/bin/env python3
"""Score completed native envelope replays with the unchanged CC64 reference."""
import argparse
import csv
import json
from audit_keyboard_recovery import coverage
from midi_sustain_reference import read_intervals
from routing_duration_baseline import ROOT,atomic_json,digest
from routing_duration_score import merge,score


def read(path):
    return json.loads(path.read_text())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--display',action='store_true')
    args=parser.parse_args()
    prefix='pitch_attack_display_native' if args.display else 'pitch_attack_envelope_native'
    pointer=read(ROOT/'build'/prefix/'current.json')
    replay_path=ROOT/pointer['report']
    replay=read(replay_path)
    assert replay['complete'] and digest(replay_path)==pointer['sha256']
    directory=replay_path.parent
    plan_path=directory/'plan.json'
    plan=read(plan_path)
    assert digest(plan_path)==replay['plan_sha256']
    assert digest(ROOT/plan['build'])==plan['build_sha256']
    built=read(ROOT/plan['build'])
    assert digest(directory/'pair')==built['binary_sha256']
    assert digest(directory/'src/analyzer.cpp')==built['cpp_sha256']
    assert digest(directory/'src/analyzer.hpp')==built['hpp_sha256']
    assert all(digest(ROOT/p)==h for p,h in built['inputs']['assets'].items())
    if not args.display:
        assert digest(ROOT/'scripts/replay_pitch_attack_envelope.py')==built['inputs']['script_sha256']
    assert digest(directory/'evidence.json')==plan['evidence_sha256']
    evidence=read(directory/'evidence.json')
    assert all(digest(ROOT/p)==h for p,h in evidence['inputs'].items())
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline=read(baseline_path)
    reference_path=ROOT/'build/routing_consensus_pair/e63350f9b5113f8b/report.json'
    reference=read(reference_path)
    inputs={str(p.relative_to(ROOT)):digest(p) for p in (replay_path,plan_path,baseline_path,reference_path,ROOT/'scripts/score_pitch_attack_envelope.py')}
    for helper in ('audit_keyboard_recovery.py','midi_sustain_reference.py','routing_duration_score.py'):
        inputs['scripts/'+helper]=digest(ROOT/'scripts'/helper)
    results={}
    for name,checksum in replay['outputs'].items():
        assert digest(ROOT/plan['recordings'][name]['path'])==plan['recordings'][name]['sha256']
        target=directory/(name+'.tsv')
        assert digest(target)==checksum
        inputs[str(target.relative_to(ROOT))]=checksum
        expected_path=reference_path.parent/('piano-'+name+'.tsv')
        assert digest(expected_path)==reference['recordings']['piano-'+name]['sha256']
        with target.open() as stream:
            rows=list(csv.DictReader(stream,delimiter='\t'))
        with expected_path.open() as stream:
            expected=list(csv.DictReader(stream,delimiter='\t'))
        assert len(rows)==len(expected)==1200
        for row,before in zip(rows,expected):
            assert all(row[k]==before['after_'+k if k in ('guitar','voice') else k] for k in ('end_sample','bass','guitar','keys','voice','other','ambiguous','chord','bpm','confidence','drums'))
        sample=next(s for s in baseline['selection'] if s['id']==name)
        midi_path=ROOT/sample['midi']
        assert digest(midi_path)==sample['midi_sha256']
        inputs[str(midi_path.relative_to(ROOT))]=digest(midi_path)
        notes=read_intervals(midi_path.read_bytes())
        held={};allowed={}
        for note in notes:
            if note['channel']!=9:
                held.setdefault(note['midi'],[]).append((note['start'],note['key_end']))
                allowed.setdefault(note['midi'],[]).append((note['start'],note['end']+.3))
        held={m:merge(v) for m,v in held.items()}
        allowed={m:merge(v) for m,v in allowed.items()}
        rate=baseline['recordings'][name]['rate']
        sets=[{int(m) for m in row['after_keys'].split(',') if m} for row in rows]
        delta=dict(added_cells=0,removed_cells=0,held_added_seconds=0.,held_removed_seconds=0.,
            supported_removed_seconds=0.,unsupported_added_seconds=0.,isolated_additions=0,
            unrelated_changed_frames=0,tempo_changed_frames=0,surviving_cell_changed_frames=0)
        additions=[]
        removals=[]
        for i,row in enumerate(rows):
            original={int(m) for m in row['keys'].split(',') if m}
            changed=sets[i]
            start=int(row['end_sample'])/rate
            end=min(60.,start+.05)
            delta['unrelated_changed_frames']+=bool(row['unrelated_difference'])
            delta['tempo_changed_frames']+=row['bpm_changed']!='0'
            delta['surviving_cell_changed_frames']+=row['survivor_changed']!='0'
            for m in original-changed:
                delta['removed_cells']+=1
                key_held=coverage(held.get(m,[]),start,end)
                supported=coverage(allowed.get(m,[]),start,end)
                delta['held_removed_seconds']+=key_held
                delta['supported_removed_seconds']+=supported
                removals.append(dict(end_sample=int(row['end_sample']),midi=m,held_seconds=key_held,supported_seconds=supported))
            for m in changed-original:
                delta['added_cells']+=1
                supported=coverage(allowed.get(m,[]),start,end)
                delta['held_added_seconds']+=coverage(held.get(m,[]),start,end)
                delta['unsupported_added_seconds']+=end-start-supported
                isolated=m not in (sets[i-1] if i else set()) and m not in (sets[i+1] if i+1<len(sets) else set())
                delta['isolated_additions']+=isolated
                additions.append(dict(end_sample=int(row['end_sample']),midi=m,unsupported_seconds=end-start-supported,isolated=isolated))
        before_score=score(rows,notes,rate)['keys']
        after_score=score([dict(r,keys=r['after_keys']) for r in rows],notes,rate)['keys']
        safe=(delta['supported_removed_seconds']<1e-8 and delta['unsupported_added_seconds']<1e-8 and
            not any(delta[k] for k in ('unrelated_changed_frames','tempo_changed_frames','surviving_cell_changed_frames','isolated_additions')) and
            after_score['matched_attacks']>=before_score['matched_attacks'])
        results[name]=dict(deltas=delta,before=before_score,after=after_score,additions=additions,removals=removals,passed=safe)
        print(name,json.dumps(dict(deltas=delta,attack_gain=after_score['matched_attacks']-before_score['matched_attacks'],passed=safe)),flush=True)
    benefit=any(r['after']['matched_attacks']>r['before']['matched_attacks'] or
                r['deltas']['held_added_seconds']>r['deltas']['held_removed_seconds']+1e-8 for r in results.values())
    passed=benefit and all(r['passed'] for r in results.values())
    assert all(digest(ROOT/p)==h for p,h in inputs.items())
    atomic_json(directory/'score.json',dict(inputs=inputs,results=results,passed=passed,benefit=benefit,
        decision='requires_live_worker_validation' if passed else 'reject_native_display' if args.display else 'reject_native_confirmation',
        scope='Paired actual native display with captured causal evidence; development only, no live worker or production promotion.'))
    print(directory.relative_to(ROOT)/'score.json',flush=True)


if __name__=='__main__':
    main()
