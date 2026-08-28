#pragma once

#include "analyzer.hpp"

namespace mao {

// This predicate is deliberately independent of model loading and threading.
// The offline replay validates it as a potential Vocal display mirror only
// when both analyzers name the same MIDI: Basic Pitch is confident enough and
// the native candidate is either Guitar-owned with a measurable keyboard
// component or Keyboard-owned with a measurable guitar component. The native
// ownership is preserved; the live worker uses this only to add a mirrored
// Vocal display candidate.
constexpr float kBasicPitchVocalFusionMinConfidence = 0.80f;
// Keep a small binary-float margin below the measured six-decimal boundary.
// This admits the intended CSD candidate (printed as 0.181744) without
// creating a rounded-boundary discrepancy between the audit and the runtime.
constexpr float kBasicPitchVocalFusionMinKeyboardScore = 0.1817f;
// The reciprocal Keyboard-owned branch is independently reproduced by CSD
// and ESMUC. Keep the same small margin below the six-decimal replay boundary
// (0.205994) so binary-float rounding cannot disagree with the audit.
constexpr float kBasicPitchVocalFusionMinGuitarScore = 0.2059f;

inline bool basic_pitch_vocal_fusion_supported(const FullMixDebugCandidate &native,
						       float basic_pitch_confidence)
{
	if (basic_pitch_confidence < kBasicPitchVocalFusionMinConfidence)
		return false;
	return (native.owner == InstrumentKind::Guitar &&
		native.keyboard_score >= kBasicPitchVocalFusionMinKeyboardScore) ||
	       (native.owner == InstrumentKind::Keyboard &&
		native.guitar_score >= kBasicPitchVocalFusionMinGuitarScore);
}

} // namespace mao
