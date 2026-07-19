#!/usr/bin/env python3
from pathlib import Path
import sqlite3
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_good_sounds_samples


def write_executable(path, text):
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def write_fake_ffmpeg(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
import shutil
import sys

args = sys.argv[1:]
source = args[args.index("-i") + 1]
dest = args[-1]
shutil.copyfile(source, dest)
""",
    )


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header != ["id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities"]:
            raise AssertionError(f"unexpected header: {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def make_official_like_database(path):
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE packs(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE sounds(
          id INTEGER PRIMARY KEY,
          pack_id INTEGER,
          instrument TEXT,
          note TEXT,
          octave INTEGER,
          dynamics TEXT,
          semitone INTEGER,
          klass TEXT
        );
        CREATE TABLE takes(
          id INTEGER PRIMARY KEY,
          sound_id INTEGER,
          filename TEXT
        );
        INSERT INTO packs(id, name) VALUES (1, 'session-a'), (2, 'session-b');
        INSERT INTO sounds(id, pack_id, instrument, note, octave, dynamics, semitone, klass) VALUES
          (1, 1, 'bass', 'C', 2, 'mf', 36, 'good-sound'),
          (2, 1, 'violin', 'Bb', 4, 'p', 70, 'bad'),
          (3, 2, 'clarinet', 'F#', 5, 'f', 78, 'good-sound'),
          (4, 2, 'flute', 'C', 5, 'mf', 72, 'scale-good');
        INSERT INTO takes(id, sound_id, filename) VALUES
          (10, 1, 'bass_c2.flac'),
          (11, 2, 'violin_bb4.flac'),
          (12, 3, 'clarinet_fs5.flac'),
          (13, 4, 'flute_scale.flac');
        """
    )
    conn.commit()
    conn.close()


def make_generic_database(path):
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE rows(id INTEGER PRIMARY KEY, instrument TEXT, midi INTEGER, filename TEXT);
        INSERT INTO rows(id, instrument, midi, filename) VALUES
          (1, 'piano', 60, 'generic/piano_c4.flac'),
          (2, 'voice', 69, 'generic/voice_a4.flac');
        """
    )
    conn.commit()
    conn.close()


def make_archive(root, generic=False):
    archive = root / "good-sounds.zip"
    db = root / ("generic.sqlite" if generic else "good-sounds.sqlite")
    if generic:
        make_generic_database(db)
    else:
        make_official_like_database(db)
    with zipfile.ZipFile(archive, "w") as file:
        file.write(db, db.name)
        if generic:
            file.writestr("generic/piano_c4.flac", b"piano")
            file.writestr("generic/voice_a4.flac", b"voice")
        else:
            file.writestr("sound_files/session-a/bass_c2.flac", b"bass")
            file.writestr("sound_files/session-a/violin_bb4.flac", b"violin")
            file.writestr("sound_files/session-b/clarinet_fs5.flac", b"clarinet")
            file.writestr("sound_files/session-b/flute_scale.flac", b"flute-scale")
    return archive


def run_prepare(base, *, generic=False, min_samples=1):
    archive = make_archive(base, generic=generic)
    output = base / "out"
    ffmpeg = base / "fake-ffmpeg"
    write_fake_ffmpeg(ffmpeg)
    prepare_good_sounds_samples.main([
        "--archive",
        str(archive),
        "--output",
        str(output),
        "--limit",
        "0",
        "--min-samples",
        str(min_samples),
        "--ffmpeg",
        str(ffmpeg),
    ])
    return output


def test_official_schema_manifest_mapping():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp))
        rows = manifest_rows(output / "manifest.tsv")
        families = [row[1] for row in rows]
        notes = [row[5] for row in rows]
        sources = [row[3] for row in rows]
        if families != ["bass", "other", "other"]:
            raise AssertionError(f"unexpected family mapping: {families}")
        if notes != ["C2", "A#4", "F#5"]:
            raise AssertionError(f"unexpected note mapping: {notes}")
        if sources != ["bass", "violin", "clarinet"]:
            raise AssertionError(f"unexpected source mapping: {sources}")
        if any("flute" in row[3] for row in rows):
            raise AssertionError("scale rows should be excluded from one-note fixtures")
        for row in rows:
            if not (output / row[6]).is_file():
                raise AssertionError(f"missing copied audio {row[6]}")


def test_generic_schema_fallback():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), generic=True)
        rows = manifest_rows(output / "manifest.tsv")
        families = [row[1] for row in rows]
        notes = [row[5] for row in rows]
        if families != ["piano", "vocals"]:
            raise AssertionError(f"unexpected generic family mapping: {families}")
        if notes != ["C4", "A4"]:
            raise AssertionError(f"unexpected generic notes: {notes}")


def test_minimum_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        try:
            run_prepare(Path(temp), min_samples=4)
        except SystemExit:
            rows = manifest_rows(Path(temp) / "out" / "manifest.tsv.partial")
            if len(rows) != 3:
                raise AssertionError("partial manifest should contain prepared rows")
        else:
            raise AssertionError("expected min-samples failure")


def main():
    test_official_schema_manifest_mapping()
    test_generic_schema_fallback()
    test_minimum_failure_writes_partial_manifest()
    print("test_prepare_good_sounds_samples: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
