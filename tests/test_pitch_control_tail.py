import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pitch_continuity_control_evidence import audio_gates


class PartialHopTest(unittest.TestCase):
    def test_partial_tail_cannot_enter_complete_hop_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary);raw=directory/'audio.f32';features=directory/'features.tsv'
            features.write_text('end_sample\tmfcc_valid\n800\t0\n1600\t0\n')
            complete=np.zeros(1600,dtype='<f4');matrix=np.eye(88)
            observed=[]
            def capture(audio,rate):
                observed.append(audio.copy())
                return np.zeros((88,2))
            with patch('pitch_continuity_control_evidence.observations',side_effect=capture):
                complete.tofile(raw)
                expected=audio_gates(raw,features,16000,matrix,{'negative_max':.9})
                np.concatenate((complete,np.ones(799,dtype='<f4'))).tofile(raw)
                actual=audio_gates(raw,features,16000,matrix,{'negative_max':.9})
            self.assertEqual(actual,expected)
            self.assertEqual(len(actual[0]),2)
            np.testing.assert_array_equal(observed[0],observed[1])


if __name__=='__main__':
    unittest.main()
