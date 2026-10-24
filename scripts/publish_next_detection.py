#!/usr/bin/env python3
"""Plan/review/publish an explicit measurement checkpoint on verified primary."""
import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "build/next_detection_publication.json"
PATHS = ["accuracy_next.mk", "docs/next_detection_improvements.md",
         "scripts/inspect_primary_branch.py", "scripts/publish_next_detection.py",
         "scripts/measure_sustained_analyzer.py", "scripts/evaluate_next_detection.py",
         "scripts/evaluate_source_tempo_histories.py", "tests/analyzer_sustained.cpp",
         "tests/test_sustained_analyzer.py", "tests/test_next_detection.py",
         "src/tempo_candidate_gate.hpp", "src/pcm_tempo_selection.hpp",
         "src/pcm_tempo_evidence.hpp", "tests/tempo_candidate_gate.cpp",
         "scripts/measure_sustained_piano.py", "scripts/midi_sustain_reference.py",
         "tests/test_sustained_piano.py"]


def git(*args, data=None):
    return subprocess.run(["git", *args], cwd=ROOT, input=data, text=True,
                          capture_output=True, check=True, timeout=60).stdout


def identity():
    branch = git("branch", "--show-current").strip()
    remote = git("config", "--get", "branch." + branch + ".remote").strip()
    merge = git("config", "--get", "branch." + branch + ".merge").strip()
    url = git("remote", "get-url", remote).strip()
    assert url in ("git@github.com:kokizzu/music_analyzer_obs_plugin.git",
                   "https://github.com/kokizzu/music_analyzer_obs_plugin.git"), "Unexpected upstream identity"
    observed = git("ls-remote", "--symref", remote, "HEAD")
    primary = next(line.split()[1] for line in observed.splitlines() if line.startswith("ref:"))
    tip = next(line.split()[0] for line in observed.splitlines() if not line.startswith("ref:") and line.endswith("\tHEAD"))
    assert primary in ("refs/heads/main", "refs/heads/master") and merge == primary and branch == primary.removeprefix("refs/heads/"), "Not tracked primary branch"
    return branch, remote, primary, tip


def checks():
    for target in ("test-next-detection", "test-tempo-candidate-gate", "test-sustained-analyzer", "test-sustained-piano"):
        subprocess.run(["make", target], cwd=ROOT, check=True)
    # Validate the benchmark against the actual primary-branch interface too;
    # local uncommitted fields must not become hidden publication dependencies.
    with tempfile.TemporaryDirectory(prefix="next-detection-syntax-") as temporary:
        base = Path(temporary)
        pending = ["analyzer.hpp"]
        seen = set()
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            seen.add(name)
            text = git("show", "HEAD:src/" + name)
            (base / name).parent.mkdir(parents=True, exist_ok=True)
            (base / name).write_text(text)
            pending.extend(re.findall(r'^#include "([^"]+)"', text, flags=re.MULTILINE))
        subprocess.run(["g++", "-std=c++17", "-fsyntax-only", "-I" + str(base),
                        str(ROOT / "tests/analyzer_sustained.cpp")], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "stage", "commit", "push"))
    args = parser.parse_args()
    branch, remote, primary, tip = identity()
    if args.mode == "plan":
        assert not git("diff", "--cached", "--name-only").strip(), "Preserve existing staged work"
        head = git("rev-parse", "HEAD").strip()
        assert head == tip, "Existing unpushed/remote work needs review before scoped publication"
        for path in PATHS:
            assert not git("ls-files", "--", path).strip(), "Checkpoint path already tracked: " + path
        base = git("show", "HEAD:Makefile")
        staged_make = base + "\n# Detection measurement checkpoint.\ninclude accuracy_next.mk\n"
        patch = "".join(difflib.unified_diff(base.splitlines(True), staged_make.splitlines(True), fromfile="a/Makefile", tofile="b/Makefile"))
        for path in PATHS:
            text = (ROOT / path).read_text()
            patch += "".join(difflib.unified_diff([], text.splitlines(True), fromfile="/dev/null", tofile="b/" + path))
        PLAN.parent.mkdir(parents=True, exist_ok=True)
        PLAN.with_suffix(".patch").write_text(patch)
        state = dict(head=head, branch=branch, remote=remote, primary=primary,
                     paths={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in PATHS},
                     staged_make=staged_make)
        PLAN.write_text(json.dumps(state, indent=2) + "\n")
        print(json.dumps(dict(paths=PATHS, patch=str(PLAN.with_suffix('.patch').relative_to(ROOT)), branch=branch), indent=2))
        return
    state = json.loads(PLAN.read_text())
    assert (branch, remote, primary) == (state["branch"], state["remote"], state["primary"])
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in state["paths"].items()), "Planned files changed"
    if args.mode == "stage":
        assert git("rev-parse", "HEAD").strip() == state["head"] == tip
        assert not git("diff", "--cached", "--name-only").strip()
        checks()
        git("add", "--", *PATHS)
        blob = git("hash-object", "-w", "--stdin", data=state["staged_make"]).strip()
        git("update-index", "--cacheinfo", "100644," + blob + ",Makefile")
        git("diff", "--cached", "--check")
        print(git("diff", "--cached", "--stat"))
        return
    if args.mode == "commit":
        assert git("rev-parse", "HEAD").strip() == state["head"] == tip
        assert set(git("diff", "--cached", "--name-only").splitlines()) == set(PATHS + ["Makefile"])
        assert git("show", ":Makefile") == state["staged_make"]
        for path in PATHS:
            assert hashlib.sha256(git("show", ":" + path).encode()).hexdigest() == state["paths"][path]
        git("diff", "--cached", "--check")
        print(git("commit", "-m", "Add causal detection screens and sustained playback benchmarks"))
        state["commit"] = git("rev-parse", "HEAD").strip()
        PLAN.write_text(json.dumps(state, indent=2) + "\n")
        return
    assert git("rev-parse", "HEAD").strip() == state["commit"]
    assert git("rev-parse", "HEAD^").strip() == state["head"]
    assert tip in (state["head"], state["commit"]), "Remote advanced; safe reconciliation required"
    assert not git("diff", "--cached", "--name-only").strip()
    print(git("push", remote, "HEAD:" + primary))
    assert identity()[3] == state["commit"]
    print("Published", state["commit"], "to", primary)


if __name__ == "__main__":
    main()
