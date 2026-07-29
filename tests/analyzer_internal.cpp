#include "../src/analyzer.cpp"

#include <cstdio>
#include <cstring>
#include <string>

namespace mao {
namespace test_internal {

struct Runner {
	int checks = 0;
	int failures = 0;

	void expect(bool ok, const std::string &message)
	{
		++checks;
		if (!ok) {
			++failures;
			std::fprintf(stderr, "%s\n", message.c_str());
		}
	}
};

ChordResult make_crowded_chord(const char *label)
{
	ChordResult chord;
	std::snprintf(chord.label, sizeof(chord.label), "%s", label);
	chord.root = 0;
	chord.confidence = 0.80f;
	chord.uncertain = false;
	return chord;
}

void check_crowded_guitar_prune_modes(Runner &runner)
{
	static constexpr const char *kCrowdedLabel = "Csus2=Gsus4=C=Cm=Cmaj7=Cpow=Caug";

	ChordResult isolated = make_crowded_chord(kCrowdedLabel);
	prune_crowded_guitar_chord_label(isolated, false);
	runner.expect(chord_label_has_exact_component(isolated.label, "Csus2"),
		      std::string("isolated crowded guitar prune: expected primary, got `") + isolated.label +
			      "`");
	runner.expect(chord_label_has_exact_component(isolated.label, "Gsus4"),
		      std::string("isolated crowded guitar prune: expected equivalent sus alias, got `") +
			      isolated.label + "`");
	runner.expect(chord_label_has_exact_component(isolated.label, "Cpow"),
		      std::string("isolated crowded guitar prune: expected no-third alias, got `") +
			      isolated.label + "`");
	runner.expect(chord_label_has_exact_component(isolated.label, "Caug"),
		      std::string("isolated crowded guitar prune: expected same-root altered alias, got `") +
			      isolated.label + "`");

	ChordResult mixed = make_crowded_chord(kCrowdedLabel);
	prune_crowded_guitar_chord_label(mixed, true);
	runner.expect(std::strcmp(mixed.label, "Csus2=Gsus4=C=Cm") == 0,
		      std::string("mixed crowded guitar prune: expected strict primary/equivalent/plain label, got `") +
			      mixed.label + "`");
	runner.expect(chord_label_component_count(mixed.label) < chord_label_component_count(isolated.label),
		      std::string("mixed crowded guitar prune: expected fewer components than isolated, got mixed `") +
			      mixed.label + "` isolated `" + isolated.label + "`");
	runner.expect(!chord_label_has_exact_component(mixed.label, "Cpow"),
		      std::string("mixed crowded guitar prune: expected no-third alias pruned, got `") +
			      mixed.label + "`");
	runner.expect(!chord_label_has_exact_component(mixed.label, "Caug"),
		      std::string("mixed crowded guitar prune: expected altered alias pruned, got `") +
			      mixed.label + "`");
	runner.expect(!chord_label_has_exact_component(mixed.label, "Cmaj7"),
		      std::string("mixed crowded guitar prune: expected extension alias pruned, got `") +
			      mixed.label + "`");
}

int run()
{
	Runner runner;
	check_crowded_guitar_prune_modes(runner);
	if (runner.failures) {
		std::fprintf(stderr, "analyzer_internal: %d/%d checks failed\n", runner.failures,
			     runner.checks);
		return 1;
	}
	std::printf("analyzer_internal: %d checks passed\n", runner.checks);
	return 0;
}

} // namespace test_internal
} // namespace mao

int main()
{
	return mao::test_internal::run();
}
