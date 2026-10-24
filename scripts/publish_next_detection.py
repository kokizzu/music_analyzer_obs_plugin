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
PATHS += ['scripts/evaluate_backbeat_tempo.py', 'tests/test_backbeat_tempo.py',
          'scripts/evaluate_chord_source_agreement.py', 'scripts/evaluate_drum_attack_shapes.py',
          'tests/test_drum_attack_shapes.py', 'scripts/evaluate_keyboard_voice_classifier.py',
          'scripts/export_keyboard_voice_model.py', 'scripts/evaluate_native_mfcc_voice.py',
          'scripts/export_native_mfcc_voice.py', 'scripts/native_timbre_reference.py',
          'models/keyboard_voice_classifier.json', 'models/native_mfcc_voice.json',
          'src/keyboard_voice_classifier.hpp', 'src/keyboard_voice_model_data.hpp',
          'src/native_timbre_features.hpp', 'src/native_mfcc_voice.hpp', 'src/native_mfcc_voice_model_data.hpp',
          'tests/keyboard_voice_classifier.cpp', 'tests/test_keyboard_voice_classifier.py',
          'tests/native_timbre_features.cpp', 'tests/test_native_timbre_reference.py',
          'tests/native_mfcc_voice.cpp', 'tests/test_native_mfcc_voice.py', 'tests/native_mfcc_voice_vectors.json',
          'tests/pcm_tempo_score_cache.cpp']
PATHS += ['scripts/prepare_native_voice_primary.py', 'scripts/measure_keyboard_voice_pair.py',
          'tests/native_keyboard_voice_pair.cpp', 'tests/non_tempo_snapshot.hpp',
          'src/experimental_keyboard_voice_hook.inc']


def publication_text(path):
    text = (ROOT / path).read_text()
    if path == 'accuracy_next.mk':
        # Keep replay targets that depend on older unpublished analyzer/harness
        # work local; publish independently buildable libraries and screens.
        blocked = ('capture-', 'audit-keyboard-', 'native_mfcc_voice_evidence_replay',
                   'native_keyboard_voice_replay', 'native_keyboard_voice_pair',
                   'measure-keyboard-voice-', 'native_temporal_voice_evidence_replay')
        text = '\n\n'.join(block for block in text.split('\n\n') if not any(token in block for token in blocked))
        text = text.rstrip() + '\n'
    return text


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
    for target in ("test-next-detection", "test-tempo-candidate-gate", "test-sustained-analyzer", "test-sustained-piano",
                   'test-backbeat-tempo', 'test-drum-attack-shapes', 'test-keyboard-voice-classifier',
                   'test-native-timbre-features', 'test-native-timbre-reference', 'test-native-mfcc-voice', 'test-pcm-tempo-score-cache'):
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
        base = git("show", "HEAD:Makefile")
        staged_make = base if 'include accuracy_next.mk' in base else base + "\n# Detection measurement checkpoint.\ninclude accuracy_next.mk\n"
        patch = "".join(difflib.unified_diff(base.splitlines(True), staged_make.splitlines(True), fromfile="a/Makefile", tofile="b/Makefile"))
        contents = {}
        for path in PATHS:
            text = publication_text(path)
            tracked = bool(git('ls-files', '--', path).strip())
            previous = git('show', 'HEAD:' + path) if tracked else ''
            if text == previous:
                continue
            contents[path] = text
            patch += "".join(difflib.unified_diff(previous.splitlines(True), text.splitlines(True), fromfile='a/' + path if tracked else '/dev/null', tofile="b/" + path))
        PLAN.parent.mkdir(parents=True, exist_ok=True)
        PLAN.with_suffix(".patch").write_text(patch)
        state = dict(head=head, branch=branch, remote=remote, primary=primary,
                     paths={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in contents},
                     contents=contents, make_changed=base != staged_make,
                     staged_make=staged_make)
        PLAN.write_text(json.dumps(state, indent=2) + "\n")
        print(json.dumps(dict(paths=list(contents), patch=str(PLAN.with_suffix('.patch').relative_to(ROOT)), branch=branch), indent=2))
        return
    state = json.loads(PLAN.read_text())
    assert (branch, remote, primary) == (state["branch"], state["remote"], state["primary"])
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in state["paths"].items()), "Planned files changed"
    if args.mode == "stage":
        assert git("rev-parse", "HEAD").strip() == state["head"] == tip
        assert not git("diff", "--cached", "--name-only").strip()
        checks()
        for path, content in state['contents'].items():
            assert publication_text(path) == content
            blob = git('hash-object', '-w', '--stdin', data=content).strip()
            git('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + path)
        if state['make_changed']:
            blob = git("hash-object", "-w", "--stdin", data=state["staged_make"]).strip()
            git("update-index", "--cacheinfo", "100644," + blob + ",Makefile")
        git("diff", "--cached", "--check")
        print(git("diff", "--cached", "--stat"))
        return
    if args.mode == "commit":
        assert git("rev-parse", "HEAD").strip() == state["head"] == tip
        assert set(git("diff", "--cached", "--name-only").splitlines()) == set(list(state['contents']) + (["Makefile"] if state['make_changed'] else []))
        assert git("show", ":Makefile") == state["staged_make"]
        for path, content in state['contents'].items():
            assert git("show", ":" + path) == content
        git("diff", "--cached", "--check")
        print(git("commit", "-m", "Add native spectral verification and cache exact tempo scoring"))
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
