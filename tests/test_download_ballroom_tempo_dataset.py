#!/usr/bin/env python3
"""Regression coverage for verified resume of the Ballroom archive download."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "download_ballroom_tempo_dataset.sh"


class DownloadBallroomTempoDatasetTest(unittest.TestCase):
    def test_retries_a_cleanly_ended_partial_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            source_tree = temp / "source"
            source_tree.mkdir()
            (source_tree / "fixture.wav").write_bytes(b"fixture audio\n" * 4096)
            source_archive = temp / "source.tar.gz"
            with tarfile.open(source_archive, "w:gz") as archive:
                archive.add(source_tree / "fixture.wav", arcname="fixture.wav")
            expected_md5 = hashlib.md5(source_archive.read_bytes()).hexdigest()

            curl_calls = temp / "curl-calls"
            fake_curl = temp / "fake-curl.py"
            fake_curl.write_text(
                "#!/usr/bin/env python3\n"
                "import os\n"
                "from pathlib import Path\n"
                "import sys\n"
                "destination = Path(sys.argv[sys.argv.index('-o') + 1])\n"
                "source = Path(os.environ['BALLROOM_TEST_SOURCE'])\n"
                "calls = Path(os.environ['BALLROOM_TEST_CALLS'])\n"
                "count = int(calls.read_text() if calls.exists() else '0')\n"
                "payload = source.read_bytes()\n"
                "if count == 0:\n"
                "    destination.write_bytes(payload[:len(payload) // 2])\n"
                "else:\n"
                "    with destination.open('ab') as output:\n"
                "        output.write(payload[len(payload) // 2:])\n"
                "calls.write_text(str(count + 1))\n",
                encoding="utf-8",
            )
            fake_curl.chmod(0o755)
            fake_aria2 = temp / "fake-aria2.py"
            fake_aria2.write_text(
                "#!/usr/bin/env python3\n"
                "from pathlib import Path\n"
                "import sys\n"
                "directory = Path(sys.argv[sys.argv.index('--dir') + 1])\n"
                "name = sys.argv[sys.argv.index('--out') + 1]\n"
                "(directory / f'{name}.aria2').write_text('stale range bitmap')\n"
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            fake_aria2.chmod(0o755)

            store = temp / "InstrumentSamples"
            (store / "ballroom_tempo" / "annotations" / ".git").mkdir(parents=True)
            environment = os.environ.copy()
            environment.update(
                {
                    "BALLROOM_TEST_SOURCE": str(source_archive),
                    "BALLROOM_TEST_CALLS": str(curl_calls),
                }
            )
            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    str(store),
                    str(fake_curl),
                    "fixture-url",
                    str(fake_aria2),
                    expected_md5,
                    "",
                    "1",
                    "2",
                ],
                check=True,
                capture_output=True,
                text=True,
                env=environment,
            )

            archive_path = store / "ballroom_tempo" / "data1.tar.gz"
            self.assertEqual(hashlib.md5(archive_path.read_bytes()).hexdigest(), expected_md5)
            self.assertEqual(curl_calls.read_text(encoding="utf-8"), "2")
            self.assertFalse(Path(f"{archive_path}.aria2").exists())
            self.assertTrue((store / "ballroom_tempo" / "audio" / "fixture.wav").is_file())
            self.assertIn("ballroom tempo data ready", result.stdout)

    def test_resets_a_full_length_checksum_invalid_archive_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            source_tree = temp / "source"
            source_tree.mkdir()
            (source_tree / "fixture.wav").write_bytes(b"fixture audio\n" * 4096)
            source_archive = temp / "source.tar.gz"
            with tarfile.open(source_archive, "w:gz") as archive:
                archive.add(source_tree / "fixture.wav", arcname="fixture.wav")
            payload = source_archive.read_bytes()
            expected_md5 = hashlib.md5(payload).hexdigest()

            curl_calls = temp / "curl-calls"
            fake_curl = temp / "fake-curl.py"
            fake_curl.write_text(
                "#!/usr/bin/env python3\n"
                "import os\n"
                "from pathlib import Path\n"
                "import sys\n"
                "destination = Path(sys.argv[sys.argv.index('-o') + 1])\n"
                "source = Path(os.environ['BALLROOM_TEST_SOURCE'])\n"
                "calls = Path(os.environ['BALLROOM_TEST_CALLS'])\n"
                "count = int(calls.read_text() if calls.exists() else '0')\n"
                "if destination.stat().st_size == 0:\n"
                "    destination.write_bytes(source.read_bytes())\n"
                "calls.write_text(str(count + 1))\n",
                encoding="utf-8",
            )
            fake_curl.chmod(0o755)

            store = temp / "InstrumentSamples"
            target = store / "ballroom_tempo"
            (target / "annotations" / ".git").mkdir(parents=True)
            # Match the server length while ensuring the initial cache cannot
            # pass the integrity gate. The first fake resume is a no-op.
            (target / "data1.tar.gz").write_bytes(b"x" * len(payload))
            environment = os.environ.copy()
            environment.update(
                {
                    "BALLROOM_TEST_SOURCE": str(source_archive),
                    "BALLROOM_TEST_CALLS": str(curl_calls),
                }
            )
            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    str(store),
                    str(fake_curl),
                    "fixture-url",
                    "",
                    expected_md5,
                    "",
                    "1",
                    "2",
                ],
                check=True,
                capture_output=True,
                text=True,
                env=environment,
            )

            archive_path = target / "data1.tar.gz"
            self.assertEqual(hashlib.md5(archive_path.read_bytes()).hexdigest(), expected_md5)
            self.assertEqual(curl_calls.read_text(encoding="utf-8"), "2")
            self.assertIn("resetting invalid cache once", result.stderr)


if __name__ == "__main__":
    unittest.main()
