#include "basic_pitch_onnx_runtime.hpp"
#include "basic_pitch_onnx_decoder.hpp"
#include "basic_pitch_pcm_history.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>

static double cpu_ms()
{
	timespec value{};
	if (clock_gettime(CLOCK_THREAD_CPUTIME_ID, &value)) return -1;
	return value.tv_sec * 1000. + value.tv_nsec / 1e6;
}

int main(int argc, char **argv)
{
	if (argc != 6) return 2;
	const unsigned rate = std::stoul(argv[2]);
	if (rate != 16000 && rate != 44100 && rate != 48000) return 2;
	std::ifstream input(argv[1], std::ios::binary);
	std::ofstream out(argv[5]);
	if (!input || !out) return 3;
	mao::BasicPitchOnnxRuntime runtime;
	if (!runtime.load(argv[3], argv[4])) { std::cerr << runtime.last_error() << '\n'; return 4; }
	mao::BasicPitchPcmHistory history;
	mao::BasicPitchOnnxDecoder decoder;
	std::array<float, mao::BasicPitchOnnxRuntime::kInputSamples> waveform{};
	const auto hop = std::size_t(std::lround(rate * .05));
	std::vector<float> fresh(hop);
	std::size_t end = 0, captures = 0;
	out << "end_sample\tmidi\tlegacy\tedge4_note\tedge4_onset\twall_ms\tcpu_ms\n" << std::setprecision(12);
	while (input.read(reinterpret_cast<char *>(fresh.data()), fresh.size() * sizeof(float))) {
		for (float value : fresh) if (!std::isfinite(value)) return 5;
		end += hop;
		if (!history.push(fresh.data(), fresh.size(), rate, waveform)) continue;
		mao::BasicPitchOnnxOutput tensor;
		const double before_cpu = cpu_ms();
		const auto before_wall = std::chrono::steady_clock::now();
		if (!runtime.infer(waveform.data(), waveform.size(), tensor)) {
			std::cerr << runtime.last_error() << '\n'; return 6;
		}
		const double wall = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - before_wall).count();
		const double cpu = cpu_ms() - before_cpu;
		constexpr auto bins = mao::BasicPitchOnnxOutput::kNoteBins;
		if (tensor.note.size() != mao::BasicPitchOnnxOutput::kFrames * bins || tensor.onset.size() != tensor.note.size() || before_cpu < 0 || cpu < 0) return 7;
		const auto decoded = decoder.decode(tensor);
		constexpr auto edge = mao::BasicPitchOnnxOutput::kFrames - 4;
		for (std::size_t p = 0; p < bins; ++p) {
			const float note = tensor.note[edge * bins + p], onset = tensor.onset[edge * bins + p];
			if (!std::isfinite(note) || !std::isfinite(onset)) return 8;
			out << end << '\t' << p + 21 << '\t' << decoded.confidence[p] << '\t'
			    << note << '\t' << onset << '\t' << wall << '\t' << cpu << '\n';
		}
		++captures;
		if (captures % 200 == 0) std::cout << end / double(rate) << " seconds of causal model evidence\n" << std::flush;
	}
	if (!input.eof() || !captures) return 9;
	std::cout << captures << " model snapshots; original PCM, no gain or future audio\n";
}
