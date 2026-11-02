	if (joint_grace_eligible && mao_stage_trace::state.started) {
		auto &observer = mao_stage_trace::state;
		observer.finish(snapshot.keyboard_notes);
		const auto original_levels = mao_stage_trace::levels(snapshot.keyboard_notes);
		joint::OriginalDisplayHistory<kNoteProbeCount>::Mask original{}, candidates{};
		std::array<const char *, kNoteProbeCount> last_removal{};
		for (const auto &event : observer.events)
			if (event.before > 0 && event.after <= 0)
				last_removal[static_cast<std::size_t>(event.midi - kFirstMidi)] = event.between ? "between" : event.stage;
		bool any = false;
		for (std::size_t i = 0; i < original.size(); ++i) {
			original[i] = original_levels[i] > 0;
			const auto &tracking = keyboard_note_tracking_[i];
			candidates[i] = observer.initial[i] > 0 && !original[i] && last_removal[i] &&
				std::strcmp(last_removal[i], "suppress_other_dominant_same_pitch_keyboard_shadows") == 0 &&
				tracking.confirmed && tracking.consecutive_hits >= 3 && joint_grace_history_.preceded(i);
			any |= candidates[i];
		}
		// Only original final display updates history. Restorations cannot keep
		// themselves eligible or bypass confirmation on a following frame.
		joint_grace_history_.finish(original);
		if (any && joint_before_other) {
			if (!joint_grace_fitter_ready_)
				joint_grace_fitter_ready_ = joint_grace_fitter_.configure(std::vector<double>(joint::kDictionary.begin(), joint::kDictionary.end()));
			joint::FitOutput fit;
			if (joint_grace_fitter_ready_ && joint_grace_fitter_.extract(samples, usable, sample_rate_, fit)) {
				bool changed = false;
				for (std::size_t i = 0; i < candidates.size(); ++i) {
					const int midi = static_cast<int>(i) + kFirstMidi;
					if (!candidates[i] || midi < 21 || midi > 108 || fit.relative[midi - 21] < .8 || fit.explained[midi - 21] < .3) continue;
					changed |= joint::restore_erased_note(snapshot.keyboard_notes, *joint_before_other, midi);
				}
				if (changed) write_note_grid_label(snapshot.keyboard, snapshot.keyboard_notes, -1);
			}
		}
	} else {
		joint_grace_history_.reset();
	}
