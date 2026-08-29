#!/usr/bin/env python3
"""Run the external Sneakybass analyzer audit and preserve its result log."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SUMMARY = re.compile(r"^real_bass_fixture: (\d+)/(\d+) expected pitch classes detected$", re.MULTILINE)
DEBUG_SUMMARY = re.compile(r"^real_bass_fixture_debug: spectral=(\d+) periodic=(\d+) total=(\d+)$", re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--fixture-root", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--attributes", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--source-name", default="double bass")
    args = parser.parse_args()
    if not args.binary.is_file():
        raise SystemExit(f"missing analyzer test binary: {args.binary}")
    if not (args.fixture_root / "manifest.tsv").is_file():
        raise SystemExit(f"missing Sneakybass fixture manifest: {args.fixture_root / 'manifest.tsv'}")
    if args.jobs < 1:
        raise SystemExit("--jobs must be positive")

    def run_shard(index: int) -> tuple[int, str, Path]:
        environment = os.environ.copy()
        environment["MUSIC_ANALYZER_SKIP_STANDARD_INSTRUMENT_SAMPLES"] = "1"
        environment["MUSIC_ANALYZER_REAL_BASS_FIXTURE_ROOT"] = str(args.fixture_root)
        environment["MUSIC_ANALYZER_REAL_BASS_SOURCE_NAME"] = args.source_name
        environment["MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_COUNT"] = str(args.jobs)
        environment["MUSIC_ANALYZER_INSTRUMENT_SAMPLE_SHARD_INDEX"] = str(index)
        attribute_path = staged_attributes / f"shard-{index:03d}.tsv"
        environment["MUSIC_ANALYZER_INSTRUMENT_ATTRIBUTE_TSV"] = str(attribute_path)
        completed = subprocess.run(
            [str(args.binary)],
            env=environment,
            cwd=args.binary.parent.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return completed.returncode, completed.stdout, attribute_path

    args.attributes.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sneakybass-attributes-", dir=args.attributes.parent) as temporary:
        staged_attributes = Path(temporary)
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            completed = list(executor.map(run_shard, range(args.jobs)))
        exit_code = max(result[0] for result in completed)
        output = "\n".join(
            f"[shard {index}]\n{result[1]}" for index, result in enumerate(completed)
        )
        parts = [result[2] for result in completed if result[2].is_file()]
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False,
                                         dir=args.attributes.parent) as staged:
            header = ""
            for part in parts:
                lines = part.read_text(encoding="utf-8", errors="replace").splitlines()
                if not lines:
                    continue
                if not header:
                    header = lines[0]
                    staged.write(header + "\n")
                elif lines[0] != header:
                    raise RuntimeError(f"attribute header mismatch: {part}")
                for line in lines[1:]:
                    staged.write(line + "\n")
            staged_path = Path(staged.name)
        staged_path.replace(args.attributes)
    payload = (
        f"timestamp_utc={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"exit_code={exit_code}\n"
        f"jobs={args.jobs}\n"
        f"source_name={args.source_name}\n"
        f"fixture={args.fixture_root}\n"
        f"\n{output}"
    )
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=args.log.parent) as staged:
        staged.write(payload)
        staged_path = Path(staged.name)
    staged_path.replace(args.log)
    matches = [tuple(int(value) for value in match.groups()) for match in SUMMARY.finditer(output)]
    if matches:
        detected = sum(match[0] for match in matches)
        total = sum(match[1] for match in matches)
        percent = 100.0 * detected / total if total else 0.0
        print(f"sneakybass_audit: detected={detected} total={total} recall={percent:.1f}%")
    else:
        print("sneakybass_audit: no result summary; inspect log")
    debug_matches = [tuple(int(value) for value in match.groups()) for match in DEBUG_SUMMARY.finditer(output)]
    if debug_matches:
        spectral = sum(match[0] for match in debug_matches)
        periodic = sum(match[1] for match in debug_matches)
        debug_total = sum(match[2] for match in debug_matches)
        print(f"sneakybass_audit_debug: spectral={spectral} periodic={periodic} total={debug_total}")
    print(f"sneakybass_audit_log={args.log}")
    print(f"sneakybass_audit_attributes={args.attributes}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
