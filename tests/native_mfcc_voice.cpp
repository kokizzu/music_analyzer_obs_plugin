#include "native_mfcc_voice.hpp"
#include <fstream>
#include <iomanip>

int main(int argc, char **argv)
{
	if (argc != 3) return 2;
	std::ifstream input(argv[1]);
	std::ofstream output(argv[2]);
	if (!input || !output) return 2;
	output << std::setprecision(17);
	mao::keyboard_voice_model::Features base{};
	mao::timbre::Cepstra cepstra{};
	while (input >> base[0]) {
		for (std::size_t i = 1; i < base.size(); ++i) if (!(input >> base[i])) return 3;
		for (auto &value : cepstra) if (!(input >> value)) return 3;
		output << mao::native_mfcc_voice::lower_probability(base, cepstra) << '\n';
	}
	return input.eof() ? 0 : 3;
}
