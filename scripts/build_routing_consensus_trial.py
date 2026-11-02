#!/usr/bin/env python3
"""Build corroborated native routing against primary without touching dirty sources."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest

ASSETS = ['src/routing_duplicate_consensus.hpp', 'src/native_piano_consensus_cached_hook.inc',
          'src/piano_guitar_features.hpp', 'src/piano_guitar_verifier.hpp', 'src/piano_guitar_model_data.hpp',
          'src/native_timbre_features.hpp', 'tests/routing_consensus_pair.cpp']


def candidate_sources(cpp, header):
    if 'native_piano_duplicate_consensus' in header:
        assert (ROOT / 'src/native_piano_consensus_cached_hook.inc').read_text() in cpp
        assert 'routing_duplicate_consensus_.begin_frame(dropped_windows);' in cpp
        assert 'timbre::CepstralExtractor routing_cepstra_;' in header
        return cpp, header
    anchor = '\tbool experimental_piano_guitar_filter = false;'
    assert header.count(anchor) == 1
    header = header.replace(anchor, anchor + '\n\tbool native_piano_duplicate_consensus = false;', 1)
    anchor = '#include "basic_pitch_pcm_history.hpp"'
    assert header.count(anchor) == 1
    header = header.replace(anchor, anchor + '\n#include "routing_duplicate_consensus.hpp"\n#include "native_timbre_features.hpp"', 1)
    anchor = 'private:\n\tstruct Probe {'
    assert header.count(anchor) == 1
    header = header.replace(anchor, 'private:\n\trouting::DuplicateConsensus<kNoteProbeCount * 2> routing_duplicate_consensus_;\n\ttimbre::CepstralExtractor routing_cepstra_;\n\tstruct Probe {', 1)
    anchor = 'void AnalysisEngine::reset_analysis_state()\n{'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, anchor + '\n\trouting_duplicate_consensus_.reset();', 1)
    anchor = '\tcopy_text(snapshot.source, sizeof(snapshot.source), resolved_source_name);'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, '\trouting_duplicate_consensus_.begin_frame(dropped_windows);\n' + anchor, 1)
    anchor = '\n\t// Keep the expensive high-tempo hypothesis outside the phase path.'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, '\n' + (ROOT / 'src/native_piano_consensus_cached_hook.inc').read_text() + anchor, 1)
    return cpp, header


def main():
    identity()
    baseline = ROOT / 'build/routing_duration_primary/02001c66f49dc729'
    objects = [baseline / (name + '.o') for name in ('BTT', 'DFT', 'Filter', 'STFT', 'Statistics', 'fastsin',
               'basic_pitch_onnx_worker', 'basic_pitch_onnx_runtime', 'basic_pitch_onnx_decoder', 'basic_pitch_pcm_history')]
    sdk = list((ROOT / 'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk) == 1
    original_cpp, original_header = (git('show', 'HEAD:src/analyzer.' + suffix) for suffix in ('cpp', 'hpp'))
    inputs = dict(primary_cpp_sha256=hashlib.sha256(original_cpp.encode()).hexdigest(),
                  primary_hpp_sha256=hashlib.sha256(original_header.encode()).hexdigest(),
                  source_tree=git('rev-parse', 'HEAD:src').strip(), assets={p: digest(ROOT / p) for p in ASSETS},
                  objects={str(p.relative_to(ROOT)): digest(p) for p in objects}, script_sha256=digest(Path(__file__)),
                  comparison_sha256=digest(ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38/non_tempo_snapshot.hpp'),
                  compiler=subprocess.run(['g++', '--version'], text=True, capture_output=True, check=True).stdout.splitlines()[0],
                  sdk_headers={p.name: digest(p) for p in sorted(sdk[0].parent.glob('*.h'))})
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    directory = ROOT / 'build/routing_consensus_trial' / key
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / 'build.json'
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text())
        assert state['inputs'] == inputs and digest(directory / 'pair') == state['binary_sha256']
    else:
        archive = subprocess.run(['git', 'archive', 'HEAD', 'src'], cwd=ROOT, capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(directory, filter='data')
        cpp, header = candidate_sources(original_cpp, original_header)
        (directory / 'src/analyzer.cpp').write_text(cpp)
        (directory / 'src/analyzer.hpp').write_text(header)
        for path in ASSETS:
            if path.startswith('src/'):
                (directory / path).write_bytes((ROOT / path).read_bytes())
        (directory / 'pair.cpp').write_bytes((ROOT / 'tests/routing_consensus_pair.cpp').read_bytes())
        (directory / 'non_tempo_snapshot.hpp').write_bytes((ROOT / 'build/piano_guitar_trial/5423eaeda3f96b38/non_tempo_snapshot.hpp').read_bytes())
        subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(sdk[0].parent), '-I' + str(baseline / 'third_party/beat_and_tempo_tracking'),
                        '-c', str(directory / 'src/analyzer.cpp'), '-o', str(directory / 'analyzer.o')], check=True)
        subprocess.run(['g++', '-O2', '-std=c++17', '-I' + str(directory / 'src'), '-I' + str(directory),
                        str(directory / 'pair.cpp'), str(directory / 'analyzer.o'), *map(str, objects),
                        '-lm', '-pthread', '-ldl', '-o', str(directory / 'pair')], check=True)
        state = dict(inputs=inputs, cpp_sha256=digest(directory / 'src/analyzer.cpp'), hpp_sha256=digest(directory / 'src/analyzer.hpp'),
                     binary_sha256=digest(directory / 'pair'))
        atomic_json(checkpoint, state)
    assert all(digest(ROOT / path) == checksum for path, checksum in inputs['assets'].items())
    atomic_json(directory.parent / 'current.json', dict(build=str(checkpoint.relative_to(ROOT)), sha256=digest(checkpoint)))
    print(directory.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
