#include "joint_grace_body.hpp"
#include <array>
#include <iostream>
#include <limits>

int main()
{
	std::array<mao::FullMixDebugCandidate, 2> rows{};
	rows[0].midi = 60; rows[0].keyboard_score = .8f; rows[0].pitch_stability = .9f;
	if (!mao::joint::stable_body(rows.data(), rows.size(), 60)) return 1;
	rows[1] = rows[0]; rows[1].keyboard_score = .9f; rows[1].onset_strength = .2f;
	if (mao::joint::stable_body(rows.data(), rows.size(), 60)) return 2;
	rows[1].onset_strength = 0; rows[1].decay_rate = .2f;
	if (mao::joint::stable_body(rows.data(), rows.size(), 60)) return 3;
	rows[1].decay_rate = 0; rows[1].pitch_stability = .7f;
	if (mao::joint::stable_body(rows.data(), rows.size(), 60)) return 4;
	rows[1].pitch_stability = .9f; rows[1].vocal_tone_profile_supported = true;
	if (mao::joint::stable_body(rows.data(), rows.size(), 60)) return 5;
	rows[1].vocal_tone_profile_supported = false; rows[1].onset_strength = std::numeric_limits<float>::quiet_NaN();
	if (mao::joint::stable_body(rows.data(), rows.size(), 60)) return 6;
	if (mao::joint::stable_body(nullptr, 0, 60) || mao::joint::stable_body(rows.data(), rows.size(), 61)) return 7;
	std::cout << "Stable body: strongest candidate, attack/decay veto, pitch stability, profile and invalid data passed\n";
}
