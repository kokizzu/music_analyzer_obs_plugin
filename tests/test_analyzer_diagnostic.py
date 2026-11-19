import sys
from pathlib import Path
import struct
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from detection_validation_store import Store
from analyzer_diagnostic import save_recording


class RecordingTest(unittest.TestCase):
    def test_exact_audio_deduplicated_with_format_in_identity(self):
        with tempfile.TemporaryDirectory() as temporary,Store(Path(temporary)/'state.sqlite3') as store:
            pcm=struct.pack('<800f',*([.1]*800))
            first=save_recording(store,pcm,16000)
            self.assertEqual(first,save_recording(store,pcm,16000))
            self.assertNotEqual(first,save_recording(store,pcm,48000))
            self.assertEqual(store.connection.execute('select count(*) from payloads').fetchone()[0],1)

    def test_invalid_audio_rejected_before_storage(self):
        with tempfile.TemporaryDirectory() as temporary,Store(Path(temporary)/'state.sqlite3') as store:
            for data,rate in ((b'',48000),(b'123',48000),(struct.pack('<f',float('nan')),48000),(b'0000',123)):
                with self.assertRaises(ValueError):
                    save_recording(store,data,rate)
            self.assertEqual(store.connection.execute('select count(*) from recordings').fetchone()[0],0)

    def test_recording_limit_preserves_existing_data(self):
        with tempfile.TemporaryDirectory() as temporary,Store(Path(temporary)/'state.sqlite3') as store:
            first=None
            for index in range(20):
                key=save_recording(store,struct.pack('<f',index/20),48000)
                first=first or key
            with self.assertRaises(ValueError):
                save_recording(store,struct.pack('<f',.99),48000)
            self.assertEqual(store.connection.execute('select count(*) from recordings').fetchone()[0],20)
            self.assertEqual(first,save_recording(store,struct.pack('<f',0),48000))


if __name__=='__main__':
    unittest.main()
