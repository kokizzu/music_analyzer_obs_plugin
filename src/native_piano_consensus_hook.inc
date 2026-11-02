	// Current-window forest decisions require temporal corroboration before
	// removing a duplicate. No tracking envelope or other instrument is edited.
	if (mixed_source && keyboard_enabled && settings.native_piano_duplicate_consensus &&
	    !settings.experimental_piano_guitar_filter && !settings.basic_pitch_vocal_fusion_enabled &&
	    (sample_rate_ == 16000 || sample_rate_ == 44100 || sample_rate_ == 48000) &&
	    usable == static_cast<std::size_t>(std::lround(sample_rate_ * .1)) &&
	    std::abs(settings.analysis_interval_seconds - .05f) < 1e-6f) {
		routing::DuplicateConsensus<kNoteProbeCount * 2>::Mask predicted{};
		const auto &candidates = snapshot.full_mix_debug_candidates;
		const std::size_t count = std::min(snapshot.full_mix_debug_candidate_count, candidates.size());
		bool attempted = false, valid = false;
		timbre::Cepstra cepstra{};
		const auto visible = [](const NoteGrid &grid, int midi) {
			const int pc = midi_pitch_class(midi);
			for (const auto &row : grid.rows)
				if (row[pc].active && row[pc].midi == midi && note_cell_effective_visual_level(row[pc]) > 0) return true;
			return false;
		};
		for (std::size_t i = 0; i < count; ++i) {
			const auto &candidate = candidates[i];
			if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi ||
			    !piano_guitar_model::eligible_scores(candidate.keyboard_score, candidate.guitar_score,
				candidate.vocal_score, candidate.vocal_tone_profile_supported) ||
			    !visible(snapshot.keyboard_notes, candidate.midi)) continue;
			const bool guitar = guitar_enabled && visible(snapshot.guitar_notes, candidate.midi);
			const bool voice = vocal_enabled && visible(snapshot.vocal_notes, candidate.midi);
			if (!guitar && !voice) continue;
			if (!attempted) {
				attempted = true;
				timbre::CepstralExtractor extractor;
				valid = extractor.extract(samples, usable, sample_rate_, cepstra);
			}
			if (!valid) continue;
			const auto values = piano_guitar_model::candidate_features(candidate, cepstra, candidates, count);
			if (!piano_guitar_model::should_remove_duplicate(values, candidate.vocal_tone_profile_supported)) continue;
			const std::size_t index = static_cast<std::size_t>(candidate.midi - kFirstMidi);
			predicted[index] = guitar;
			predicted[index + kNoteProbeCount] = voice;
		}
		const auto confirmed = routing_duplicate_consensus_.confirm(predicted);
		const auto apply = [&](NoteGrid &grid, InstrumentState &state, std::size_t offset) {
			bool changed = false;
			for (std::size_t i = 0; i < kNoteProbeCount; ++i) {
				if (!confirmed[i + offset]) continue;
				clear_note_grid_midi(grid, static_cast<int>(i) + kFirstMidi);
				changed = true;
			}
			if (!changed) return;
			for (std::size_t pc = 0; pc < grid.cells.size(); ++pc) {
				if (grid.cells[pc].active) continue;
				for (const auto &row : grid.rows)
					if (row[pc].active && (!grid.cells[pc].active || row[pc].level > grid.cells[pc].level)) grid.cells[pc] = row[pc];
			}
			write_note_grid_label(state, grid, -1);
		};
		apply(snapshot.guitar_notes, snapshot.guitar, 0);
		apply(snapshot.vocal_notes, snapshot.vocal, kNoteProbeCount);
	} else {
		routing_duplicate_consensus_.reset();
	}
