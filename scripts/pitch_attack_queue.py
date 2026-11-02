"""Integer-sample single-worker timing; completion is never backdated."""
import math


def simulate_latest(events,rate):
    if rate<=0:
        raise ValueError('Need a positive sample rate')
    previous=-1
    previous_ready=-1
    for event in events:
        end,duration=event['end_sample'],event['wall_ms']
        ready=event.get('ready_sample',end)
        if end<0 or int(end)!=end or end<=previous or not math.isfinite(duration) or duration<0 or int(ready)!=ready or ready<end or ready<previous_ready:
            raise ValueError('Need increasing source endpoints and finite nonnegative execution times')
        previous=end
        previous_ready=ready
    result=[]
    cursor=0
    free=0
    while cursor<len(events):
        free=max(free,events[cursor].get('ready_sample',events[cursor]['end_sample']))
        selected=cursor
        while selected+1<len(events) and events[selected+1].get('ready_sample',events[selected+1]['end_sample'])<=free:
            selected+=1
        event=events[selected]
        completed=free+math.ceil(event['wall_ms']*rate/1000)
        result.append(dict(event_index=selected,model_end_sample=event['end_sample'],started_sample=free,completed_sample=completed))
        free=completed
        cursor=selected+1
    return result


def available_result(queue,endpoint,maximum_age):
    if endpoint<0 or maximum_age<0:
        raise ValueError('Invalid analysis clock or expiry')
    latest=None
    for result in queue:
        if result['completed_sample']>endpoint:
            break
        latest=result
    if latest is None or endpoint-latest['model_end_sample']>maximum_age:
        return None
    assert latest['model_end_sample']<=latest['completed_sample']<=endpoint
    return latest
