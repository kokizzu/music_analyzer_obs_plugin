#!/usr/bin/env python3
"""Build a disabled multiwindow candidate from verified primary source blobs."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
from low_keyboard_coherence_trial import candidate_sources
from publish_next_detection import git, identity
from routing_duration_baseline import ROOT, atomic_json, digest


def translate(text):
    return text.replace('low_keyboard_coherence.hpp','multiscale_low_keyboard.hpp').replace('LowKeyboardCoherence','MultiScaleLowKeyboard').replace('experimental_low_keyboard_coherence','experimental_multiscale_low_keyboard')


def main():
    identity()
    base=ROOT/'build/routing_duration_primary/02001c66f49dc729'
    assets=['src/multiscale_low_keyboard.hpp','scripts/low_keyboard_coherence_trial.py','tests/low_keyboard_coherence.cpp',
            'tests/low_keyboard_coherence_history.cpp','tests/low_keyboard_coherence_pair.cpp','tests/note_grid_comparison.hpp',
            'tests/multiscale_low_keyboard.cpp','src/low_keyboard_coherence.hpp']
    objects=[base/(name+'.o') for name in ('BTT','DFT','Filter','STFT','Statistics','fastsin',
             'basic_pitch_onnx_worker','basic_pitch_onnx_runtime','basic_pitch_onnx_decoder','basic_pitch_pcm_history')]
    sdk=list((ROOT/'build').glob('onnxruntime-*/include/onnxruntime_c_api.h'))
    assert len(sdk)==1
    inputs=dict(source_tree=git('rev-parse','HEAD:src').strip(),assets={p:digest(ROOT/p) for p in assets},
        script_sha256=digest(Path(__file__)),objects={str(p.relative_to(ROOT)):digest(p) for p in objects},
        compiler=subprocess.run(['g++','--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0],
        sdk_headers={p.name:digest(p) for p in sorted(sdk[0].parent.glob('*.h'))},
        comparison_sha256=digest(ROOT/'build/piano_guitar_trial/5423eaeda3f96b38/non_tempo_snapshot.hpp'))
    directory=ROOT/'build/multiscale_low_keyboard_native'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    checkpoint=directory/'build.json'
    if checkpoint.exists():
        state=json.loads(checkpoint.read_text())
        assert state['inputs']==inputs and digest(directory/'pair')==state['binary_sha256']
    else:
        archive=subprocess.run(['git','archive','HEAD','src'],cwd=ROOT,capture_output=True,check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(directory,filter='data')
        cpp,header=candidate_sources(git('show','HEAD:src/analyzer.cpp'),git('show','HEAD:src/analyzer.hpp'))
        (directory/'src/analyzer.cpp').write_text(translate(cpp))
        (directory/'src/analyzer.hpp').write_text(translate(header))
        (directory/'src/multiscale_low_keyboard.hpp').write_bytes((ROOT/assets[0]).read_bytes())
        include=['-I'+str(directory/'src'),'-I'+str(sdk[0].parent),'-I'+str(base/'third_party/beat_and_tempo_tracking')]
        for name in ('low_keyboard_coherence','low_keyboard_coherence_history'):
            source=directory/(name+'.cpp')
            source.write_text(translate((ROOT/'tests'/(name+'.cpp')).read_text()))
            subprocess.run(['g++','-O2','-std=c++17',*include,str(source),'-o',str(directory/name)],check=True)
            subprocess.run([str(directory/name)],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,str(ROOT/'tests/multiscale_low_keyboard.cpp'),'-o',str(directory/'brief_note')],check=True)
        subprocess.run([str(directory/'brief_note')],check=True)
        (directory/'pair.cpp').write_text(translate((ROOT/'tests/low_keyboard_coherence_pair.cpp').read_text()))
        (directory/'note_grid_comparison.hpp').write_bytes((ROOT/'tests/note_grid_comparison.hpp').read_bytes())
        (directory/'non_tempo_snapshot.hpp').write_bytes((ROOT/'build/piano_guitar_trial/5423eaeda3f96b38/non_tempo_snapshot.hpp').read_bytes())
        subprocess.run(['g++','-O2','-std=c++17',*include,'-c',str(directory/'src/analyzer.cpp'),'-o',str(directory/'analyzer.o')],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,'-I'+str(directory),str(directory/'pair.cpp'),str(directory/'analyzer.o'),
                        *map(str,objects),'-lm','-pthread','-ldl','-o',str(directory/'pair')],check=True)
        state=dict(inputs=inputs,binary_sha256=digest(directory/'pair'),cpp_sha256=digest(directory/'src/analyzer.cpp'),
                   hpp_sha256=digest(directory/'src/analyzer.hpp'),regression_passed=True)
        atomic_json(checkpoint,state)
    atomic_json(directory.parent/'current.json',dict(build=str(checkpoint.relative_to(ROOT)),sha256=digest(checkpoint)))
    print(directory.relative_to(ROOT),flush=True)


if __name__=='__main__':
    main()
