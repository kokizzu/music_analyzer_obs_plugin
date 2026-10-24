// Research-only hook: primary replay has no held-out gain; not included by production.
	if (mixed_source && vocal_enabled && settings.experimental_keyboard_voice_suppression) {
		bool changed = false;
		bool cepstra_attempted = false, cepstra_valid = false;
		timbre::Cepstra cepstra{};
		const std::size_t count = std::min<std::size_t>(full_mix_ownership.debug_candidate_count,
			full_mix_ownership.debug_candidates.size());
		for (std::size_t i = 0; i < count; ++i) {
			const auto &candidate = full_mix_ownership.debug_candidates[i];
			if (candidate.midi < kFirstMidi || candidate.midi > kLastMidi) continue;
			const int pitch_class = midi_pitch_class(candidate.midi);
			bool visible_keys = false, visible_voice = false;
			for (const auto &row : snapshot.keyboard_notes.rows) {
				const auto &cell = row[pitch_class];
				visible_keys |= cell.active && cell.midi == candidate.midi && note_cell_effective_visual_level(cell) > 0;
			}
			for (const auto &row : snapshot.vocal_notes.rows) {
				const auto &cell = row[pitch_class];
				visible_voice |= cell.active && cell.midi == candidate.midi && note_cell_effective_visual_level(cell) > 0;
			}
			// Preserve the pitch itself in an independently visible native row.
			if (!visible_keys || !visible_voice) continue;
			const keyboard_voice_model::Features features = {
				candidate.onset_strength, candidate.decay_rate, candidate.pitch_stability,
				candidate.simultaneous_onset, candidate.pitch_confidence, candidate.periodicity,
				candidate.harmonic_fit_error, candidate.spectral_centroid, candidate.spectral_slope,
				candidate.local_noise_level, candidate.harmonic_ratios[1], candidate.harmonic_ratios[2],
				candidate.harmonic_ratios[3], candidate.harmonic_ratios[4]};
			if (!keyboard_voice_model::should_suppress(features, candidate.owner == InstrumentKind::Keyboard,
				candidate.keyboard_score, candidate.guitar_score, candidate.vocal_score,
				candidate.vocal_tone_profile_supported)) continue;
			// Verify a proposal against current-window spectral shape. The parent
			// alone confuses several pure vowels with piano; never apply it alone.
			if (!cepstra_attempted) {
				cepstra_attempted = true;
				timbre::CepstralExtractor extractor;
				cepstra_valid = extractor.extract(samples, usable, sample_rate_, cepstra);
			}
			if (!cepstra_valid || native_mfcc_voice::lower_probability(features, cepstra) < native_mfcc_voice::threshold) continue;
			clear_note_grid_midi(snapshot.vocal_notes, candidate.midi);
			changed = true;
		}
		if (changed) {
			for (std::size_t pc = 0; pc < snapshot.vocal_notes.cells.size(); ++pc) {
				if (snapshot.vocal_notes.cells[pc].active) continue;
				for (const auto &row : snapshot.vocal_notes.rows)
					if (row[pc].active && (!snapshot.vocal_notes.cells[pc].active ||
						row[pc].level > snapshot.vocal_notes.cells[pc].level))
						snapshot.vocal_notes.cells[pc] = row[pc];
			}
			write_note_grid_label(snapshot.vocal, snapshot.vocal_notes, -1);
		}
	}
