#!/usr/bin/env python3
"""Build a disabled-by-default release trial from a verified primary export."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest
from trace_keyboard_stages import build as build_observer


def main():
    identity()
    base, observed = build_observer()
    calibration_path = ROOT / 'build/joint_grace_calibration/83a1aabf4a68fee2/report.json'
    calibration = json.loads(calibration_path.read_text())
    assert calibration['passed'] and calibration['complete']
    dictionary_path = ROOT / 'build/joint_pitch/143d517357f2b5c2/dictionary.json'
    assets = ['src/joint_piano_fit.hpp', 'src/joint_grace_history.hpp', 'src/joint_grace_restore.hpp',
              'src/experimental_joint_grace_hook.inc', 'tests/joint_grace_pair.cpp', 'tests/note_grid_comparison.hpp',
              'tests/keyboard_stage_trace.hpp']
    inputs = dict(source_tree=git('rev-parse', 'HEAD:src').strip(), observer=observed,
                  calibration_sha256=digest(calibration_path), dictionary_sha256=digest(dictionary_path),
                  assets={p: digest(ROOT / p) for p in assets}, script_sha256=digest(Path(__file__)))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/joint_grace_native' / key
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'build.json'
    if checkpoint.exists():
        report = json.loads(checkpoint.read_text())
        assert report['inputs'] == inputs and digest(directory / 'pair') == report['binary_sha256']
    else:
        shutil.copytree(base / 'src', directory / 'src', dirs_exist_ok=True)
        for path in assets[:3]:
            shutil.copy2(ROOT / path, directory / 'src' / Path(path).name)
        cpp = (directory / 'src/analyzer.cpp').read_text()
        header = (directory / 'src/analyzer.hpp').read_text()
        header = header.replace('#include "routing_duplicate_consensus.hpp"', '#include "routing_duplicate_consensus.hpp"\n#include "joint_piano_fit.hpp"\n#include "joint_grace_history.hpp"', 1)
        anchor = '\tbool native_piano_duplicate_consensus = true;'
        assert header.count(anchor) == 1
        header = header.replace(anchor, anchor + '\n\tbool experimental_joint_grace = false;', 1)
        anchor = '\trouting::DuplicateConsensus<kNoteProbeCount * 2> routing_duplicate_consensus_;'
        assert header.count(anchor) == 1
        header = header.replace(anchor, anchor + '\n\tjoint::PianoFitter joint_grace_fitter_;\n\tbool joint_grace_fitter_ready_ = false;\n\tjoint::OriginalDisplayHistory<kNoteProbeCount> joint_grace_history_;', 1)
        cpp = cpp.replace('#include "analyzer.hpp"', '#include "analyzer.hpp"\n#include "joint_piano_dictionary.hpp"\n#include "joint_grace_restore.hpp"', 1)
        anchor = 'void AnalysisEngine::reset_analysis_state()\n{'
        assert cpp.count(anchor) == 1
        cpp = cpp.replace(anchor, anchor + '\n\tjoint_grace_history_.reset();', 1)
        anchor = '\tconst std::size_t usable = std::min(count, analysis_window_samples_);'
        assert cpp.count(anchor) == 1
        cpp = cpp.replace(anchor, anchor + '''
	const bool joint_grace_eligible = settings.experimental_joint_grace && input_mode == AnalysisInputMode::FullMix &&
		!settings.basic_pitch_vocal_fusion_enabled && (sample_rate_ == 16000 || sample_rate_ == 44100 || sample_rate_ == 48000) &&
		count == usable && usable == static_cast<std::size_t>(std::lround(sample_rate_ * .1)) &&
		std::abs(settings.analysis_interval_seconds - .05f) < 1e-6f;
	if (joint_grace_eligible) joint_grace_history_.begin(dropped_windows);
	else joint_grace_history_.reset();
	std::unique_ptr<NoteGrid> joint_before_other;''', 1)
        anchor = 'mao_stage_trace::state.start(snapshot.keyboard_notes);'
        assert cpp.count(anchor) == 1
        cpp = cpp.replace(anchor, 'if (joint_grace_eligible) ' + anchor, 1)
        anchor = '\t\tsuppress_other_dominant_same_pitch_keyboard_shadows(snapshot.keyboard_notes,'
        assert cpp.count(anchor) == 1
        cpp = cpp.replace(anchor, '\t\tif (joint_grace_eligible) joint_before_other = std::make_unique<NoteGrid>(snapshot.keyboard_notes);\n' + anchor, 1)
        begin = cpp.index('AnalysisSnapshot AnalysisEngine::analyze(')
        opening = cpp.index('\n{', begin) + 2
        cpp = cpp[:opening] + '\n\tmao_stage_trace::state.started = false;\n\tmao_stage_trace::state.watched = nullptr;' + cpp[opening:]
        end = cpp.index('\n}', begin)
        body = cpp[begin:end]
        assert body.count('\n\treturn snapshot;') == 1
        cpp = cpp[:begin] + body.replace('\n\treturn snapshot;', '\n' + (ROOT / 'src/experimental_joint_grace_hook.inc').read_text() + '\n\treturn snapshot;', 1) + cpp[end:]
        (directory / 'src/analyzer.cpp').write_text(cpp)
        (directory / 'src/analyzer.hpp').write_text(header)
        columns = json.loads(dictionary_path.read_text())['columns']
        values = ',\n'.join(','.join(format(v, '.17g') for v in column) for column in columns)
        (directory / 'src/joint_piano_dictionary.hpp').write_text('#pragma once\n#include <array>\nnamespace mao::joint { inline constexpr std::array<double,180312> kDictionary = {' + values + '}; }\n')
        for name in ('note_grid_comparison.hpp', 'joint_grace_pair.cpp'):
            shutil.copy2(ROOT / 'tests' / name, directory / name)
        shutil.copy2(ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38/non_tempo_snapshot.hpp', directory / 'non_tempo_snapshot.hpp')
        sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
        assert len(sdk) == 1
        include = ['-I' + str(directory / 'src'), '-I' + str(sdk[0].parent), '-I' + str(ROOT / 'build/routing_duration_primary/02001c66f49dc729/third_party/beat_and_tempo_tracking')]
        objects = [ROOT / p for p in observed['inputs']['objects']]
        subprocess.run(['g++', '-O2', '-std=c++17', *include, '-c', str(directory / 'src/analyzer.cpp'), '-o', str(directory / 'analyzer.o')], check=True)
        subprocess.run(['g++', '-O2', '-std=c++17', *include, '-I' + str(directory), str(directory / 'joint_grace_pair.cpp'),
                        str(directory / 'analyzer.o'), *map(str, objects), '-lm', '-pthread', '-ldl', '-o', str(directory / 'pair')], check=True)
        report = dict(inputs=inputs, binary_sha256=digest(directory / 'pair'), cpp_sha256=digest(directory / 'src/analyzer.cpp'),
                      hpp_sha256=digest(directory / 'src/analyzer.hpp'), observer_instrumentation=True,
                      scope='Isolated native trial only. Full observer provenance is retained for quality parity, not a production-ready integration.')
        atomic_json(checkpoint, report)
    atomic_json(directory.parent / 'current.json', dict(build=str(checkpoint.relative_to(ROOT)), sha256=digest(checkpoint)))
    print(directory.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
