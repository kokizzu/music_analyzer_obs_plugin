bool promote_keyboard_note_grid_primary_midi(NoteGrid &grid, int midi, float level, bool visibility_guard)
{
	if (visibility_guard) {
		if (midi < kFirstMidi || midi > kLastMidi) return false;
		const int pc = midi_pitch_class(midi);
		bool visible = grid.cells[pc].active && note_cell_effective_visual_level(grid.cells[pc]) > 0;
		for (const auto &row : grid.rows)
			visible |= row[pc].active && note_cell_effective_visual_level(row[pc]) > 0;
		if (!visible) return false;
	}
	return promote_note_grid_primary_midi(grid, midi, level);
}
