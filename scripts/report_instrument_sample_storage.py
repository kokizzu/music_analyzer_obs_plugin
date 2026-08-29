#!/usr/bin/env python3
"""Report the configured external location used for instrument fixtures."""

from __future__ import annotations

import os
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"
PATTERN = re.compile(
    r"^\s*(?:export\s+)?(INSTRUMENT_SAMPLE_[A-Z_]+|MUSIC_ANALYZER_INSTRUMENT_[A-Z_]+)\s*[:?+]?=\s*(.*)$"
)


def main() -> int:
    print(f"repository={ROOT}")
    print(f"repository_realpath={ROOT.resolve()}")
    print("makefile_variables:")
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        match = PATTERN.match(line)
        if match:
            print(f"  {match.group(1)}={match.group(2)}")

    makefile_text = MAKEFILE.read_text(encoding="utf-8")
    missing_scripts = []
    for match in re.finditer(r"scripts/([A-Za-z0-9_.-]+\.py)", makefile_text):
        relative = Path("scripts") / match.group(1)
        if not (ROOT / relative).is_file() and relative not in missing_scripts:
            missing_scripts.append(relative)
    print(f"makefile_missing_python_scripts={len(missing_scripts)}")
    for relative in missing_scripts:
        print(f"  {relative}")
        for number, line in enumerate(makefile_text.splitlines(), start=1):
            if str(relative) in line:
                print(f"    makefile:{number}: {line.strip()}")

    print("environment:")
    for name in (
        "INSTRUMENT_SAMPLE_BUILD_ROOT",
        "INSTRUMENT_SAMPLE_SOURCE_DIR",
        "MUSIC_ANALYZER_INSTRUMENT_SAMPLE_ROOT",
    ):
        value = os.environ.get(name, "")
        if not value:
            print(f"  {name}=<unset>")
            continue
        path = Path(value)
        print(f"  {name}={path}")
        print(f"  {name}_exists={path.exists()}")
        print(f"  {name}_is_symlink={path.is_symlink()}")
        if path.exists() or path.is_symlink():
            print(f"  {name}_realpath={path.resolve()}")

    print("repository_sample_paths:")
    for relative in (
        "build/InstrumentSamples",
        "build/instrument_sample_sources",
        "build/piano_samples",
        "build/bass_samples",
    ):
        path = ROOT / relative
        print(f"  {relative}_exists={path.exists()}")
        print(f"  {relative}_is_symlink={path.is_symlink()}")
        if path.exists() or path.is_symlink():
            print(f"  {relative}_realpath={path.resolve()}")

    external_store = Path("/media/kyz/sshflashtor/InstrumentSamples")
    print("sneakybass_fixture_paths:")
    for relative in (
        "sources/sneakybass/sneakybass.zip",
        "sources/sneakybass/sneakybass.zip.part",
        "sources/sneakybass",
        "real-fixtures/sneakybass/manifest.tsv",
    ):
        path = external_store / relative
        exists = path.exists() or path.is_symlink()
        print(f"  {relative}_exists={exists}")
        if path.is_file():
            print(f"  {relative}_bytes={path.stat().st_size}")
            if path.suffix == ".part" and path.name.endswith(".zip.part"):
                valid = zipfile.is_zipfile(path)
                print(f"  {relative}_valid_zip={valid}")
                if valid:
                    with zipfile.ZipFile(path) as archive:
                        print(f"  {relative}_entries={len(archive.infolist())}")

    source_root = external_store / "sources" / "sneakybass"
    if source_root.is_dir():
        extensions: dict[str, int] = {}
        for candidate in source_root.rglob("*"):
            if candidate.is_file():
                suffix = candidate.suffix.lower() or "<none>"
                extensions[suffix] = extensions.get(suffix, 0) + 1
        print("sneakybass_source_extensions:")
        for suffix, count in sorted(extensions.items()):
            print(f"  {suffix}={count}")
        sfz_files = sorted(candidate for candidate in source_root.rglob("*")
                           if candidate.is_file() and candidate.suffix.lower() == ".sfz")
        print(f"sneakybass_sfz_files={len(sfz_files)}")
        print("sneakybass_sfz_sample_counts:")
        for sfz in sfz_files:
            count = sum("sample=" in line.lower()
                        for line in sfz.read_text(encoding="utf-8", errors="replace").splitlines())
            if count:
                print(f"  {sfz.relative_to(source_root)}={count}")
        for sfz in sfz_files[:3]:
            print(f"  sfz={sfz.relative_to(source_root)}")
            lines = sfz.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in lines[:8]:
                print(f"    {line}")
            sample_lines = [line for line in lines if "sample=" in line.lower()]
            for line in sample_lines[:4]:
                print(f"    sample: {line}")
        mapped_files = [sfz for sfz in sfz_files
                        if "sample=" in sfz.read_text(encoding="utf-8", errors="replace").lower()]
        if mapped_files:
            mapped = mapped_files[0]
            print(f"sneakybass_first_mapping={mapped.relative_to(source_root)}")
            for line in mapped.read_text(encoding="utf-8", errors="replace").splitlines()[:24]:
                print(f"  {line}")
            sample_value = next(
                (line.split("=", 1)[1].strip() for line in mapped.read_text(
                    encoding="utf-8", errors="replace").splitlines() if line.lower().startswith("sample=")),
                "",
            )
            if sample_value:
                sample_path = (mapped.parent / sample_value.replace("\\", "/")).resolve()
                print(f"  first_sample_path={sample_path}")
                print(f"  first_sample_exists={sample_path.is_file()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
