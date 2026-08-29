#!/usr/bin/env python3
"""Commit or push the external real-drum corpus diagnostics without staging user work."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATHS = (
    "scripts/inspect_drum_detector_source.py",
    "scripts/inspect_real_drum_runner.py",
    "scripts/manage_real_drum_corpus_coverage.py",
    "scripts/report_external_drum_manifests.py",
    "scripts/report_real_drum_corpus.sh",
)
MAKEFILE_BLOCKS = (
    """.PHONY: inspect-real-drum-runner
inspect-real-drum-runner: scripts/inspect_real_drum_runner.py
\tpython3 scripts/inspect_real_drum_runner.py
""",
    """.PHONY: report-external-drum-manifests
report-external-drum-manifests: scripts/report_external_drum_manifests.py
\tpython3 scripts/report_external_drum_manifests.py
""",
    """.PHONY: report-real-drum-corpus
report-real-drum-corpus: build/analyzer_real_drum_samples scripts/report_real_drum_corpus.sh
\tsh scripts/report_real_drum_corpus.sh

.PHONY: report-real-drum-corpus-debug
report-real-drum-corpus-debug: build/analyzer_real_drum_samples scripts/report_real_drum_corpus.sh
\tsh scripts/report_real_drum_corpus.sh --verbose
""",
    """.PHONY: commit-real-drum-corpus-coverage
commit-real-drum-corpus-coverage: scripts/manage_real_drum_corpus_coverage.py
\tpython3 scripts/manage_real_drum_corpus_coverage.py commit

.PHONY: push-real-drum-corpus-coverage
push-real-drum-corpus-coverage: scripts/manage_real_drum_corpus_coverage.py
\tpython3 scripts/manage_real_drum_corpus_coverage.py push
""",
)
MESSAGE = "test: add external real drum corpus diagnostics"


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, check=True, capture_output=capture)
    return result.stdout if capture else ""


def ensure_no_external_staging() -> None:
    staged = [line for line in run("git", "diff", "--cached", "--name-only", capture=True).splitlines() if line]
    if staged:
        raise RuntimeError(f"refusing to commit pre-staged paths: {', '.join(staged)}")


def stage_makefile_targets() -> None:
    worktree = (ROOT / "Makefile").read_text(encoding="utf-8")
    index = run("git", "show", ":Makefile", capture=True)
    for block in MAKEFILE_BLOCKS:
        if block not in worktree:
            raise RuntimeError("required Makefile target block is missing from worktree")
        if block not in index:
            if not index.endswith("\n"):
                index += "\n"
            index += "\n" + block
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=ROOT) as staged:
        staged.write(index)
        staged_path = Path(staged.name)
    try:
        blob = run("git", "hash-object", "-w", str(staged_path), capture=True).strip()
    finally:
        staged_path.unlink(missing_ok=True)
    run("git", "update-index", "--add", "--cacheinfo", "100644", blob, "Makefile")


def commit() -> None:
    ensure_no_external_staging()
    missing = [path for path in PATHS if not (ROOT / path).is_file()]
    if missing:
        raise RuntimeError(f"missing coverage paths: {', '.join(missing)}")
    run("git", "add", "--", *PATHS)
    stage_makefile_targets()
    run("git", "commit", "-m", MESSAGE)


def push() -> None:
    run("git", "fetch", "origin", "master")
    run("git", "merge-base", "--is-ancestor", "origin/master", "HEAD")
    run("git", "push", "origin", "HEAD:master")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"commit", "push"}:
        print("usage: manage_real_drum_corpus_coverage.py commit|push", file=sys.stderr)
        return 2
    try:
        if sys.argv[1] == "commit":
            commit()
        else:
            push()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"real-drum-corpus-coverage: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
