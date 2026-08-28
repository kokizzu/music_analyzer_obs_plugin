#include "basic_pitch_vocal_fusion.hpp"

#include <cstdio>

int main()
{
	int failures = 0;
	mao::FullMixDebugCandidate candidate;
	candidate.owner = mao::InstrumentKind::Guitar;
	candidate.keyboard_score = mao::kBasicPitchVocalFusionMinKeyboardScore;
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
	if (failures)
		return 1;
	std::printf("basic_pitch_vocal_fusion: 7 boundary checks passed\n");
	return 0;
}
