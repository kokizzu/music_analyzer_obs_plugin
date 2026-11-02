// Native replay candidate only. Production inclusion requires the paired gates.
	if (mixed_source && guitar_enabled && keyboard_enabled && settings.experimental_piano_guitar_filter &&
	    !settings.basic_pitch_vocal_fusion_enabled &&
	    usable == static_cast<std::size_t>(std::lround(sample_rate_ * .1)) &&
	    std::abs(settings.analysis_interval_seconds - .05f) < 1e-6f) {
		const auto &candidates = snapshot.full_mix_debug_candidates;
		const std::size_t count = std::min(snapshot.full_mix_debug_candidate_count, candidates.size());
		bool attempted = false, valid = false, changed = false;
		timbre::Cepstra cepstra{};
		for (std::size_t i = 0; i < count; ++i) {
			const auto &candidate = candidates[i];
			if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi ||
			    !piano_guitar_model::eligible_scores(candidate.keyboard_score, candidate.guitar_score,
				candidate.vocal_score, candidate.vocal_tone_profile_supported)) continue;
			const int pc = midi_pitch_class(candidate.midi);
			bool keys = false, guitar = false;
			for (const auto &row : snapshot.keyboard_notes.rows)
				keys |= row[pc].active && row[pc].midi == candidate.midi && note_cell_effective_visual_level(row[pc]) > 0;
			for (const auto &row : snapshot.guitar_notes.rows)
				guitar |= row[pc].active && row[pc].midi == candidate.midi && note_cell_effective_visual_level(row[pc]) > 0;
			if (!keys || !guitar) continue;
			if (!attempted) {
				attempted = true;
				timbre::CepstralExtractor extractor;
				valid = extractor.extract(samples, usable, sample_rate_, cepstra);
			}
			if (!valid) continue;
			const auto values = piano_guitar_model::candidate_features(candidate, cepstra, candidates, count);
			if (!piano_guitar_model::should_remove_duplicate(values, candidate.vocal_tone_profile_supported)) continue;
			clear_note_grid_midi(snapshot.guitar_notes, candidate.midi);
			changed = true;
		}
		if (changed) {
			for (std::size_t pc = 0; pc < snapshot.guitar_notes.cells.size(); ++pc) {
				if (snapshot.guitar_notes.cells[pc].active) continue;
				for (const auto &row : snapshot.guitar_notes.rows)
					if (row[pc].active && (!snapshot.guitar_notes.cells[pc].active || row[pc].level > snapshot.guitar_notes.cells[pc].level))
						snapshot.guitar_notes.cells[pc] = row[pc];
			}
			write_note_grid_label(snapshot.guitar, snapshot.guitar_notes, -1);
		}
	}
