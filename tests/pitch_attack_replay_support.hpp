#pragma once
#include <array>
// Diagnostic evidence injection only. The harness changes this at each input
// endpoint using audio-only features and already-completed model results.
namespace mao_attack_replay {
inline std::array<bool, 88> supported{};
}
