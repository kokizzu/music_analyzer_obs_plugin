#!/usr/bin/env python3
"""Refresh derived analyzer attribute row dumps without rerunning analyzers."""

from __future__ import annotations

import argparse
import concurrent.futures
import pathlib
import subprocess
import sys
import tempfile


DRUMS = ("kick", "tom", "snare", "hihat", "crash", "ride", "rim")
FULL_DRUMS = ("kick", "snare", "tom", "rim")


def existing(paths: list[pathlib.Path]) -> bool:
    return all(path.exists() for path in paths)


def stale(sources: list[pathlib.Path], outputs: list[pathlib.Path]) -> bool:
    if not existing(sources):
        return False
    if not existing(outputs):
        return True
    newest_source = max(path.stat().st_mtime for path in sources)
    oldest_output = min(path.stat().st_mtime for path in outputs)
    return newest_source > oldest_output


def write_command(output: pathlib.Path, command: list[str], script_root: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=output.parent, delete=False) as handle:
        temp_path = pathlib.Path(handle.name)
        try:
            subprocess.run(command, cwd=script_root, check=True, text=True, stdout=handle)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
    temp_path.replace(output)


def script(script_root: pathlib.Path, name: str) -> str:
    return str(script_root / "scripts" / name)


def run_commands(
    commands: list[tuple[pathlib.Path, list[str]]],
    script_root: pathlib.Path,
    jobs: int,
) -> None:
    if not commands:
        return
    if jobs <= 1 or len(commands) == 1:
        for output, command in commands:
            write_command(output, command, script_root)
        return

    workers = min(jobs, len(commands))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(write_command, output, command, script_root)
            for output, command in commands
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()


def refresh(build_dir: pathlib.Path, script_root: pathlib.Path, python: str, jobs: int) -> None:
    commands: list[tuple[pathlib.Path, list[str]]] = []

    instrument_inspector = pathlib.Path(script(script_root, "inspect_instrument_sample_owner_buckets.py"))
    instrument_source = build_dir / "instrument_sample_attributes.tsv"
    instrument_output = build_dir / "instrument_detected_attribute_rows.tsv"
    if stale([instrument_source, instrument_inspector], [instrument_output]):
        commands.append(
            (
                instrument_output,
                [
                    python,
                    str(instrument_inspector),
                    str(instrument_source),
                    "--dump-rows",
                ],
            )
        )

    real_inspector = pathlib.Path(script(script_root, "inspect_real_note_attribute_buckets.py"))
    real_source = build_dir / "real_note_full_mix_attributes.tsv"
    real_output = build_dir / "real_note_detected_attribute_rows.tsv"
    real_miss_output = build_dir / "real_note_miss_attribute_rows.tsv"
    if stale([real_source, real_inspector], [real_output, real_miss_output]):
        base_command = [
            python,
            str(real_inspector),
            str(real_source),
            "--dump-rows",
        ]
        commands.append((real_output, base_command))
        commands.append((real_miss_output, base_command + ["--misses-only"]))

    guitar_inspector = pathlib.Path(script(script_root, "inspect_guitarset_attribute_buckets.py"))
    guitar_source = build_dir / "guitar_chord_mix_attributes.tsv"
    guitar_output = build_dir / "guitar_chord_detected_attribute_rows.tsv"
    guitar_miss_output = build_dir / "guitar_chord_miss_attribute_rows.tsv"
    if stale([guitar_source, guitar_inspector], [guitar_output, guitar_miss_output]):
        base_command = [
            python,
            str(guitar_inspector),
            str(guitar_source),
            "--dump-rows",
        ]
        commands.append((guitar_output, base_command))
        commands.append((guitar_miss_output, base_command + ["--misses-only"]))

    drum_analyzer = pathlib.Path(script(script_root, "analyze_drum_primary_debug.py"))
    primary_sources = [build_dir / f"{drum}_primary_debug.err" for drum in DRUMS]
    primary_output = build_dir / "drum_primary_miss_attribute_rows.tsv"
    if stale(primary_sources + [drum_analyzer], [primary_output]):
        commands.append(
            (
                primary_output,
                [
                    python,
                    str(drum_analyzer),
                    "--dump-rows",
                    "--include-debug-rows",
                    *(str(path) for path in primary_sources),
                ],
            )
        )

    full_sources = [build_dir / f"full_{drum}_debug.err" for drum in FULL_DRUMS]
    full_output = build_dir / "drum_full_attribute_rows.tsv"
    if stale(full_sources + [drum_analyzer], [full_output]):
        commands.append(
            (
                full_output,
                [
                    python,
                    str(drum_analyzer),
                    "--dump-rows",
                    "--include-debug-rows",
                    *(str(path) for path in full_sources),
                ],
            )
        )

    run_commands(commands, script_root, jobs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=pathlib.Path, default=pathlib.Path("build"))
    parser.add_argument("--script-root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1])
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()

    refresh(args.build_dir, args.script_root, args.python, max(1, args.jobs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
