import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from native_note_candidates import RepeatedStrikeGate,OwnershipHold


class CandidateTest(unittest.TestCase):
    def test_repeat_needs_native_rise_and_fresh_pitch_without_visibility_gap(self):
        gate=RepeatedStrikeGate(1000,50)
        self.assertEqual(gate.step(50,{60},{60:0},{60:.9},50,50),set())
        self.assertEqual(gate.step(100,{60},{60:.8},{60:.9},50,90),{60})
        self.assertEqual(gate.step(150,{60},{60:.9},{60:.9},100,140),set())

    def test_future_stale_or_missing_pitch_cannot_trigger(self):
        for source,completed,notes in ((150,201,{60:.9}),(1,2,{60:.9}),(150,190,{})):
            gate=RepeatedStrikeGate(1000,50)
            gate.step(150,{60},{60:0},{60:.9},150,150)
            self.assertEqual(gate.step(200,{60},{60:.8},notes,source,completed),set())

    def test_gap_clears_old_visibility_and_native_peak(self):
        gate=RepeatedStrikeGate(1000,50)
        gate.step(50,{60},{60:0},{60:.9},50,50)
        self.assertEqual(gate.step(150,{60},{60:.8},{60:.9},100,140),set())

    def test_owner_needs_consecutive_confident_observations(self):
        hold=OwnershipHold(50)
        self.assertEqual([hold.step(end,60,'guitar',.9) for end in (50,100,150)],['ambiguous','ambiguous','guitar'])
        self.assertEqual(hold.step(200,60,'guitar',.2),'ambiguous')
        self.assertEqual(hold.step(300,60,'guitar',.9),'ambiguous')


if __name__=='__main__':
    unittest.main()
