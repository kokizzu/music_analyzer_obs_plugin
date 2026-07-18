#!/usr/bin/env python3

from pathlib import Path
import math
import struct
import sys
import tempfile
import wave
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_idmt_guitar_samples


NOTE_PITCH_CLASS = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}


def write_executable(path, text):
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def write_placeholder_wav(path):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00\x00" * 44100 * 3)


def fixture_xml(audio_file):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<idmt>
  <globalParameter>
    <audioFileName>{audio_file}</audioFileName>
    <instrument>Guitar</instrument>
    <instrumentModel>Fixture Guitar</instrumentModel>
    <pickUpSetting>bridge</pickUpSetting>
  </globalParameter>
  <transcription>
    <event>
      <onsetSec>0.10</onsetSec>
      <offsetSec>0.90</offsetSec>
      <pitch>52</pitch>
      <excitationStyle>PK</excitationStyle>
      <expressionStyle>NO</expressionStyle>
      <stringNumber>4</stringNumber>
      <fretNumber>2</fretNumber>
    </event>
    <event>
      <onsetSec>1.10</onsetSec>
      <offsetSec>1.90</offsetSec>
      <pitch>55</pitch>
      <excitationStyle>FS</excitationStyle>
      <expressionStyle>VI</expressionStyle>
      <stringNumber>3</stringNumber>
      <fretNumber>0</fretNumber>
    </event>
    <event>
      <onsetSec>2.00</onsetSec>
      <offsetSec>2.70</offsetSec>
      <pitch>57</pitch>
      <excitationStyle>PK</excitationStyle>
      <expressionStyle>NO</expressionStyle>
      <stringNumber>3</stringNumber>
      <fretNumber>2</fretNumber>
    </event>
    <event>
      <onsetSec>2.02</onsetSec>
      <offsetSec>2.65</offsetSec>
      <pitch>60</pitch>
      <excitationStyle>PK</excitationStyle>
      <expressionStyle>NO</expressionStyle>
      <stringNumber>2</stringNumber>
      <fretNumber>1</fretNumber>
    </event>
  </transcription>
</idmt>
"""


def write_fixture_zip(path):
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        wav_path = temp_path / "AR_NO_I.wav"
        xml_path = temp_path / "AR_NO_I.xml"
        write_placeholder_wav(wav_path)
        xml_path.write_text(fixture_xml("AR_NO_I.wav"), encoding="utf-8")
        with zipfile.ZipFile(path, "w") as archive:
            archive.write(wav_path, "IDMT-SMT-GUITAR_V2/dataset2/audio/AR_NO_I.wav")
            archive.write(xml_path, "IDMT-SMT-GUITAR_V2/dataset2/annotation/AR_NO_I.xml")


def write_fake_ffmpeg(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
from pathlib import Path
import math
import re
import struct
import sys
import wave

PITCH_CLASS = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}

out = Path(sys.argv[-1])
match = re.search(r"_([A-G](?:#)?)([0-8])_", out.name)
if not match:
    raise SystemExit(f"cannot infer note from {out}")
name, octave = match.groups()
midi = (int(octave) + 1) * 12 + PITCH_CLASS[name]
freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
sample_rate = 48000
frames = []
for index in range(int(sample_rate * 0.8)):
    sample = int(math.sin(2.0 * math.pi * freq * index / sample_rate) * 16000)
    frames.append(struct.pack("<h", sample))
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    wav.writeframes(b"".join(frames))
""",
    )


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        expected = ["id", "family", "nsynth_family", "source", "midi", "note", "path", "signature"]
        if header != expected:
            raise AssertionError(f"unexpected manifest header: {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def run_prepare(base, limit=0, min_samples=1, expressions=""):
    archive = base / "IDMT-SMT-GUITAR_V2.zip"
    output = base / "out"
    ffmpeg = base / "fake-ffmpeg"
    write_fixture_zip(archive)
    write_fake_ffmpeg(ffmpeg)
    args = [
        "--archive",
        str(archive),
        "--output",
        str(output),
        "--cache-dir",
        str(base / "cache"),
        "--limit",
        str(limit),
        "--min-samples",
        str(min_samples),
        "--ffmpeg",
        str(ffmpeg),
    ]
    if expressions:
        args.extend(["--expressions", expressions])
    prepare_idmt_guitar_samples.main(args)
    return output


def test_idmt_guitar_xml_is_prepared_as_guitar_notes():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), min_samples=2)
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 2:
            raise AssertionError(f"expected two monophonic rows, got {len(rows)}")
        notes = [row[5] for row in rows]
        if notes != ["E3", "G3"]:
            raise AssertionError(f"expected E3/G3 rows, got {notes}")
        if any(row[1] != "guitar" for row in rows):
            raise AssertionError(f"expected guitar family rows, got {rows}")
        for row in rows:
            if not (output / row[6]).is_file():
                raise AssertionError(f"missing prepared WAV {row[6]}")


def test_limit_and_expression_filter_are_enforced():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), limit=1, min_samples=1, expressions="VI")
        rows = manifest_rows(output / "manifest.tsv")
        notes = [row[5] for row in rows]
        if notes != ["G3"]:
            raise AssertionError(f"expected only the vibrato G3 row, got {notes}")


def test_minimum_sample_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        try:
            run_prepare(base, limit=1, min_samples=3)
        except SystemExit:
            partial = base / "out" / "manifest.tsv.partial"
            rows = manifest_rows(partial)
            if len(rows) != 1:
                raise AssertionError("partial manifest should contain the limited prepared row")
        else:
            raise AssertionError("expected min-samples failure")


def test_xml_parser_accepts_idmt_tags():
    audio_file, metadata, notes = prepare_idmt_guitar_samples.parse_xml_annotation(
        fixture_xml("Take01.wav").encode("utf-8")
    )
    if audio_file != "Take01.wav":
        raise AssertionError(f"unexpected audio filename {audio_file}")
    if metadata["model"] != "Fixture Guitar":
        raise AssertionError(f"unexpected metadata {metadata}")
    if [note["midi"] for note in notes] != [52, 55, 57, 60]:
        raise AssertionError(f"unexpected notes {notes}")
    if not math.isclose(notes[0]["onset"], 0.10, abs_tol=0.001):
        raise AssertionError(f"unexpected onset {notes[0]['onset']}")


def main():
    test_idmt_guitar_xml_is_prepared_as_guitar_notes()
    test_limit_and_expression_filter_are_enforced()
    test_minimum_sample_failure_writes_partial_manifest()
    test_xml_parser_accepts_idmt_tags()
    print("test_prepare_idmt_guitar_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
