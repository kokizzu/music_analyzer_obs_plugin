"""Development candidates only; neither policy is wired into production."""
import math


class RepeatedStrikeGate:
    def __init__(self,rate,hop):
        if rate<=0 or hop<=0:
            raise ValueError('Invalid source clock')
        self.rate=rate;self.hop=hop;self.end=None;self.visible=set();self.above=set();self.last={}

    def step(self,end,visible,onsets,notes,source_end,completed):
        if self.end is not None and end<=self.end:
            raise ValueError('Nonincreasing source clock')
        if self.end is not None and end-self.end!=self.hop:
            self.visible=set();self.above=set();self.last={}
        above={m for m,v in onsets.items() if math.isfinite(v) and v>=.5}
        fresh=source_end is not None and completed is not None and 0<=source_end<=completed<=end and end-source_end<=round(self.rate*.15)
        strikes={m for m in (visible&self.visible&above)-self.above if fresh and notes.get(m,0)>=.3 and end-self.last.get(m,-self.rate)>=round(self.rate*.15)}
        for midi in strikes:
            self.last[midi]=end
        self.end=end;self.visible=set(visible);self.above=above
        return strikes


class OwnershipHold:
    def __init__(self,hop):
        self.hop=hop;self.history={}

    def step(self,end,midi,owner,confidence):
        if not 0<=midi<=127 or not math.isfinite(confidence):
            raise ValueError('Invalid ownership observation')
        previous=self.history.get(midi)
        count=1 if confidence>=.8 else 0
        if count and previous and previous[0]==end-self.hop and previous[1]==owner:
            count=min(3,previous[2]+1)
        self.history[midi]=(end,owner,count)
        return owner if count>=3 else 'ambiguous'
