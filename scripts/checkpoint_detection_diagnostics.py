#!/usr/bin/env python3
"""Verify and publish only tested detection diagnostics; no runtime promotion."""
import argparse
import ast
import json
import subprocess
from detection_validation_store import Store
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,digest
from analyzer_diagnostic import verify_recovery_lineage
from source_recovery_patch import candidate_sources

PATHS=['make/pitch_continuity_controls.mk','docs/routing_duration_goal.md',
    'scripts/note_onset_score.py','tests/test_note_onset_score.py',
    'scripts/detection_validation_store.py','tests/test_detection_validation_store.py',
    'scripts/screen_routing_onset_proposals.py','scripts/analyzer_diagnostic.py','tests/test_analyzer_diagnostic.py',
    'scripts/benchmark_detection_worker.py','tests/detection_worker_latency.cpp','scripts/checkpoint_detection_diagnostics.py']
PATHS += ['scripts/source_recovery_patch.py','scripts/validate_source_recovery.py','tests/source_recovery.cpp',
    'tests/worker_context_epoch.cpp','scripts/checkpoint_pitch_controls.py']
PATHS += ['scripts/native_note_candidates.py','scripts/screen_native_note_candidates.py','tests/test_native_note_candidates.py',
    'scripts/pipeline_diagnostics.py','tests/test_pipeline_diagnostics.py','scripts/regression_recordings.py','tests/test_regression_recordings.py']
RUNTIME=['src/analyzer.cpp','src/analyzer.hpp','src/basic_pitch_onnx_worker.cpp','src/basic_pitch_onnx_worker.hpp']


def recovery():
    with Store() as store:
        result=evidence(store,'source-recovery')
        assert result['cases_passed']==7 and result['epoch_passed']
        assert sum(r['frames'] for r in result['ordinary'].values())==2400
        assert digest(ROOT/result['binary'])==result['binary_sha256']
        assert result['timing']['observed_results']==100 and result['timing']['unobserved_or_replaced']==0
        assert result['timing']['completion_p99_ms']<45 and result['timing']['completion_max_ms']<50
        sources=candidate_sources()
        assert all(store.get(h).decode()==sources[name] for name,h in result['source_payloads'].items())
    return result,sources


def evidence(store,key):
    row=store.connection.execute('select payload from evidence where id=?',(key,)).fetchone()
    assert row,key+' missing'
    value=json.loads(store.get(row[0]))
    assert all(digest(ROOT/p)==h for p,h in value['inputs'].items())
    return value


def verify():
    identity()
    for target in ('test-note-onset-score','test-detection-validation-store','test-analyzer-diagnostic',
        'test-native-note-candidates','test-pipeline-diagnostics','test-regression-recordings'):
        subprocess.run(['make',target],cwd=ROOT,check=True)
    for path in PATHS:
        if path.endswith('.py'):
            ast.parse((ROOT/path).read_text())
    with Store() as store:
        screen=evidence(store,'routing-onset-screen');worker=evidence(store,'worker-latency')
        native=evidence(store,'native-note-candidates');pipeline=evidence(store,'workspace-pipeline');regression=evidence(store,'regression-replay')
        assert native['repeat_decision']=='cancel_development' and native['uncertainty_decision']=='cancel_protected_row_loss'
        assert pipeline['passed_pipeline_budget'] and pipeline['controlled_stream_hop_gaps']==0 and pipeline['intentional_idle_hops']==9
        assert pipeline['physical_capture_latency_ms'] is None and pipeline['audio_dropped_windows'] is None
        assert regression['passed'] and len(regression['cases'])==3 and regression['unique_inputs']==2
        assert pipeline['source_tree']==regression['source_tree']==git('rev-parse','HEAD:src').strip()
        from regression_recordings import verify_files
        verify_files(store)
    assert set(screen['recordings'])=={'training-1','training-2','training-3'}
    assert screen['routing_decision']==screen['onset_decision']=='reject_development'
    assert screen['recordings']['training-3']['routing']['unsupported_seconds_delta']>0
    assert worker['submitted']==worker['observed_results']==100 and worker['unobserved_or_replaced']==0
    assert worker['passed_worker_budget'] and worker['completion_p99_ms']<45 and worker['completion_max_ms']<50 and worker['submit_p99_ms']<1
    subprocess.run(['make','verify-pitch-controls'],cwd=ROOT,check=True)
    verify_recovery_lineage()
    recovery()
    print('Verified: rejected admission proposals, source-recovery provenance, paced workspace pipeline and retained regression replay. No additional runtime promotion.',flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('verify','stage','publish','inspect'));args=parser.parse_args()
    if args.mode=='inspect':
        print(json.dumps(dict(head=git('rev-parse','HEAD').strip(),remote_tip=identity()[3])),flush=True)
        source=git('show','HEAD:src/standalone.cpp');lines=source.splitlines()
        for anchor,width in (('class StandaloneAnalyzer',230),('auto reset_visual_state',210)):
            start=next(i for i,line in enumerate(lines) if anchor in line)
            print('\n'.join(str(i+1)+': '+lines[i] for i in range(start,min(len(lines),start+width))))
        return
    verify()
    if args.mode=='verify':
        return
    _,remote,primary,tip=identity();assert git('rev-parse','HEAD').strip()==tip
    result,sources=recovery()
    assert set(git('diff','--cached','--name-only').splitlines())<=set(PATHS+RUNTIME),'Preserve unrelated staged work'
    git('add','--',*PATHS);git('diff','--cached','--check')
    for name,text in sources.items():
        blob=git('hash-object','-w','--stdin',data=text).strip()
        git('update-index','--add','--cacheinfo','100644,'+blob+',src/'+name)
    git('diff','--cached','--check')
    patch=git('diff','--cached')
    with Store() as store:
        store.evidence('publication-review','diff',dict(paths=PATHS+RUNTIME,head=tip,patch=patch))
    print(git('diff','--cached','--stat'),flush=True)
    if args.mode=='stage':
        return
    changed=set(git('diff','--cached','--name-only').splitlines())
    message='Invalidate stale Basic Pitch results across source discontinuities' if changed&set(RUNTIME) else 'Add paced app diagnostics and retained real-recording regressions'
    print(git('commit','-m',message),flush=True)
    # Publish the exact replay executable validated above as the new primary
    # reference. Other frozen historical studies retain their original tools.
    metadata=json.loads((ROOT/'build/pitch_heldout_tools/06aec4200b7fb541/build.json').read_text())
    metadata['inputs']['source_tree']=git('rev-parse','HEAD:src').strip()
    metadata['inputs']['objects']={p:h for p,h in metadata['inputs']['objects'].items() if p.rsplit('/',1)[-1] in ('BTT.o','DFT.o','Filter.o','STFT.o','Statistics.o','fastsin.o')}
    metadata['binaries']={'primary':result['binary_sha256']}
    assert all(git('show','HEAD:src/'+name)==text for name,text in sources.items())
    with Store() as store:
        store.evidence('primary-replay-tool','build',dict(binary=result['binary'],metadata=metadata))
    print(git('push',remote,'HEAD:'+primary),flush=True)
    assert identity()[3]==git('rev-parse','HEAD').strip()


if __name__=='__main__':
    main()
