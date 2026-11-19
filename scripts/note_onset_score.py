"""Score per-pitch attack events independently of sustained display visibility."""
import math
from collections import defaultdict


def score_onsets(events,notes,horizon,tolerance=.15):
    if not math.isfinite(horizon) or horizon<=0 or not math.isfinite(tolerance) or tolerance<0:
        raise ValueError('Invalid horizon or tolerance')
    predicted=defaultdict(list);expected=defaultdict(list);censored=0
    for midi,time in events:
        if not isinstance(midi,int) or not 0<=midi<=127 or not math.isfinite(time) or not 0<=time<=horizon:
            raise ValueError('Invalid or future attack event')
        predicted[midi].append(time)
    for note in notes:
        if note['channel']==9:
            continue
        start,key_end,end=note['start'],note['key_end'],note['end']
        if not all(math.isfinite(v) for v in (start,key_end,end)) or not 0<=start<key_end<=end or not 0<=note['midi']<=127:
            raise ValueError('Invalid note interval')
        if start>=horizon:
            continue
        deadline=min(key_end,start+tolerance)
        if deadline>horizon:
            censored+=1
        else:
            expected[note['midi']].append((start,deadline))
    matched=missed=unmatched=0;latencies=[]
    for midi in set(predicted)|set(expected):
        candidates=sorted(predicted[midi]);used=set()
        # Earliest deadline first preserves feasible matches for short notes.
        for start,deadline in sorted(expected[midi],key=lambda v:(v[1],v[0])):
            index=next((i for i,time in enumerate(candidates) if i not in used and start-1e-12<=time<=deadline+1e-12),None)
            if index is None:
                missed+=1
            else:
                used.add(index);matched+=1;latencies.append((candidates[index]-start)*1000)
        unmatched+=len(candidates)-len(used)
    return dict(matched=matched,missed=missed,unmatched=unmatched,censored=censored,
        latency_ms=sorted(latencies),tolerance_seconds=tolerance,
        scope='Attack events only; sustained visibility and pedal-supported duration are scored separately. No anticipatory tolerance.')
