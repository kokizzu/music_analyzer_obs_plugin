#include "joint_grace_restore.hpp"
#include <cstring>
#include <iostream>

int main()
{
	mao::NoteGrid original{}, target{};
	auto &source = original.rows[0][0];
	source.active = true; source.midi = 60; source.level = .5f; std::strcpy(source.label, "C4");
	target.rows[0][0] = source;
	target.rows[0][0].visual_level = 0;
	auto &survivor = target.rows[1][0];
	survivor.active = true; survivor.midi = 72; survivor.level = .7f; std::strcpy(survivor.label, "C5");
	target.cells[0] = survivor;
	if (!mao::joint::restore_erased_note(target, original, 60)) return 1;
	if (target.rows[0][0].visual_level != source.visual_level || target.rows[1][0].midi != 72 || target.rows[1][0].level != .7f) return 2;
	if (mao::joint::restore_erased_note(target, original, 60)) return 3;
	if (mao::joint::restore_erased_note(target, original, 61)) return 4;
	for (auto &row : target.rows) row[0] = survivor;
	if (mao::joint::restore_erased_note(target, original, 60)) return 5;
	for (const auto &row : target.rows) if (row[0].midi != 72 || row[0].level != .7f) return 6;
	target.rows[0][0].visual_level = 0;
	if (!mao::joint::restore_erased_note(target, original, 60) || target.rows[0][0].midi != 60) {
		std::cerr << "Hidden row blocked a visible restoration\n"; return 8;
	}
	if (target.rows[1][0].midi != 72 || target.rows[1][0].level != .7f) return 9;
	target.rows[0][0] = {};
	if (!mao::joint::restore_erased_note(target, original, 60) || target.rows[0][0].midi != 60) return 7;
	std::cout << "Grace restoration: hidden note, duplicate rejection, missing source and occupied-row preservation passed\n";
}
