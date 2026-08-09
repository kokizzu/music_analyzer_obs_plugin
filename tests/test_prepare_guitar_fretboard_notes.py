#!/usr/bin/env python3

import io
import json
import tempfile
import wave
from pathlib import Path
import sys
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_guitar_fretboard_notes as prep


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.data


def wav_bytes():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00\x00" * 64)
    return buffer.getvalue()


def fake_urlopen(url, timeout=0):
    if url.startswith(prep.ROWS_ENDPOINT):
        payload = {
            "rows": [
                {
                    "row_idx": 0,
                    "row": {
                        "audio": [{"src": "https://example.test/a.wav", "type": "audio/wav"}],
                        "source": "deb",
                        "guitar_type": "acoustic",
                        "string_name": "low_E",
                        "fret": 0,
                        "note_name": "E2",
                        "midi_number": 40,
                    },
                },
                {
                    "row_idx": 1,
                    "row": {
                        "audio": [{"src": "https://example.test/b.wav", "type": "audio/wav"}],
                        "source": "ele",
                        "guitar_type": "electric",
                        "string_name": "B",
                        "fret": 1,
                        "note_name": "C4",
                        "midi_number": 60,
                    },
                },
            ],
            "num_rows_total": 2,
        }
        return FakeResponse(json.dumps(payload).encode("utf-8"))
    return FakeResponse(wav_bytes())


def main():
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(prep.request, "urlopen", side_effect=fake_urlopen):
            count = prep.prepare(Path(tmp), splits=("test",), page_size=100, retries=1)

        assert count == 2
        manifest = Path(tmp) / "manifest.tsv"
        rows = manifest.read_text(encoding="utf-8").splitlines()
        assert rows[0] == "id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath"
        assert "test_0000_deb_low_E_f0_E2\tguitar\tguitar_fretboard_notes\tacoustic:deb:low_E:f0\t40\tE2\taudio/test_0000_deb_low_E_f0_E2.wav" in rows
        assert "test_0001_ele_B_f1_C4\tguitar\tguitar_fretboard_notes\telectric:ele:B:f1\t60\tC4\taudio/test_0001_ele_B_f1_C4.wav" in rows
        assert (Path(tmp) / "audio/test_0000_deb_low_E_f0_E2.wav").is_file()
        assert (Path(tmp) / "audio/test_0001_ele_B_f1_C4.wav").is_file()

        with mock.patch.object(prep.request, "urlopen") as urlopen:
            cached_count = prep.prepare(Path(tmp), limit=2, offline=True)
        assert cached_count == 2
        urlopen.assert_not_called()

        (Path(tmp) / "audio/test_0001_ele_B_f1_C4.wav").unlink()
        try:
            prep.prepare(Path(tmp), limit=2, offline=True)
        except RuntimeError as exc:
            assert "offline cache miss" in str(exc)
        else:
            raise AssertionError("offline preparation accepted an incomplete cached manifest")


if __name__ == "__main__":
    main()
