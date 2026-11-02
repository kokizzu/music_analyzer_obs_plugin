#!/usr/bin/env python3
"""Native display continuity with frozen causal seed/sustain evidence."""
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
    base=ROOT/'build/pitch_attack_display_native/381fe8745f049c1b'
    previous=read(base/'build.json')
    assert digest(base/'pair')==previous['binary_sha256']
    assert digest(base/'src/analyzer.cpp')==previous['cpp_sha256']
    assert digest(base/'src/analyzer.hpp')==previous['hpp_sha256']
    source_support=ROOT/'build/pitch_attack_continuity_screen/native-support.json'
    support=read(source_support)
    assert all(digest(ROOT/p)==h for p,h in support['inputs'].items())
    assets=['src/piano_attack_continuity.hpp','tests/piano_attack_continuity.cpp','scripts/replay_pitch_attack_continuity.py']
    inputs=dict(base_build_sha256=digest(base/'build.json'),source_tree=git('rev-parse','HEAD:src').strip(),
        assets={p:digest(ROOT/p) for p in assets},support_sha256=digest(source_support),
        hypothesis='Strict first-hit seed, at most three 50 ms display hops, continuing current spectral/neural support, no analytical mutation or visible-row eviction')
    directory=ROOT/'build/pitch_attack_continuity_native'/hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    directory.mkdir(parents=True,exist_ok=True)
    checkpoint=directory/'build.json'
    if not checkpoint.exists():
        shutil.copytree(base/'src',directory/'src',dirs_exist_ok=True)
        shutil.copy2(ROOT/'src/piano_attack_continuity.hpp',directory/'src/piano_attack_continuity.hpp')
        old='experimental_pitch_attack_display_replay';flag='experimental_pitch_attack_continuity_replay'
        header=(base/'src/analyzer.hpp').read_text().replace(old,flag)
        assert header.count('namespace mao {')==1
        header=header.replace('namespace mao {','namespace mao::joint { class AttackDisplayContinuity; }\nnamespace mao {',1)
        member='\trouting::DuplicateConsensus<kNoteProbeCount * 2> routing_duplicate_consensus_;'
        assert header.count(member)==1
        header=header.replace(member,member+'\n\tstd::unique_ptr<joint::AttackDisplayContinuity> attack_display_continuity_;',1)
        cpp=(base/'src/analyzer.cpp').read_text().replace(old,flag).replace('#include "piano_attack_display.hpp"','#include "piano_attack_continuity.hpp"',1)
        reset='void AnalysisEngine::reset_analysis_state()\n{'
        assert cpp.count(reset)==1
        cpp=cpp.replace(reset,reset+'\n\tif (attack_display_continuity_) attack_display_continuity_->reset();',1)
        begin=cpp.index('    if (settings.'+flag+' && replay_attack_raw &&')
        end=cpp.index('\n\treturn snapshot;',begin)
        hook=cpp[begin:end]
        call='''        if (joint::recover_first_hit_display(snapshot.keyboard_notes,*replay_attack_raw,
                keyboard_note_tracking_,mao_attack_replay::supported))'''
        assert hook.count(call)==1
        hook=hook.replace(call,'''        if (!attack_display_continuity_) attack_display_continuity_=std::make_unique<joint::AttackDisplayContinuity>();
        if (attack_display_continuity_->apply(snapshot.keyboard_notes,*replay_attack_raw,
                keyboard_note_tracking_,mao_attack_replay::supported,mao_attack_replay::continuing))''',1)
        assert hook.endswith('    }\n')
        hook=hook[:-6]+'    } else if (attack_display_continuity_) attack_display_continuity_->reset();\n'
        cpp=cpp[:begin]+hook+cpp[end:]
        (directory/'src/analyzer.cpp').write_text(cpp)
        (directory/'src/analyzer.hpp').write_text(header)
        support_header=(base/'src/pitch_attack_replay_support.hpp').read_text()+'\nnamespace mao_attack_replay { inline std::array<bool,88> continuing{}; }\n'
        (directory/'src/pitch_attack_replay_support.hpp').write_text(support_header)
        for name in ('non_tempo_snapshot.hpp','note_grid_comparison.hpp'):
            shutil.copy2(base/name,directory/name)
        harness=(base/'pair.cpp').read_text().replace(old,flag)
        harness=harness.replace('std::map<std::size_t,std::array<bool,88>> support;',
            'struct SupportFrame { std::array<bool,88> seed{},continuing{}; };\n    std::map<std::size_t,SupportFrame> support;',1)
        harness=harness.replace('std::size_t endpoint; int midi;','std::size_t endpoint; int midi,seed,continuing;',1)
        harness=harness.replace('!(row>>endpoint>>midi) || endpoint<previous || midi<21 || midi>108',
            '!(row>>endpoint>>midi>>seed>>continuing) || endpoint<previous || midi<21 || midi>108 || seed<0 || seed>1 || continuing<0 || continuing>1',1)
        harness=harness.replace('support[endpoint][midi-21]=true; previous=endpoint;',
            'support[endpoint].seed[midi-21]=seed; support[endpoint].continuing[midi-21]=continuing; previous=endpoint;',1)
        harness=harness.replace('mao_attack_replay::supported=support[end];',
            'mao_attack_replay::supported=support[end].seed; mao_attack_replay::continuing=support[end].continuing;',1)
        (directory/'pair.cpp').write_text(harness)
        objects=read(ROOT/'build/pitch_attack_envelope_native/9bf32267d49cc8fb/build.json')['inputs']['objects']
        assert all(digest(ROOT/p)==h for p,h in objects.items())
        include=['-I'+str(directory/'src'),'-I'+str(directory),'-I'+str(ROOT/'build/onnxruntime-linux-x64-1.29.0/include'),
                 '-I'+str(ROOT/'build/routing_duration_primary/02001c66f49dc729/third_party/beat_and_tempo_tracking')]
        subprocess.run(['g++','-O2','-std=c++17',*include,str(ROOT/'tests/piano_attack_continuity.cpp'),'-o',str(directory/'test')],check=True)
        subprocess.run([str(directory/'test')],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,'-c',str(directory/'src/analyzer.cpp'),'-o',str(directory/'analyzer.o')],check=True)
        subprocess.run(['g++','-O2','-std=c++17',*include,str(directory/'pair.cpp'),str(directory/'analyzer.o'),*[str(ROOT/p) for p in objects],
                        '-lm','-pthread','-ldl','-o',str(directory/'pair')],check=True)
        atomic_json(checkpoint,dict(inputs=inputs,binary_sha256=digest(directory/'pair'),cpp_sha256=digest(directory/'src/analyzer.cpp'),
            hpp_sha256=digest(directory/'src/analyzer.hpp'),test_passed=True))
    built=read(checkpoint)
    assert built['inputs']==inputs and built['test_passed'] and digest(directory/'pair')==built['binary_sha256']
    return directory,source_support,support


def main():
    directory,source_support,support=build()
    prepared=support['recordings']
    for row in prepared.values():
        assert digest(ROOT/row['path'])==row['sha256']
    shutil.copy2(source_support,directory/'evidence.json')
    atomic_json(directory/'plan.json',dict(build=str((directory/'build.json').relative_to(ROOT)),build_sha256=digest(directory/'build.json'),
        evidence_sha256=digest(directory/'evidence.json'),recordings=prepared,
        scope='Native bounded display continuity, frozen audio-only captured evidence, no live worker/hardware latency qualification.'))
    for name,row in prepared.items():
        subprocess.run([str(directory/'pair'),str(ROOT/row['raw']),str(row['rate']),str(directory/(name+'.tsv')),str(ROOT/row['path'])],check=True,timeout=3600)
        print(name,'native continuity replay complete',flush=True)
    replay=directory/'replay.json'
    atomic_json(replay,dict(plan_sha256=digest(directory/'plan.json'),complete=True,outputs={n:digest(directory/(n+'.tsv')) for n in prepared}))
    atomic_json(directory.parent/'current.json',dict(report=str(replay.relative_to(ROOT)),sha256=digest(replay)))
    print(directory.relative_to(ROOT),flush=True)


if __name__=='__main__':
    main()
