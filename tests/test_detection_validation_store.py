import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from detection_validation_store import Store


class StoreTest(unittest.TestCase):
    def test_deduplicates_and_rolls_back_failed_transaction(self):
        with tempfile.TemporaryDirectory() as temporary:
            with Store(Path(temporary)/'state.sqlite3') as store:
                with store.connection:
                    a=store.put(b'a'*10000);b=store.put(b'a'*10000)
                self.assertEqual(a,b)
                self.assertEqual(store.connection.execute('select count(*) from payloads').fetchone()[0],1)
                self.assertEqual(store.get(a),b'a'*10000)
                with self.assertRaises(RuntimeError):
                    with store.connection:
                        store.put(b'rollback');raise RuntimeError()
                self.assertEqual(store.connection.execute('select count(*) from payloads').fetchone()[0],1)
                row=store.connection.execute('select length(data),raw_size from payloads').fetchone()
                self.assertLess(row[0],row[1])

    def test_payload_integrity_is_checked(self):
        with tempfile.TemporaryDirectory() as temporary,Store(Path(temporary)/'state.sqlite3') as store:
            with store.connection:
                key=store.put(b'original')
                store.connection.execute('update payloads set raw_size=raw_size+1 where hash=?',(key,))
            with self.assertRaises(ValueError):
                store.get(key)

    def test_budget_refuses_growth_without_deleting_evidence(self):
        with tempfile.TemporaryDirectory() as temporary,Store(Path(temporary)/'state.sqlite3',max_payloads=1) as store:
            with store.connection:
                key=store.put(b'keep')
            with self.assertRaises(ValueError):
                with store.connection:
                    store.put(b'new')
            self.assertEqual(store.get(key),b'keep')
            with store.connection:
                self.assertEqual(store.put(b'keep'),key)


if __name__=='__main__':
    unittest.main()
