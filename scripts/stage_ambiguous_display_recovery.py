#!/usr/bin/env python3
"""Stage only the ambiguous shared keyboard/guitar display recovery change."""

from __future__ import annotations

import argparse
import difflib
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = "src/analyzer.cpp"
TEST_PATH = "tests/test_ambiguous_display_recovery.py"
MAKEFILE_PATH = "Makefile"
HELPER = (
    "bool ambiguous_shared_keyboard_guitar_display_supported(FullMixDisplayRow row,\n"
    "\t\t\t\t\t\t\t const FullMixDebugCandidate &debug,\n"
    "\t\t\t\t\t\t\t int display_midi)\n{\n"
    "\tif (debug.owner != InstrumentKind::Ambiguous || display_midi != debug.midi ||\n"
    "\t    debug.spectral_level < 0.80f || debug.pitch_confidence < 0.75f ||\n"
    "\t    debug.periodicity < 0.60f || debug.local_noise_level > 0.18f)\n"
    "\t\treturn false;\n"
    "\tif (row == FullMixDisplayRow::Keyboard)\n"
    "\t\treturn display_midi >= 48 && display_midi <= 84;\n"
    "\tif (row == FullMixDisplayRow::Guitar)\n"
    "\t\treturn display_midi >= kGuitarMinMidi && display_midi <= 80;\n"
    "\treturn false;\n}\n\n"
)
MAKE_TARGET = (
    "\n.PHONY: test-ambiguous-display-recovery\n"
    "test-ambiguous-display-recovery: analyze-real-note-attributes tests/test_ambiguous_display_recovery.py\n"
    "\t@python3 tests/test_ambiguous_display_recovery.py\n"
)


def git_show(path: str) -> str:
    return subprocess.run(
        ["git", "show", f":{path}"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


def stage_text(path: str, content: str) -> None:
    blob = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"], cwd=ROOT, check=True,
        input=content, capture_output=True, text=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}"],
        cwd=ROOT, check=True,
    )


def staged_source(indexed: str) -> str:
    signature = (
        "bool full_mix_display_mirror_supported(FullMixDisplayRow row, const FullMixDebugCandidate &debug,\n"
        "\t\t\t\t       int display_midi)\n{\n"
    )
    if signature not in indexed:
        raise RuntimeError("indexed analyzer source no longer has the mirror gate signature")
    result = indexed.replace(signature, HELPER + signature, 1)
    start = result.index(signature)
    tail = "\t\treturn false;\n\n\tswitch (row) {"
    position = result.find(tail, start)
    if position < 0:
        raise RuntimeError("indexed mirror gate no longer has the expected switch boundary")
    replacement = (
        "\t\treturn false;\n"
        "\tif (ambiguous_shared_keyboard_guitar_display_supported(row, debug, display_midi))\n"
        "\t\treturn true;\n\n"
        "\tswitch (row) {"
    )
    return result[:position] + replacement + result[position + len(tail):]


def staged_makefile(indexed: str) -> str:
    if "test-ambiguous-display-recovery:" in indexed:
        raise RuntimeError("indexed Makefile already has the ambiguous display recovery target")
    return indexed.rstrip() + "\n" + MAKE_TARGET


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    args = parser.parse_args()
    indexed_source = git_show(SOURCE_PATH)
    indexed_makefile = git_show(MAKEFILE_PATH)
    source = staged_source(indexed_source)
    makefile = staged_makefile(indexed_makefile)
    test = (ROOT / TEST_PATH).read_text(encoding="utf-8")
    if args.mode == "plan":
        for path, before, after in ((SOURCE_PATH, indexed_source, source), (MAKEFILE_PATH, indexed_makefile, makefile)):
            print("".join(difflib.unified_diff(
                before.splitlines(keepends=True), after.splitlines(keepends=True),
                fromfile=f"a/{path}", tofile=f"b/{path}", n=3,
            )), end="")
        print(f"new file: {TEST_PATH} ({len(test.splitlines())} lines)")
        return 0
    stage_text(SOURCE_PATH, source)
    stage_text(MAKEFILE_PATH, makefile)
    subprocess.run(["git", "add", "--", TEST_PATH], cwd=ROOT, check=True)
    print(f"staged: {SOURCE_PATH}, {TEST_PATH}, {MAKEFILE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
