#include "keyboard_voice_classifier.hpp"
#include <fstream>
#include <iomanip>

int main(int argc, char **argv)
{
	const int triad[] = {60, 64, 67};
	const int harmonics[] = {60, 72, 79, 84, 88, 91};
	const int cluster[] = {60, 61, 62};
	if (!mao::keyboard_voice_model::has_local_keyboard_triad(64, triad, 3) ||
	    mao::keyboard_voice_model::has_local_keyboard_triad(60, harmonics, 6) ||
	    mao::keyboard_voice_model::has_local_keyboard_triad(60, cluster, 3)) return 4;
	if (argc != 3) return 2;
	std::ifstream input(argv[1]);
	std::ofstream output(argv[2]);
	if (!input || !output) return 2;
	output << std::setprecision(17);
	mao::keyboard_voice_model::Features features{};
	while (input >> features[0]) {
		for (std::size_t i = 1; i < features.size(); ++i) if (!(input >> features[i])) return 3;
		double keys, guitar, voice;
		int owner, profile;
		if (!(input >> keys >> guitar >> voice >> owner >> profile)) return 3;
		output << mao::keyboard_voice_model::lower_probability(features) << '\t'
			<< mao::keyboard_voice_model::should_suppress(features, owner != 0, keys, guitar, voice, profile != 0) << '\n';
	}
	return input.eof() ? 0 : 3;
}
