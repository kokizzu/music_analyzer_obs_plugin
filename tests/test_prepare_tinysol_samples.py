#!/usr/bin/env python3
from pathlib import Path
import sys
import tempfile
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_tinysol_samples


def write_wav_bytes():
    import io

    data = io.BytesIO()
    with wave.open(data, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(44100)
        file.writeframes(b"\0\0" * 4410)
    return data.getvalue()


def make_fixture(root, current_header=False):
    metadata = root / "TinySOL_metadata.csv"
    if current_header:
        header = (
            "Path,Fold,Family,Instrument (abbr.),Instrument (in full),Technique (abbr.),"
            "Technique (in full),Pitch,Pitch ID,Dynamics,Dynamics ID,Resampled,String ID"
        )
    else:
        header = (
            "Path,Fold,Family,Instrument,Instrument Name,Technique,Technique Name,Pitch,Pitch ID,"
            "Dynamics,Dynamics ID,Resampled,String ID"
        )
    metadata.write_text(
        "\n".join([
            header,
            "Strings/Contrabass/ordinario/Cb-ord-E2-ff-N.wav,0,Strings,Cb,Contrabass,ord,ordinario,E2,40,ff,4,False,",
            "Keyboards/Accordion/ordinario/Acc-ord-C4-mf-N.wav,0,Keyboards,Acc,Accordion,ord,ordinario,C4,60,mf,2,False,",
            "Winds/Flute/ordinario/Fl-ord-A4-pp-N.wav,0,Winds,Fl,Flute,ord,ordinario,A4,69,pp,0,False,",
            "Strings/Violin/ordinario/Vn-ord-G6-mf-1cR.wav,0,Strings,Vn,Violin,ord,ordinario,G6,91,mf,2,True,1",
        ]) + "\n",
        encoding="utf-8",
    )
    archive = root / "TinySOL.zip"
    wav = write_wav_bytes()
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("TinySOL/audio/Strings/Contrabass/ordinario/Cb-ord-E2-ff-N.wav", wav)
        file.writestr("TinySOL/audio/Keyboards/Accordion/ordinario/Acc-ord-C4-mf-N.wav", wav)
        file.writestr("TinySOL/audio/Winds/Flute/ordinario/Fl-ord-A4-pp-N.wav", wav)
        file.writestr("TinySOL/audio/Strings/Violin/ordinario/Vn-ord-G6-mf-1cR.wav", wav)
    return metadata, archive


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        header = file.readline().rstrip("\n").split("\t")
        if header != ["id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities"]:
            raise AssertionError(f"unexpected header: {header}")
        return [line.rstrip("\n").split("\t") for line in file if line.strip()]


def run_prepare(base, include_resampled=False, min_samples=3, current_header=False):
    metadata, archive = make_fixture(base, current_header=current_header)
    output = base / "out"
    args = [
        "--metadata", str(metadata),
        "--archive", str(archive),
        "--output", str(output),
        "--min-samples", str(min_samples),
    ]
    if include_resampled:
        args.append("--include-resampled")
    prepare_tinysol_samples.main(args)
    return output


def test_tinysol_families_and_manifest_paths():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp))
        rows = manifest_rows(output / "manifest.tsv")
        families = [row[1] for row in rows]
        notes = [row[5] for row in rows]
        if families != ["bass", "other", "piano"]:
            raise AssertionError(f"unexpected family mapping: {families}")
        if notes != ["E2", "A4", "C4"]:
            raise AssertionError(f"unexpected note mapping: {notes}")
        for row in rows:
            if not (output / row[6]).is_file():
                raise AssertionError(f"missing copied audio {row[6]}")


def test_resampled_rows_are_optional():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), include_resampled=True, min_samples=4)
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 4:
            raise AssertionError(f"expected four rows with resampled enabled, got {len(rows)}")
        if "G6" not in [row[5] for row in rows]:
            raise AssertionError("expected resampled violin row to be retained")


def test_current_tinysol_header_is_supported():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), current_header=True)
        rows = manifest_rows(output / "manifest.tsv")
        families = [row[1] for row in rows]
        sources = [row[3] for row in rows]
        if families != ["bass", "other", "piano"]:
            raise AssertionError(f"unexpected family mapping with current header: {families}")
        if sources != ["contrabass", "flute", "accordion"]:
            raise AssertionError(f"unexpected sources with current header: {sources}")


def test_minimum_failure_writes_partial_manifest():
    with tempfile.TemporaryDirectory() as temp:
        try:
            run_prepare(Path(temp), min_samples=4)
        except SystemExit:
            rows = manifest_rows(Path(temp) / "out" / "manifest.tsv.partial")
            if len(rows) != 3:
                raise AssertionError("partial manifest should contain prepared non-resampled rows")
        else:
            raise AssertionError("expected min-samples failure")


def main():
    test_tinysol_families_and_manifest_paths()
    test_resampled_rows_are_optional()
    test_current_tinysol_header_is_supported()
    test_minimum_failure_writes_partial_manifest()
    print("test_prepare_tinysol_samples: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
