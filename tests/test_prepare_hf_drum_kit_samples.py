#!/usr/bin/env python3

import io
import json
import sys
import tempfile
import wave
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.prepare_hf_drum_kit_samples as prep


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


def populate_cached_manifest(root):
    rows = []
    for category in sorted(set(prep.LABEL_MAP.values())):
        relative = Path(category) / f"cached_{category}.wav"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(wav_bytes())
        rows.append((category, str(relative), "0.000000", f"cached:{category}"))
    prep.write_manifest(root, rows)
    return len(rows)


def fake_urlopen(url, timeout=0):
    if url.startswith(prep.ROWS_ENDPOINT):
        labels = ("kick", "snare", "hat", "crash", "tom", "ride", "rim", "cymbal")
        payload = {
            "rows": [
                {
                    "row_idx": index,
                    "row": {
                        "audio": [{"src": f"https://example.test/{label}.wav", "type": "audio/wav"}],
                        "label": label,
                    },
                }
                for index, label in enumerate(labels)
            ],
            "num_rows_total": len(labels),
        }
        return FakeResponse(json.dumps(payload).encode("utf-8"))
    return FakeResponse(wav_bytes())


def main():
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(prep.request, "urlopen", side_effect=fake_urlopen):
            count = prep.prepare(Path(tmp), splits=("test",), page_size=100, retries=1)

        assert count == 7
        manifest = Path(tmp) / "manifest.tsv"
        rows = manifest.read_text(encoding="utf-8").splitlines()
        assert rows[0] == "category\tpath\tduration_seconds\tsource"
        assert "kick\tkick/test_0000_kick_0001.wav\t0.000000\tairasoul/drum-kit:test:0:kick" in rows
        assert "hihat\thihat/test_0002_hat_0001.wav\t0.000000\tairasoul/drum-kit:test:2:hat" in rows
        assert "rim\trim/test_0006_rim_0001.wav\t0.000000\tairasoul/drum-kit:test:6:rim" in rows
        assert (Path(tmp) / "kick/test_0000_kick_0001.wav").is_file()
        assert (Path(tmp) / "hihat/test_0002_hat_0001.wav").is_file()
        assert not (Path(tmp) / "crash/test_0007_cymbal_0001.wav").exists()

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        cached_count = populate_cached_manifest(root)
        with mock.patch.object(prep.request, "urlopen", side_effect=AssertionError("network called")):
            count = prep.prepare(root, splits=("test",), page_size=100, retries=1,
                                 cache_min_per_category=1)

        assert count == cached_count


if __name__ == "__main__":
    main()
