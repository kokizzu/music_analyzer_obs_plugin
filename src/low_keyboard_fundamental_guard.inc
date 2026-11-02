		// Veto emission after choosing the original winner. Retain its score
		// so neither an octave runner-up nor renormalized neighbors are added.
		const float direct_support_confidence =
			require_direct_fundamental &&
				(raw_note_level <= 1.0e-6f || raw_note_level < strongest_note_level * 0.001f) ?
				0.0f : 1.0f;
