import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from detection_validation_store import Store
from regression_recordings import register_case,verify_files


class RegressionTest(unittest.TestCase):
    def test_reuses_external_audio_without_copying_it(self):
        with tempfile.TemporaryDirectory() as temporary,Store(Path(temporary)/'state.sqlite3') as store:
            raw=Path(temporary)/'audio.f32';raw.write_bytes(b'1234')
            register_case(store,'first',raw,48000,dict(reason='routing'))
            register_case(store,'second',raw,48000,dict(reason='rearticulation'))
            self.assertEqual(store.connection.execute('select count(*) from regression_files').fetchone()[0],1)
            self.assertEqual(store.connection.execute('select count(*) from regression_cases').fetchone()[0],2)
            verify_files(store)
            raw.write_bytes(b'changed')
            with self.assertRaises(ValueError): verify_files(store)


if __name__=='__main__': unittest.main()
