"""Shared frozen audio gates for variable-length continuous controls."""
import csv
from itertools import groupby
import math
import numpy as np
from evaluate_guitar_duplicate_model import lower_probability
from piano_context_features import features
from pitch_attack_queue import simulate_latest,available_result
from transfer_real_piano_dictionary import observations


def audio_gates(raw,feature_path,rate,matrix,context):
    audio=np.fromfile(raw,dtype='<f4');count=round(rate*.1);hop=round(rate*.05)
    assert len(audio)%hop==0 and np.isfinite(audio).all()
    x=observations(audio.astype(float),rate);activation=__import__('joint_pitch_reference').fit(matrix,x)
    relative=activation/np.maximum(activation.max(axis=0),1e-12)
    explained=activation/np.maximum(matrix.T@x,1e-12)
    padded=np.pad(audio,(count,0));previous=set();frames=[];requests=[]
    with feature_path.open() as stream:
        for index,(end,rows) in enumerate(groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample']))):
            row=next(rows);assert end==(index+1)*hop
            strong={i+21 for i in range(88) if relative[i,index]>=.8 and explained[i,index]>=.3}
            new=strong-previous;previous=strong;probability=0.
            if row['mfcc_valid']=='1':
                vector=features(padded[end:end+count],rate,[float(row['mfcc'+str(i)]) for i in range(24)])
                probability=lower_probability(context['model'],vector)
            eligible=probability>=context['negative_max']+.001
            if eligible and new:
                requests.append(end)
            frames.append((end,strong if eligible else set(),{i+21 for i in range(88) if explained[i,index]>=.3}))
    assert len(frames)==len(audio)//hop
    return frames,requests


def support_text(frames,requests,model_path,rate):
    events=[];selected=set(requests)
    with model_path.open() as stream:
        for end,rows in groupby(csv.DictReader(stream,delimiter='\t'),key=lambda r:int(r['end_sample'])):
            group=list(rows);assert [int(r['midi']) for r in group]==list(range(21,109))
            assert end in selected
            assert all(math.isfinite(float(r[k])) and 0<=float(r[k])<=1 for r in group for k in ('legacy','edge4_note','edge4_onset'))
            events.append(dict(end_sample=end,ready_sample=end+math.ceil(rate*.005),wall_ms=float(group[0]['wall_ms']),cpu_ms=float(group[0]['cpu_ms']),
                notes={int(r['midi']):float(r['edge4_note']) for r in group}))
    queue=simulate_latest(events,rate);lines=[]
    for end,strong,continuing in frames:
        latest=available_result(queue,end,round(rate*.15))
        if latest is None:
            continue
        notes=events[latest['event_index']]['notes']
        for midi in range(21,109):
            seed=midi in strong and notes[midi]>=.3;sustain=midi in continuing and notes[midi]>=.3
            if seed or sustain:
                lines.append(f'{end}\t{midi}\t{int(seed)}\t{int(sustain)}\n')
    return ''.join(lines),dict(requests=len(events),processed=len(queue),
        estimated_worker_core_share=sum(events[r['event_index']]['cpu_ms'] for r in queue)/(frames[-1][0]/rate*1000))
