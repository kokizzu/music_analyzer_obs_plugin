#!/usr/bin/env python3
"""Isolated native display-only replay, sharing the frozen audio support."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,atomic_json,digest


def read(path):
    return json.loads(path.read_text())


def build():
    identity()
    base=ROOT/'build/pitch_attack_envelope_native/9bf32267d49cc8fb'
    previous=read(base/'build.json')
    assert digest(base/'pair')==previous['binary_sha256']
    assert digest(base/'src/analyzer.cpp')==previous['cpp_sha256']
    assert digest(base/'src/analyzer.hpp')==previous['hpp_sha256']
    cpp=(base/'src/analyzer.cpp').read_text()
    cpp=cpp.removeprefix('#include "pitch_attack_replay_support.hpp"\n')
    first=cpp.index('\n        std::array<float,kNoteProbeCount> replay_attack_floors;')
    anchor='\t\tsmooth_note_grid_envelope(snapshot.keyboard_notes, snapshot.keyboard, keyboard_note_tracking_, -1,'
    last=cpp.index(anchor,first)
    cpp=cpp[:first]+cpp[last:]
    assert cpp.count(', &replay_attack_floors)')==1
    cpp=cpp.replace(', &replay_attack_floors)',')',1)
    header=(base/'src/analyzer.hpp').read_text().replace('\n\tbool experimental_pitch_attack_replay = false;','',1)
    # Recover and verify the exact primary inputs before building the new trial.
    assert cpp==git('show','HEAD:src/analyzer.cpp')
    assert header==git('show','HEAD:src/analyzer.hpp')
    assets=['src/piano_attack_display.hpp','tests/piano_attack_display.cpp','scripts/replay_pitch_attack_display.py']
    inputs=dict(base_build_sha256=digest(base/'build.json'),source_tree=git('rev-parse','HEAD:src').strip(),
        assets={p:digest(ROOT/p) for p in assets},evidence_sha256=digest(base/'evidence.json'),
        hypothesis='Recover only current first-hit raw notes after final analytical processing, with no occupied-row eviction or tracking mutation')
    directory=ROOT/'build/pitch_attack_display_native'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    checkpoint=directory/'build.json'
    if not checkpoint.exists():
        shutil.copytree(base/'src',directory/'src',dirs_exist_ok=True)
        shutil.copy2(ROOT/'src/piano_attack_display.hpp',directory/'src/piano_attack_display.hpp')
        flag='experimental_pitch_attack_display_replay'
        setting='\tbool native_piano_duplicate_consensus = true;'
        assert header.count(setting)==1
        header=header.replace(setting,setting+'\n\tbool '+flag+' = false;',1)
        cpp='#include "piano_attack_display.hpp"\n#include "pitch_attack_replay_support.hpp"\n'+cpp
        start=cpp.index('AnalysisSnapshot AnalysisEngine::analyze(')
        opening=cpp.index('\n{',start)+2
        cpp=cpp[:opening]+'\n\tstd::unique_ptr<NoteGrid> replay_attack_raw;'+cpp[opening:]
        cpp=cpp.replace(anchor,'\t\tif (settings.'+flag+') replay_attack_raw=std::make_unique<NoteGrid>(snapshot.keyboard_notes);\n'+anchor,1)
        end=cpp.index('\n}',start)
        body=cpp[start:end]
        assert body.count('\n\treturn snapshot;')==1
        hook='''
    if (settings.experimental_pitch_attack_display_replay && replay_attack_raw &&
        input_mode==AnalysisInputMode::FullMix && !settings.basic_pitch_vocal_fusion_enabled &&
        count==usable && usable==static_cast<std::size_t>(std::lround(sample_rate_*.1)) &&
        std::abs(settings.analysis_interval_seconds-.05f)<1e-6f && dropped_windows==0 &&
        (sample_rate_==16000 || sample_rate_==44100 || sample_rate_==48000)) {
        if (joint::recover_first_hit_display(snapshot.keyboard_notes,*replay_attack_raw,
                keyboard_note_tracking_,mao_attack_replay::supported))
            write_note_grid_label(snapshot.keyboard,snapshot.keyboard_notes,-1);
    }
'''
        cpp=cpp[:start]+body.replace('\n\treturn snapshot;',hook+'\n\treturn snapshot;',1)+cpp[end:]
        (directory/'src/analyzer.cpp').write_text(cpp)
        (directory/'src/analyzer.hpp').write_text(header)
        for name in ('pair.cpp','non_tempo_snapshot.hpp','note_grid_comparison.hpp'):
            text=(base/name).read_text().replace('experimental_pitch_attack_replay',flag)
            (directory/name).write_text(text)
        objects=[ROOT/p for p in previous['inputs']['objects']]
        assert all(digest(ROOT/p)==h for p,h in previous['inputs']['objects'].items())
        include=['-I'+str(directory/'src'),'-I'+str(directory),'-I'+str(ROOT/'build/onnxruntime-linux-x64-1.29.0/include'),
                 '-I'+str(ROOT/'build/routing_duration_primary/02001c66f49dc729/third_party/beat_and_tempo_tracking')]
        test=directory/'test-display'
        subprocess.run(['g++','-O2','-std=c++17',*include,str(ROOT/'tests/piano_attack_display.cpp'),'-o',str(test)],check=True)
        subprocess.run([str(test)],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,'-c',str(directory/'src/analyzer.cpp'),'-o',str(directory/'analyzer.o')],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,str(directory/'pair.cpp'),str(directory/'analyzer.o'),*map(str,objects),
                        '-lm','-pthread','-ldl','-o',str(directory/'pair')],check=True)
        atomic_json(checkpoint,dict(inputs=inputs,binary_sha256=digest(directory/'pair'),cpp_sha256=digest(directory/'src/analyzer.cpp'),
            hpp_sha256=digest(directory/'src/analyzer.hpp'),test_passed=True))
    built=read(checkpoint)
    assert built['inputs']==inputs and built['test_passed'] and digest(directory/'pair')==built['binary_sha256']
    return directory,base


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--build',action='store_true')
    args=parser.parse_args()
    directory,base=build()
    if args.build:
        print(directory.relative_to(ROOT),flush=True)
        return
    evidence=read(base/'evidence.json')
    assert all(digest(ROOT/p)==h for p,h in evidence['inputs'].items())
    prepared=evidence['recordings']
    for name,row in prepared.items():
        assert digest(ROOT/row['path'])==row['sha256']
    shutil.copy2(base/'evidence.json',directory/'evidence.json')
    atomic_json(directory/'plan.json',dict(build=str((directory/'build.json').relative_to(ROOT)),build_sha256=digest(directory/'build.json'),
        evidence_sha256=digest(directory/'evidence.json'),recordings=prepared,
        scope='Display-only native feasibility replay using the frozen audio support; no live worker or hardware latency claim.'))
    for name,row in prepared.items():
        subprocess.run([str(directory/'pair'),str(ROOT/row['raw']),str(row['rate']),str(directory/(name+'.tsv')),str(ROOT/row['path'])],check=True,timeout=3600)
        print(name,'display paired replay complete',flush=True)
    replay=directory/'replay.json'
    atomic_json(replay,dict(plan_sha256=digest(directory/'plan.json'),complete=True,outputs={n:digest(directory/(n+'.tsv')) for n in prepared}))
    atomic_json(directory.parent/'current.json',dict(report=str(replay.relative_to(ROOT)),sha256=digest(replay)))
    print(directory.relative_to(ROOT),flush=True)


if __name__=='__main__':
    main()
