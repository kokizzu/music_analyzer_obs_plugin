import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pitch_attack_continuity import simulate


def fixture():
    frames=[dict(end_sample=e,visible=set(),strong={60},first_hits={60} if e==250 else set(),free_slots=[1]*12)
            for e in range(100,451,50)]
    events={e:dict(notes={60:.8},wall_ms=30.,cpu_ms=30.) for e in range(100,451,50)}
    return frames,events


class ContinuityTest(unittest.TestCase):
    def test_refresh_pays_execution_and_expires_seed(self):
        frames,events=fixture()
        before=simulate(frames,events,{100},1000,False)
        after=simulate(frames,events,{100},1000,True)
        self.assertEqual([c['end_sample'] for c in before['accepted']],[250])
        self.assertEqual([c['end_sample'] for c in after['accepted']],[250,300,350])
        self.assertEqual(after['requests'],[100,250,300,350])
        self.assertTrue(all(c['completed_sample']<=c['end_sample'] for c in after['accepted']))
        self.assertEqual(after['accepted'][1]['model_end_sample'],250)
        self.assertEqual(after['accepted'][1]['completed_sample'],285)

    def test_handoff_context_and_capacity(self):
        frames,events=fixture()
        frames[4]['visible']={60}
        result=simulate(frames,events,{100},1000,True)
        self.assertEqual([c['end_sample'] for c in result['accepted']],[250])
        self.assertNotIn(300,result['requests'])
        frames,events=fixture()
        frames[4]['strong']=set()
        self.assertEqual([c['end_sample'] for c in simulate(frames,events,{100},1000,True)['accepted']],[250])
        frames,events=fixture()
        frames[3]['free_slots'][0]=0
        self.assertEqual(simulate(frames,events,{100},1000,True)['accepted'],[])

    def test_future_outputs_cannot_change_past(self):
        frames,events=fixture()
        original=simulate(frames,events,{100},1000,True)
        events[300]['notes']={60:0.}
        changed=simulate(frames,events,{100},1000,True)
        past=lambda r:[c for c in r['accepted'] if c['end_sample']<=300]
        self.assertEqual(past(original),past(changed))
        self.assertEqual([c['end_sample'] for c in changed['accepted']],[250,300])

    def test_seed_context_latch_still_requires_current_pitch_and_neural_support(self):
        frames,events=fixture()
        for frame in frames:
            frame['continuing']={60}
            if frame['end_sample']!=250:
                frame['strong']=set()
        result=simulate(frames,events,{100,250,300},1000,False,context_latch=True)
        self.assertEqual([c['end_sample'] for c in result['accepted']],[250,300,350])
        frames[4]['continuing']=set()
        self.assertEqual([c['end_sample'] for c in simulate(frames,events,{100,250,300},1000,False,context_latch=True)['accepted']],[250])
        frames,events=fixture()
        for frame in frames:
            frame['continuing']={60}
            frame['strong']=set()
        self.assertEqual(simulate(frames,events,{100},1000,False,context_latch=True)['accepted'],[])


if __name__=='__main__':
    unittest.main()
