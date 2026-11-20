"""Construct a narrowly scoped primary patch without overwriting local analyzer work."""
from publish_next_detection import git
from routing_duration_baseline import ROOT


def replace_once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


def candidate_sources():
    cpp=git('show','HEAD:src/analyzer.cpp');header=git('show','HEAD:src/analyzer.hpp')
    if 'void AnalysisEngine::reset_basic_pitch_recovery_context()' in cpp:
        # After publication, validate the committed implementation directly.
        return {name:git('show','HEAD:src/'+name) for name in
            ('analyzer.cpp','analyzer.hpp','basic_pitch_onnx_worker.cpp','basic_pitch_onnx_worker.hpp')}
    helper='''void AnalysisEngine::reset_basic_pitch_recovery_context()
{
\tif (basic_pitch_worker_)
\t\tbasic_pitch_worker_->reset_context();
\tbasic_pitch_pcm_history_.reset();
\tbasic_pitch_notes_ = {};
\tbasic_pitch_notes_ready_ = false;
}

'''
    cpp=replace_once(cpp,'void AnalysisEngine::update_basic_pitch_vocal_fusion(',helper+'void AnalysisEngine::update_basic_pitch_vocal_fusion(')
    cpp=replace_once(cpp,'void AnalysisEngine::reset_analysis_state()\n{','void AnalysisEngine::reset_analysis_state()\n{\n\treset_basic_pitch_recovery_context();')
    anchor='\tconst AnalysisInputMode input_mode = resolve_input_mode(settings, resolved_source_name);'
    cpp=replace_once(cpp,anchor,'''
\tif (dropped_windows != basic_pitch_recovery_dropped_windows_) {
\t\tbasic_pitch_recovery_dropped_windows_ = dropped_windows;
\t\treset_basic_pitch_recovery_context();
\t}
'''+anchor)
    header=replace_once(header,'\tvoid reset_analysis_state();','\tvoid reset_analysis_state();\n\tvoid reset_basic_pitch_recovery_context();\n\tuint64_t basic_pitch_recovery_dropped_windows_ = 0;')
    # This focused reset implementation already exists locally. Reuse and test
    # it; unrelated analyzer/standalone changes are never staged wholesale.
    worker={name:(ROOT/'src'/name).read_text() for name in ('basic_pitch_onnx_worker.cpp','basic_pitch_onnx_worker.hpp')}
    assert 'first_valid_sequence_' in worker['basic_pitch_onnx_worker.hpp']
    assert 'processed_sequence_ = std::max(processed_sequence_, sequence);' in worker['basic_pitch_onnx_worker.cpp']
    return dict(worker,**{'analyzer.cpp':cpp,'analyzer.hpp':header})
