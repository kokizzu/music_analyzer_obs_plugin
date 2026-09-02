#include "basic_pitch_vocal_fusion.hpp"

#include <cstdio>

int main()
{
	int failures = 0;
	mao::FullMixDebugCandidate candidate;
	candidate.owner = mao::InstrumentKind::Guitar;
	candidate.keyboard_score = mao::kBasicPitchVocalFusionMinKeyboardScore;
	if (mao::basic_pitch_vocal_fusion_supported(candidate,
					 mao::kBasicPitchVocalFusionMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted instrumental guitar pitch\n");
		++failures;
	}
	candidate.vocal_tone_profile_supported = true;
	candidate.midi = 62;
	candidate.spectral_level = 1.0f;
	candidate.pitch_confidence = 0.93f;
	candidate.periodicity = 0.88f;
	candidate.harmonic_fit_error = 0.05f;
	candidate.spectral_centroid = 0.16f;
	candidate.local_noise_level = 0.07f;
	candidate.harmonic_ratios = {1.0f, 0.50f, 0.18f, 0.06f, 0.012f};
	if (!mao::basic_pitch_vocal_fusion_supported(candidate,
						 mao::kBasicPitchVocalFusionMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: rejected audited boundary\n");
		++failures;
	}
	candidate.keyboard_score = mao::kBasicPitchVocalFusionMinKeyboardScore - 0.0001f;
	if (mao::basic_pitch_vocal_fusion_supported(candidate,
						mao::kBasicPitchVocalFusionMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted below keyboard boundary\n");
		++failures;
	}
	candidate.keyboard_score = mao::kBasicPitchVocalFusionMinKeyboardScore;
	if (mao::basic_pitch_vocal_fusion_supported(
			candidate, mao::kBasicPitchVocalFusionMinConfidence - 0.001f)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted below ONNX boundary\n");
		++failures;
	}
	candidate.owner = mao::InstrumentKind::Keyboard;
	if (mao::basic_pitch_vocal_fusion_supported(candidate,
						mao::kBasicPitchVocalFusionMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted Keyboard without Guitar evidence\n");
		++failures;
	}
	candidate.guitar_score = mao::kBasicPitchVocalFusionMinGuitarScore;
	if (!mao::basic_pitch_vocal_fusion_supported(candidate,
						 mao::kBasicPitchVocalFusionMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: rejected audited reciprocal boundary\n");
		++failures;
	}
	candidate.guitar_score = mao::kBasicPitchVocalFusionMinGuitarScore - 0.0001f;
	if (mao::basic_pitch_vocal_fusion_supported(candidate,
						mao::kBasicPitchVocalFusionMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted below reciprocal boundary\n");
		++failures;
	}
	candidate.owner = mao::InstrumentKind::Other;
	candidate.guitar_score = 1.0f;
	if (mao::basic_pitch_vocal_fusion_supported(candidate,
						mao::kBasicPitchVocalFusionMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted unsupported owner\n");
		++failures;
	}
	candidate.guitar_score = 0.0f;
	candidate.other_score = mao::kBasicPitchVocalFusionOtherMinScore;
	if (mao::basic_pitch_vocal_fusion_supported(
			candidate, mao::kBasicPitchVocalFusionOtherMinConfidence - 0.001f)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted Other below ONNX boundary\n");
		++failures;
	}
	if (!mao::basic_pitch_vocal_fusion_supported(
			candidate, mao::kBasicPitchVocalFusionOtherMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: rejected audited Other boundary\n");
		++failures;
	}
	candidate.other_score = mao::kBasicPitchVocalFusionOtherMinScore - 0.0001f;
	if (mao::basic_pitch_vocal_fusion_supported(
			candidate, mao::kBasicPitchVocalFusionOtherMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted Other below score boundary\n");
		++failures;
	}

	// A real electronic-piano A3 mirror has a valid native vocal profile flag,
	// but its owner and measured body are still clearly guitar-like. Basic Pitch
	// must not turn that native upper partial into a Vocal display note.
	candidate = {};
	candidate.owner = mao::InstrumentKind::Guitar;
	candidate.midi = 57;
	candidate.vocal_tone_profile_supported = true;
	candidate.keyboard_score = 0.2835f;
	candidate.guitar_score = 0.7165f;
	candidate.spectral_level = 0.7355f;
	candidate.pitch_confidence = 0.6615f;
	candidate.periodicity = 0.7904f;
	candidate.harmonic_fit_error = 0.0302f;
	candidate.spectral_centroid = 0.1633f;
	candidate.spectral_slope = 0.0962f;
	candidate.local_noise_level = 0.1337f;
	candidate.harmonic_ratios = {1.0f, 0.3400f, 0.0967f, 0.0256f, 0.0066f};
	if (mao::basic_pitch_vocal_fusion_supported(candidate,
								mao::kBasicPitchVocalFusionMinConfidence)) {
		std::fprintf(stderr, "basic_pitch_vocal_fusion: accepted electronic-piano A3 mirror\n");
		++failures;
	}
	if (failures)
		return 1;
	std::printf("basic_pitch_vocal_fusion: 11 boundary checks passed\n");
	return 0;
}
