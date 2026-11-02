#!/usr/bin/env python3
"""Build the previously screened stable-body variant without altering v1."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    identity()
    base = ROOT / 'build/joint_grace_native/900451015dcecef6'
    source = json.loads((base / 'build.json').read_text())
    assert digest(base / 'src/analyzer.cpp') == source['cpp_sha256']
    assert digest(base / 'src/analyzer.hpp') == source['hpp_sha256']
    current_cpp = git('show', 'HEAD:src/analyzer.cpp')
    assert current_cpp == (ROOT / 'build/routing_consensus_rollout/682b938120772cd4/src/analyzer.cpp').read_text()
    inputs = dict(base_sha256=digest(base / 'build.json'), script_sha256=digest(Path(__file__)),
                  assets={p: digest(ROOT / p) for p in ('src/joint_grace_body.hpp', 'tests/joint_body_pair.cpp')},
                  training_rule='Pre-existing stable-body: best Keyboard score plus .01 ownership; no profile, stability>=.75, onset<=.1, decay<=.15',
                  frozen_joint_floors=[.8, .3], source_tree=git('rev-parse', 'HEAD:src').strip())
    directory = ROOT / 'build/joint_body_native' / hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'build.json'
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text())
        assert state['inputs'] == inputs and digest(directory / 'pair') == state['binary_sha256']
    else:
        shutil.copytree(base / 'src', directory / 'src', dirs_exist_ok=True)
        shutil.copy2(ROOT / 'src/joint_grace_body.hpp', directory / 'src/joint_grace_body.hpp')
        cpp = (directory / 'src/analyzer.cpp').read_text().replace('experimental_joint_grace', 'experimental_joint_body')
        header = (directory / 'src/analyzer.hpp').read_text().replace('experimental_joint_grace', 'experimental_joint_body')
        cpp = cpp.replace('#include "joint_grace_restore.hpp"', '#include "joint_grace_restore.hpp"\n#include "joint_grace_body.hpp"', 1)
        anchor = 'tracking.confirmed && tracking.consecutive_hits >= 3 && joint_grace_history_.preceded(i);'
        assert cpp.count(anchor) == 1
        cpp = cpp.replace(anchor, 'tracking.confirmed && tracking.consecutive_hits >= 3 && joint_grace_history_.preceded(i) &&\n'
                          '\t\t\t\tjoint::stable_body(snapshot.full_mix_debug_candidates.data(),\n'
                          '\t\t\t\t\tstd::min(snapshot.full_mix_debug_candidate_count, snapshot.full_mix_debug_candidates.size()), static_cast<int>(i) + kFirstMidi);', 1)
        (directory / 'src/analyzer.cpp').write_text(cpp)
        (directory / 'src/analyzer.hpp').write_text(header)
        for name in ('note_grid_comparison.hpp', 'non_tempo_snapshot.hpp'):
            shutil.copy2(base / name, directory / name)
        shutil.copy2(ROOT / 'tests/joint_body_pair.cpp', directory / 'pair.cpp')
        sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
        assert len(sdk) == 1
        include = ['-I' + str(directory / 'src'), '-I' + str(sdk[0].parent), '-I' + str(ROOT / 'build/routing_duration_primary/02001c66f49dc729/third_party/beat_and_tempo_tracking')]
        objects = [ROOT / p for p in source['inputs']['observer']['inputs']['objects']]
        assert all(digest(ROOT / p) == h for p, h in source['inputs']['observer']['inputs']['objects'].items())
        subprocess.run(['g++', '-O2', '-std=c++17', *include, '-c', str(directory / 'src/analyzer.cpp'), '-o', str(directory / 'analyzer.o')], check=True)
        subprocess.run(['g++', '-O2', '-std=c++17', *include, '-I' + str(directory), str(directory / 'pair.cpp'),
                        str(directory / 'analyzer.o'), *map(str, objects), '-lm', '-pthread', '-ldl', '-o', str(directory / 'pair')], check=True)
        state = dict(inputs=inputs, binary_sha256=digest(directory / 'pair'), cpp_sha256=digest(directory / 'src/analyzer.cpp'),
                     hpp_sha256=digest(directory / 'src/analyzer.hpp'), observer_instrumentation=True)
        atomic_json(checkpoint, state)
    atomic_json(directory.parent / 'current.json', dict(build=str(checkpoint.relative_to(ROOT)), sha256=digest(checkpoint)))
    print(directory.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
