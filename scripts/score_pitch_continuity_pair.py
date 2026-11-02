"""Score a paired native trial against an independent primary replay."""
from audit_keyboard_recovery import coverage
from routing_duration_score import merge,score

COLUMNS=('end_sample','bass','guitar','keys','voice','other','ambiguous','chord','bpm','confidence','drums')


def evaluate(rows,primary,notes,rate):
    assert len(rows)==len(primary)>0
    assert all(all(row[k]==original[k] for k in COLUMNS) for row,original in zip(rows,primary)), 'Disabled path differs from actual primary'
    held={};allowed={}
    for note in notes:
        if note['channel']!=9:
            held.setdefault(note['midi'],[]).append((note['start'],note['key_end']))
            allowed.setdefault(note['midi'],[]).append((note['start'],note['end']+.3))
    held={m:merge(v) for m,v in held.items()};allowed={m:merge(v) for m,v in allowed.items()}
    visible=[{int(m) for m in row['after_keys'].split(',') if m} for row in rows]
    horizon=int(rows[-1]['end_sample'])/rate
    delta=dict(added_cells=0,removed_cells=0,held_added_seconds=0.,held_removed_seconds=0.,supported_removed_seconds=0.,unsupported_added_seconds=0.,
        isolated_additions=0,unrelated_changed_frames=0,tempo_changed_frames=0,surviving_cell_changed_frames=0)
    additions=[];removals=[]
    for i,row in enumerate(rows):
        original={int(m) for m in row['keys'].split(',') if m};changed=visible[i]
        start=int(row['end_sample'])/rate;end=min(horizon,start+.05)
        delta['unrelated_changed_frames']+=bool(row['unrelated_difference'])
        delta['tempo_changed_frames']+=row['bpm_changed']!='0';delta['surviving_cell_changed_frames']+=row['survivor_changed']!='0'
        for midi in original-changed:
            key=coverage(held.get(midi,[]),start,end);supported=coverage(allowed.get(midi,[]),start,end)
            delta['removed_cells']+=1;delta['held_removed_seconds']+=key;delta['supported_removed_seconds']+=supported
            removals.append(dict(end_sample=int(row['end_sample']),midi=midi,held_seconds=key,supported_seconds=supported))
        for midi in changed-original:
            key=coverage(held.get(midi,[]),start,end);wrong=end-start-coverage(allowed.get(midi,[]),start,end)
            isolated=midi not in (visible[i-1] if i else set()) and midi not in (visible[i+1] if i+1<len(rows) else set())
            delta['added_cells']+=1;delta['held_added_seconds']+=key;delta['unsupported_added_seconds']+=wrong;delta['isolated_additions']+=isolated
            additions.append(dict(end_sample=int(row['end_sample']),midi=midi,held_seconds=key,unsupported_seconds=wrong,isolated=isolated))
    before=score(rows,notes,rate)['keys'];after=score([dict(row,keys=row['after_keys']) for row in rows],notes,rate)['keys']
    passed=not any(delta[k] for k in ('removed_cells','unrelated_changed_frames','tempo_changed_frames','surviving_cell_changed_frames','isolated_additions')) and delta['unsupported_added_seconds']<1e-8 and after['matched_attacks']>=before['matched_attacks']
    return dict(before=before,after=after,deltas=delta,additions=additions,removals=removals,passed=passed,
        benefit=after['matched_attacks']>before['matched_attacks'] or delta['held_added_seconds']>1e-8)
