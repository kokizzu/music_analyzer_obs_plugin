#!/usr/bin/env python3
"""Commit only the external MedleyDB BasicPitch context coverage changes."""

from __future__ import annotations

import difflib
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "README.md",
    "scripts/prepare_medleydb_vocal_mix_fixtures.py",
    "scripts/test_basic_pitch_medleydb_context.py",
    "tests/basic_pitch_medleydb_context.cpp",
)
MAKE_BLOCK = """.PHONY: report-basic-pitch-medleydb-mix-context report-basic-pitch-medleydb-stem-context test-basic-pitch-medleydb-context
$(BUILD_DIR)/basic_pitch_medleydb_context.o: tests/basic_pitch_medleydb_context.cpp src/analyzer.hpp src/basic_pitch_onnx_runtime.hpp src/basic_pitch_onnx_worker.hpp src/basic_pitch_pcm_history.hpp | $(BUILD_DIR)
\t$(CXX) $(CXXFLAGS) -Isrc -Itests -I$(BTT_SOURCE_DIR) -c $< -o $@

$(BUILD_DIR)/basic_pitch_medleydb_context: $(ANALYZER_TEST_OBJ) $(BUILD_DIR)/basic_pitch_medleydb_context.o
\t$(CXX) $(LDFLAGS) -o $@ $^ -ldl -lm -pthread

report-basic-pitch-medleydb-mix-context: $(BUILD_DIR)/basic_pitch_medleydb_context apply-medleydb-vocal-mix-fixtures $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
\t$(BUILD_DIR)/basic_pitch_medleydb_context "$(BUILD_DIR)/medleydb_vocal_mix_context_samples" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)"

report-basic-pitch-medleydb-stem-context: $(BUILD_DIR)/basic_pitch_medleydb_context apply-medleydb-vocal-mix-fixtures $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL)
\t$(BUILD_DIR)/basic_pitch_medleydb_context "$(BUILD_DIR)/medleydb_vocal_stem_context_samples" "$(ONNXRUNTIME_LIBRARY)" "$(BASIC_PITCH_ONNX_MODEL)"

test-basic-pitch-medleydb-context: $(BUILD_DIR)/basic_pitch_medleydb_context apply-medleydb-vocal-mix-fixtures $(ONNXRUNTIME_LIBRARY) $(BASIC_PITCH_ONNX_MODEL) scripts/test_basic_pitch_medleydb_context.py
\t$(PYTHON) scripts/test_basic_pitch_medleydb_context.py

"""
ANCHOR = ".PHONY: plan-medleydb-vocal-fixture-update-commit"


def git(*args: str, capture: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=capture)
    if result.returncode:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(f"git {' '.join(args)} failed: {result.returncode}")
    return result.stdout


def stage_makefile_block() -> None:
    if git("diff", "--cached", "--name-only", "--", "Makefile").strip():
        raise RuntimeError("refusing to alter an already staged Makefile")
    head = git("show", "HEAD:Makefile")
    if MAKE_BLOCK in head:
        return
    if ANCHOR not in head:
        raise RuntimeError("Makefile anchor not found in HEAD")
    updated = head.replace(ANCHOR, MAKE_BLOCK + ANCHOR, 1)
    patch = "".join(difflib.unified_diff(
        head.splitlines(keepends=True), updated.splitlines(keepends=True),
        fromfile="a/Makefile", tofile="b/Makefile",
    ))
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as temporary:
        temporary.write(patch)
        patch_path = Path(temporary.name)
    try:
        git("apply", "--cached", "--whitespace=nowarn", str(patch_path))
    finally:
        patch_path.unlink(missing_ok=True)


def staged_paths() -> list[str]:
    return [path for path in git("diff", "--cached", "--name-only").splitlines() if path]


def plan() -> int:
    print("worktree-status=")
    print(git("status", "--short"), end="")
    print("commit-paths=")
    for path in (*FILES, "Makefile", Path(__file__).relative_to(REPO_ROOT).as_posix()):
        print(path)
    return 0


def commit() -> int:
    stage_makefile_block()
    git("add", "--", *FILES, Path(__file__).relative_to(REPO_ROOT).as_posix(), capture=False)
    allowed = set((*FILES, "Makefile", Path(__file__).relative_to(REPO_ROOT).as_posix()))
    staged = staged_paths()
    unexpected = sorted(set(staged) - allowed)
    if unexpected:
        raise RuntimeError(f"refusing unexpected staged paths: {', '.join(unexpected)}")
    required = allowed
    missing = sorted(required - set(staged))
    if missing:
        raise RuntimeError(f"expected staged paths are missing: {', '.join(missing)}")
    git("commit", "-m", "test: cover BasicPitch MedleyDB vocal contexts", capture=False)
    return 0


def push() -> int:
    git("push", capture=False)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "commit", "push"}:
        print(f"usage: {Path(sys.argv[0]).name} plan|commit|push", file=sys.stderr)
        raise SystemExit(2)
    try:
        raise SystemExit({"plan": plan, "commit": commit, "push": push}[sys.argv[1]]())
    except RuntimeError as error:
        print(f"manage_basic_pitch_medleydb_context_commit: {error}", file=sys.stderr)
        raise SystemExit(1)
