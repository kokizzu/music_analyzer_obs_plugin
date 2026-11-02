#include "joint_grace_history.hpp"
#include <iostream>

int main()
{
	mao::joint::OriginalDisplayHistory<2> history;
	for (unsigned i = 0; i < 3; ++i) {
		history.begin(7);
		if (history.preceded(0)) return 1;
		history.finish({true, false});
	}
	history.begin(7);
	if (!history.preceded(0) || history.preceded(1)) { std::cerr << "Missing three original visible frames\n"; return 2; }
	history.finish({false, true});
	history.begin(7);
	if (history.preceded(0) || history.preceded(1)) return 3;
	history.finish({true, true});
	for (unsigned i = 0; i < 4; ++i) { history.begin(7); history.finish({true, true}); }
	history.begin(8);
	if (history.preceded(0)) return 4;
	history.finish({true, true});
	for (unsigned i = 0; i < 4; ++i) { history.begin(8); history.finish({true, true}); }
	history.begin(8);
	history.begin(8); // An unfinished call must not preserve the prior run.
	if (history.preceded(0)) return 5;
	history.finish({true, true});
	history.reset();
	history.begin(8);
	if (history.preceded(0)) return 6;
	std::cout << "Grace history: prior-only counts, missing pitches, drops, unfinished calls and reset passed\n";
}
