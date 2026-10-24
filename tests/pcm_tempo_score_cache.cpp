#include "pcm_tempo_evidence.hpp"
#include <chrono>
#include <cstdio>
#include <random>

// Frozen pre-optimization arithmetic from primary commit 44a95cc. This
// reference deliberately recomputes roots in each BPM/pair iteration.
static int legacy(const std::vector<mao::pcm_tempo::Peak> &peaks)
{
	if (peaks.size() < 3 || peaks.back().time - peaks.front().time < .45) return 0;
	double total = 0, best = 0;
	for (const auto &peak : peaks) total += std::sqrt(std::max(peak.strength, 0.));
	int winner = 0;
	std::vector<double> phase(peaks.size());
	for (int bpm = 50; bpm <= 220; ++bpm) {
		const double period = 60. / bpm;
		const double tolerance = std::clamp(period * .12, .035, .085);
		double score = 0;
		for (std::size_t i = 0; i < peaks.size(); ++i) phase[i] = std::sqrt(std::max(peaks[i].strength, 0.));
		for (std::size_t older = 0; older < peaks.size(); ++older) for (std::size_t newer = older + 1; newer < peaks.size(); ++newer) {
			const auto &a = peaks[older], &b = peaks[newer];
			const double delta = b.time - a.time;
			const int beats = static_cast<int>(std::floor(delta / period + .5));
			if (beats < 1 || beats > 8) continue;
			const double error = std::abs(delta - beats * period);
			if (error > tolerance) continue;
			const double match = 1 - error / tolerance;
			score += std::pow(a.strength * b.strength, .5) * (beats == 1 ? 1 : .18) * match * match;
			phase[older] += std::sqrt(std::max(b.strength, 0.)) * match;
			phase[newer] += std::sqrt(std::max(a.strength, 0.)) * match;
		}
		if (peaks.size() >= 4 && score > 0 && total > 1e-6)
			score *= .45 + .55 * std::clamp(*std::max_element(phase.begin(), phase.end()) / total, 0., 1.);
		if (score > best) { best = score; winner = bpm; }
	}
	return winner;
}

int main()
{
	std::mt19937 generator(20261024);
	std::uniform_real_distribution<double> strength(0., 1.), jitter(-.005, .005);
	int checks = 0;
	for (int test = 0; test < 3000; ++test) {
		std::vector<mao::pcm_tempo::Peak> peaks;
		const int count = test < 4 ? std::array<int, 4>{0, 2, 64, 65}[test] : 3 + int(generator() % 28);
		for (int i = 0; i < count; ++i) peaks.push_back({i * .13 + jitter(generator), test % 5 ? strength(generator) : 1.});
		if (legacy(peaks) != mao::pcm_tempo::estimate_tempo(peaks)) {
			std::fprintf(stderr, "tempo score cache changed result in case %d\n", test);
			return 1;
		}
		++checks;
	}
	std::vector<mao::pcm_tempo::Peak> peaks;
	for (int i = 0; i < 19; ++i) peaks.push_back({i * .16, strength(generator)});
	volatile int sink = 0;
	double before = 0, after = 0;
	for (int round = 0; round < 4; ++round) for (int order = 0; order < 2; ++order) {
		const bool reference = (round + order) % 2 == 0;
		const auto started = std::chrono::steady_clock::now();
		for (int run = 0; run < 100; ++run) sink += reference ? legacy(peaks) : mao::pcm_tempo::estimate_tempo(peaks);
		const double duration = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - started).count();
		(reference ? before : after) += duration;
	}
	std::printf("tempo score cache: %d paired cases passed; reference %.4f ms, cached %.4f ms per 19-peak estimate (sink %d)\n",
		checks, before / 400, after / 400, int(sink));
}
