"""Audio-only, bounded display continuity and causal request scheduling."""
import math
from pitch_attack_queue import simulate_latest,available_result


def simulate(frames,events,prefetch,rate,refresh,context_latch=False):
    submissions=[]
    active={}
    added=[]
    requests=[]
    maximum_age=round(rate*.15)
    previous=0
    for frame in frames:
        end=frame['end_sample']
        if end<=previous:
            raise ValueError('Analysis endpoints must increase')
        previous=end
        # Only previously submitted inputs can finish before this decision.
        queue=simulate_latest(submissions,rate)
        latest=available_result(queue,end,maximum_age)
        neural={} if latest is None else submissions[latest['event_index']]['notes']
        visible=frame['visible']
        strong=frame['strong']
        def supported(midi):
            return midi in strong and neural.get(midi,0.)>=.3
        continuing=frame['continuing'] if context_latch else strong
        active={m:birth for m,birth in active.items() if m not in visible and
                end-birth<maximum_age and m in continuing and neural.get(m,0.)>=.3}
        for midi in frame['first_hits']:
            if midi not in visible and supported(midi):
                active.setdefault(midi,end)
        free=list(frame['free_slots'])
        for midi in sorted(list(active)):
            pc=midi%12
            if free[pc]<=0:
                del active[midi]
                continue
            free[pc]-=1
            assert latest is not None and latest['completed_sample']<=end
            added.append(dict(end_sample=end,midi=midi,born_sample=active[midi],
                model_end_sample=latest['model_end_sample'],completed_sample=latest['completed_sample']))
        # Current-input inference cannot influence the decision just made.
        if end in events and (end in prefetch or (refresh and active)):
            event=dict(events[end],end_sample=end,ready_sample=end+math.ceil(rate*.005))
            submissions.append(event)
            requests.append(end)
    queue=simulate_latest(submissions,rate)
    return dict(accepted=added,requests=requests,processed=len(queue),
        estimated_worker_core_share=sum(submissions[r['event_index']]['cpu_ms'] for r in queue)/(frames[-1]['end_sample']/rate*1000))
