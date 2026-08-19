from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_zip_archive.py"


class ValidateZipArchiveTest(unittest.TestCase):
    def test_rejects_corrupt_member_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "archive.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("payload.txt", b"payload")
            data = bytearray(archive.read_bytes())
            data[data.index(b"payload")] ^= 0x01
            archive.write_bytes(data)
            result = subprocess.run([sys.executable, str(SCRIPT), str(archive)], capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("invalid ZIP member", result.stderr)


if __name__ == "__main__":
    unittest.main()
