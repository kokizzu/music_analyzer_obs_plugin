#include "piano_guitar_verifier.hpp"
#include <fstream>
#include <iomanip>
#include <limits>

int main(int argc, char **argv)
{
	if (mao::piano_guitar_model::eligible_scores(1, 0, 0, true) ||
	    mao::piano_guitar_model::eligible_scores(1, .06, 0, false) ||
	    mao::piano_guitar_model::eligible_scores(1, 0, std::numeric_limits<double>::quiet_NaN(), false)) return 4;
	mao::piano_guitar_model::Features invalid{};
	invalid[30] = std::numeric_limits<double>::quiet_NaN();
	if (mao::piano_guitar_model::lower_probability(invalid) != 0) return 4;
	if (argc != 3) return 2;
	std::ifstream input(argv[1]);
	std::ofstream output(argv[2]);
	if (!input || !output) return 2;
	output << std::setprecision(17);
	mao::piano_guitar_model::Features raw{};
	while (input >> raw[0]) {
		for (std::size_t i = 1; i < raw.size(); ++i) if (!(input >> raw[i])) return 3;
		int profile = 0;
		if (!(input >> profile)) return 3;
		output << mao::piano_guitar_model::lower_probability(raw) << '\t'
			<< mao::piano_guitar_model::should_remove_duplicate(raw, profile != 0) << '\n';
	}
	return input.eof() ? 0 : 3;
}
