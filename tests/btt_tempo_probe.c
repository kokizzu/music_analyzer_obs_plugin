/* Offline PCM probe for the MIT Beat-and-Tempo-Tracking candidate backend. */
#include "BTT.h"
#include "MKAiff.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    if (argc != 4 && argc != 6) {
        fprintf(stderr, "usage: btt_tempo_probe WAV OFFSET_SECONDS DURATION_SECONDS [MIN_BPM MAX_BPM]\n");
        return 2;
    }
    MKAiff *audio = aiffWithContentsOfFile(argv[1]);
    if (audio == NULL) {
        fprintf(stderr, "btt_tempo_probe: unable to read %s\n", argv[1]);
        return 2;
    }
    aiffMakeMono(audio);
    if (aiffSampleRate(audio) != BTT_SUGGESTED_SAMPLE_RATE) {
        fprintf(stderr, "btt_tempo_probe: expected 44100 Hz, got %.0f\n", aiffSampleRate(audio));
        return 2;
    }
    BTT *tracker = btt_new_default();
    if (tracker == NULL)
        return 2;
    const double min_tempo = argc == 6 ? strtod(argv[4], NULL) : 40.0;
    const double max_tempo = argc == 6 ? strtod(argv[5], NULL) : 240.0;
    if (min_tempo <= 0.0 || max_tempo <= min_tempo) {
        fprintf(stderr, "btt_tempo_probe: invalid tempo range %.2f..%.2f\n", min_tempo, max_tempo);
        btt_destroy(tracker);
        return 2;
    }
    btt_set_min_tempo(tracker, min_tempo);
    btt_set_max_tempo(tracker, max_tempo);
    aiffSetPlayheadToSeconds(audio, strtod(argv[2], NULL));
    const int limit = (int)(strtod(argv[3], NULL) * aiffSampleRate(audio));
    dft_sample_t samples[256];
    int consumed = 0;
    while (consumed < limit) {
        const int want = limit - consumed < 256 ? limit - consumed : 256;
        const int read = aiffReadFloatingPointSamplesAtPlayhead(audio, samples, want, aiffYes);
        if (read <= 0)
            break;
        btt_process(tracker, samples, read);
        consumed += read;
    }
    printf("raw=%.2f\tconfidence=%.3f\tmin_tempo=%.2f\tmax_tempo=%.2f\tsamples=%d\n",
           btt_get_tempo_bpm(tracker), btt_get_tempo_certainty(tracker), min_tempo, max_tempo, consumed);
    btt_destroy(tracker);
    return 0;
}
