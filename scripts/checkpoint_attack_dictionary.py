#!/usr/bin/env python3
"""Verify the first-hit studies, learned artifacts and unchanged safety failures."""
import argparse
import ast
import json
import subprocess
from pathlib import Path
import numpy as np
from evaluate_keyboard_confirmation import score_acceptances
from joint_pitch_reference import fit
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,digest
from screen_piano_attack_rises import rising
from transfer_real_piano_dictionary import observations

PATHS=['make/routing_duration.mk','make/keyboard_attack.mk','docs/routing_duration_goal.md',
       'scripts/screen_piano_context_attacks.py','scripts/supervised_piano_dictionary.py',
       'scripts/screen_supervised_piano_attacks.py','scripts/transfer_real_piano_dictionary.py',
       'scripts/screen_piano_attack_rises.py','scripts/checkpoint_attack_dictionary.py',
       'tests/test_supervised_piano_dictionary.py','tests/test_real_piano_dictionary.py','tests/test_piano_attack_rises.py']


def read(path):
    return json.loads(path.read_text())


def signatures(values):
    assert all(digest(ROOT/p)==h for p,h in values.items())


def check_admissions(name,accepted,metrics,timing,audit,context_style=False):
    cases={(c['end_sample'],c['midi']):c for c in audit['recordings'][name]['cases']}
    selected=[cases[c['end_sample'],c['midi']] for c in accepted]
    assert len(selected)==len({(c['end_sample'],c['midi']) for c in accepted})
    cells='accepted' if context_style else 'cells'
    held='held_recovery_seconds' if context_style else 'held_seconds'
    unsupported='unsupported_added_seconds' if context_style else 'unsupported_seconds'
    assert metrics[cells]==len(selected)
    assert abs(metrics[held]-sum(c['held_seconds'] for c in selected))<1e-8
    assert abs(metrics[unsupported]-sum(c['unsupported_seconds'] for c in selected))<1e-8
    assert score_acceptances(name,accepted)==timing


def verify():
    identity()
    audit=read(ROOT/'build/keyboard_confirmation_audit.json')
    signatures(audit['inputs'])
    for prefix,cells,unsupported in (('piano_context',8,.15),('piano_context_joint',1,0.),('piano_context_empirical_joint',31,.20)):
        path=ROOT/'build'/(prefix+'_attack_screen')/'report.json'
        report=read(path)
        signatures(report['inputs'])
        assert sum(r['metrics']['accepted'] for r in report['recordings'].values())==cells
        assert abs(sum(r['metrics']['unsupported_added_seconds'] for r in report['recordings'].values())-unsupported)<1e-8
        for name,row in report['recordings'].items():
            check_admissions(name,row['accepted'],row['metrics'],row['timing'],audit,True)
    cross_path=ROOT/'build/supervised_piano_attack_screen/a5e51624f9ac2c67/report.json'
    cross=read(cross_path)
    assert cross['complete'] and cross['decision']=='reject'
    signatures(cross['protocol']['inputs'])
    for name,fold in cross['folds'].items():
        assert fold['frozen']['fitting_recordings']==sorted(set(cross['folds'])-{name})
        assert digest(cross_path.parent/(name+'-dictionary.npz'))==fold['frozen']['dictionary_sha256']
        assert read(cross_path.parent/(name+'-frozen.json'))==fold['frozen']
        check_admissions(name,fold['accepted'],fold['metrics'],fold['timing'],audit)
    assert abs(sum(f['metrics']['unsupported_seconds'] for f in cross['folds'].values())-.1)<1e-8
    parent=ROOT/'build/real_piano_dictionary_transfer/cfb32e5534dc943f'
    plan=read(parent/'plan.json')
    report=read(parent/'report.json')
    signatures(plan['inputs'])
    assert report['complete'] and report['decision']=='reject_for_recovery'
    assert report['plan_sha256']==digest(parent/'plan.json')
    assert [s['id'] for s in plan['selection']]==['fit-'+str(i) for i in range(25,45)]
    frames=labelled=0
    active=np.zeros(88,dtype=bool)
    for sample in plan['selection']:
        signatures({sample['audio']:sample['audio_sha256'],sample['midi']:sample['midi_sha256']})
        path=parent/(sample['id']+'.npz')
        row=report['recordings'][sample['id']]
        assert digest(path)==row['sha256']
        data=np.load(path)
        assert data['observed'].shape==(2049,row['frames']) and data['mask'].shape==(88,row['frames'])
        assert data['mask'].dtype.kind=='b' and np.isfinite(data['observed']).all() and (data['observed']>=0).all()
        frames+=row['frames'];labelled+=int(data['mask'].any(axis=0).sum())
        active|=data['mask'].any(axis=1)
    assert frames==12000 and labelled==11666
    model_path=parent/'dictionary.npz'
    assert digest(model_path)==report['dictionary_sha256']==read(parent/'frozen.json')['dictionary_sha256']
    matrix=np.load(model_path)['dictionary']
    assert matrix.shape==(2049,88) and np.isfinite(matrix).all() and (matrix>=0).all()
    np.testing.assert_allclose(np.linalg.norm(matrix,axis=0),1.,atol=1e-12)
    prior=np.array(read(ROOT/'build/joint_pitch/143d517357f2b5c2/dictionary.json')['columns']).T
    np.testing.assert_array_equal(matrix[:,~active],prior[:,~active])
    rise=read(ROOT/'build/piano_attack_rise_screen/report.json')
    signatures(rise['inputs'])
    assert rise['decision']=='reject' and rise['attack_gain']==6
    baseline_path=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267/report.json'
    baseline=read(baseline_path)
    context=read(ROOT/'build/piano_context_empirical_joint_attack_screen/report.json')
    total_gain=0
    for name,row in report['results'].items():
        check_admissions(name,row['accepted'],row['metrics'],row['timing'],audit)
        total_gain+=row['timing']['matched_attacks']['after']-row['timing']['matched_attacks']['before']
        raw=baseline_path.parent/(name+'.f32')
        assert digest(raw)==baseline['recordings'][name]['prefix_sha256']
        rate=baseline['recordings'][name]['rate']
        x=observations(np.fromfile(raw,dtype='<f4').astype(float),rate)
        activation=fit(matrix,x)
        projection=matrix.T@x
        relative=activation/np.maximum(activation.max(axis=0),1e-12)
        explained=activation/np.maximum(projection,1e-12)
        probabilities={(p['end_sample'],p['midi']):p['probability'] for p in context['recordings'][name]['probabilities']}
        expected=set()
        for case in audit['recordings'][name]['cases']:
            endpoint,midi=case['end_sample'],case['midi']
            index=endpoint//round(rate*.05)-1
            if probabilities.get((endpoint,midi),0.)>=context['threshold'] and relative[midi-21,index]>=.8 and explained[midi-21,index]>=.3:
                expected.add((endpoint,midi))
        assert expected=={(c['end_sample'],c['midi']) for c in row['accepted']}
        rising_expected={(e,m) for e,m in expected if rising(activation,e//round(rate*.05)-1,m)}
        r=rise['results'][name]
        assert rising_expected=={(c['end_sample'],c['midi']) for c in r['accepted']}
        check_admissions(name,r['accepted'],r['metrics'],r['timing'],audit)
    assert total_gain==9
    assert abs(sum(r['metrics']['unsupported_seconds'] for r in report['results'].values())-.3)<1e-8
    assert abs(sum(r['metrics']['unsupported_seconds'] for r in rise['results'].values())-.15)<1e-8
    assert 'kLookaheadFrames = 22;' in git('show','HEAD:src/basic_pitch_onnx_decoder.hpp')
    assert 'kSnapshotStride = kTargetSampleRate / 2;' in git('show','HEAD:src/basic_pitch_pcm_history.hpp')
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    for target in ('test-supervised-piano-dictionary','test-real-piano-dictionary','test-piano-attack-rises','test-joint-note-coverage','test-routing-duration-score'):
        subprocess.run(['make',target],cwd=ROOT,check=True)
    print('Verified frozen family/pitch comparisons, three dictionary folds and twenty-recording transfer; unsafe additions remain, no runtime promotion',flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',action='store_true')
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    verify()
    if not(args.stage or args.publish):
        return
    _,remote,primary,tip=identity()
    assert git('rev-parse','HEAD').strip()==tip
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS)
    git('add','--',*PATHS)
    git('diff','--cached','--check')
    (ROOT/'build/attack_dictionary_staged.diff').write_text(git('diff','--cached'))
    print(git('diff','--cached','--stat'),flush=True)
    if args.stage:
        return
    print(git('commit','-m','Evaluate first-hit piano cues and supervised dictionary transfer without promoting unsafe additions'),flush=True)
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
