"""Inject the experimental causal guard into a plain primary source export."""
from routing_duration_baseline import ROOT


def candidate_sources(cpp, header):
    header = header.replace('#include "routing_duplicate_consensus.hpp"', '#include "routing_duplicate_consensus.hpp"\n#include "low_keyboard_coherence.hpp"', 1)
    anchor = '\tbool native_piano_duplicate_consensus = true;'
    assert header.count(anchor) == 1
    header = header.replace(anchor, anchor + '\n\tbool experimental_low_keyboard_coherence = false;', 1)
    anchor = '\trouting::DuplicateConsensus<kNoteProbeCount * 2> routing_duplicate_consensus_;'
    assert header.count(anchor) == 1
    header = header.replace(anchor, anchor + '\n\tduration::LowKeyboardCoherence low_keyboard_coherence_;', 1)
    anchor = 'void AnalysisEngine::reset_analysis_state()\n{'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, anchor + '\n\tlow_keyboard_coherence_.reset();', 1)
    anchor = '\tconst std::size_t usable = std::min(count, analysis_window_samples_);'
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, anchor + '''
	const bool coherence_enabled = settings.experimental_low_keyboard_coherence &&
		input_mode == AnalysisInputMode::FullMix && !settings.basic_pitch_vocal_fusion_enabled &&
		std::abs(settings.analysis_interval_seconds - .05f) < 1e-6f && count == usable;
	if (coherence_enabled) low_keyboard_coherence_.feed(samples, usable, sample_rate_, dropped_windows);
	else low_keyboard_coherence_.reset();
	duration::LowKeyboardCoherence::Mask newly_recovered_low{};
	const auto low_visible = [](const NoteGrid &grid, int midi) {
		for (const auto &row : grid.rows) for (const auto &cell : row)
			if (cell.active && cell.midi == midi && note_cell_effective_visual_level(cell) > 0) return true;
		return false;
	};''', 1)
    anchor = '''			for (const NoteCandidate &candidate : low_keyboard_display_candidates)
				write_note_grid_cell(snapshot.keyboard_notes, candidate, strongest_low_keyboard_candidate,
						    note_visual_loudness(rms));'''
    assert cpp.count(anchor) == 1
    cpp = cpp.replace(anchor, '''			for (const NoteCandidate &candidate : low_keyboard_display_candidates) {
				const bool already_visible = low_visible(snapshot.keyboard_notes, candidate.midi);
				write_note_grid_cell(snapshot.keyboard_notes, candidate, strongest_low_keyboard_candidate,
						    note_visual_loudness(rms));
				if (candidate.midi >= 21 && candidate.midi < 40 && !already_visible && low_visible(snapshot.keyboard_notes, candidate.midi))
					newly_recovered_low[candidate.midi - 21] = true;
			}''', 1)
    start = cpp.index('AnalysisSnapshot AnalysisEngine::analyze(')
    end = cpp.index('\n}', start)
    body = cpp[start:end]
    anchor = '\n\treturn snapshot;'
    assert body.count(anchor) == 1
    hook = '''
	if (coherence_enabled) {
		duration::LowKeyboardCoherence::Mask original{};
		for (int midi = 21; midi < 40; ++midi) original[midi - 21] = low_visible(snapshot.keyboard_notes, midi);
		const auto rejected = low_keyboard_coherence_.finish(original);
		bool changed = false;
		for (int midi = 21; midi < 40; ++midi) {
			if (!rejected[midi - 21] || !newly_recovered_low[midi - 21]) continue;
			clear_note_grid_midi(snapshot.keyboard_notes, midi);
			changed = true;
		}
		if (changed) {
			for (std::size_t pc = 0; pc < snapshot.keyboard_notes.cells.size(); ++pc) {
				if (snapshot.keyboard_notes.cells[pc].active) continue;
				for (const auto &row : snapshot.keyboard_notes.rows)
					if (row[pc].active && (!snapshot.keyboard_notes.cells[pc].active || row[pc].level > snapshot.keyboard_notes.cells[pc].level))
						snapshot.keyboard_notes.cells[pc] = row[pc];
			}
			write_note_grid_label(snapshot.keyboard, snapshot.keyboard_notes, -1);
		}
	}
'''
    return cpp[:start] + body.replace(anchor, hook + anchor, 1) + cpp[end:], header
