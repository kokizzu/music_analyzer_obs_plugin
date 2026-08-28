#!/usr/bin/env python3
"""Stage only the verified high-soprano vocal display recovery."""

from __future__ import annotations

import difflib
import subprocess


PATHS = (
    "src/analyzer.hpp",
    "src/analyzer.cpp",
    "Makefile",
    "tests/test_high_soprano_vocal_mirror.py",
    "scripts/summarize_high_soprano_mirror_result.py",
)


def run(*args: str, input_text: str | None = None) -> str:
    return subprocess.run(args, check=True, input=input_text, text=True, stdout=subprocess.PIPE).stdout


def patch_for(path: str, before: str, after: str) -> str:
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}", n=3,
    ))


def main() -> int:
    if run("git", "diff", "--cached", "--name-only").strip():
        raise RuntimeError("refusing to modify a non-empty index")

    header = run("git", "show", "HEAD:src/analyzer.hpp")
    if header.count("kEnableMeasuredHighSopranoVocalMirror = false") != 1:
        raise RuntimeError("unexpected high-soprano feature flag in HEAD")
    header_target = header.replace(
        "kEnableMeasuredHighSopranoVocalMirror = false",
        "kEnableMeasuredHighSopranoVocalMirror = true",
    )

    source = run("git", "show", "HEAD:src/analyzer.cpp")
    old_profile = '''\t// Independent Dagstuhl and ESMUC choir windows retain F5/F#5 as a real
\t// Keyboard candidate while the expected Vocal row is empty. The same
\t// noisy-second-partial profile is absent from the protected real-note set.
\treturn debug.owner == InstrumentKind::Keyboard && debug.midi >= 77 && debug.midi <= 78 &&
\t       debug.local_noise_level >= 0.024f && debug.harmonic_ratios[1] >= 0.114f;
'''
    new_profile = '''\t// Independent Dagstuhl and ESMUC choir windows retain F5/F#5 as a real
\t// Keyboard candidate while the expected Vocal row is empty. This narrower
\t// cross-choir profile avoids the broader noisy-partial match seen in other
\t// compact real-instrument fixtures.
\treturn debug.owner == InstrumentKind::Keyboard && debug.midi >= 77 && debug.midi <= 78 &&
\t       debug.adjacent_upper_ratio >= 0.032f && debug.local_noise_level >= 0.122f &&
\t       debug.pitch_confidence <= 0.814f;
'''
    if source.count(old_profile) != 1:
        raise RuntimeError("unexpected high-soprano mirror profile in HEAD")
    source_target = source.replace(old_profile, new_profile)

    makefile = run("git", "show", "HEAD:Makefile")
    anchor = '''test-ambiguous-display-recovery: analyze-real-note-attributes tests/test_ambiguous_display_recovery.py
\t@python3 tests/test_ambiguous_display_recovery.py
'''
    addition = '''
.PHONY: test-high-soprano-vocal-mirror
test-high-soprano-vocal-mirror: tests/test_high_soprano_vocal_mirror.py
\t$(PYTHON) tests/test_high_soprano_vocal_mirror.py

.PHONY: summarize-high-soprano-vocal-mirror-result
summarize-high-soprano-vocal-mirror-result: scripts/summarize_high_soprano_mirror_result.py
\t$(PYTHON) scripts/summarize_high_soprano_mirror_result.py
'''
    if makefile.count(anchor) != 1 or addition in makefile:
        raise RuntimeError("unexpected Makefile high-soprano target anchor")
    makefile_target = makefile.replace(anchor, anchor + addition)

    combined = patch_for("src/analyzer.hpp", header, header_target)
    combined += patch_for("src/analyzer.cpp", source, source_target)
    combined += patch_for("Makefile", makefile, makefile_target)
    subprocess.run(["git", "apply", "--cached"], check=True, input=combined, text=True)
    subprocess.run(["git", "add", "--", *PATHS[3:]], check=True)
    staged = run("git", "diff", "--cached", "--name-only").splitlines()
    if staged != list(PATHS):
        raise RuntimeError(f"unexpected staged scope: {staged}")
    print("staged verified high-soprano vocal mirror")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
