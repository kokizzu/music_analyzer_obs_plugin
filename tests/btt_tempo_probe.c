/* Offline PCM probe for the MIT Beat-and-Tempo-Tracking candidate backend. */
#include "BTT.h"
#include "MKAiff.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "usage: btt_tempo_probe WAV OFFSET_SECONDS DURATION_SECONDS\n");
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
    btt_set_min_tempo(tracker, 40.0);
    btt_set_max_tempo(tracker, 240.0);
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
    printf("raw=%.2f\tconfidence=%.3f\tsamples=%d\n", btt_get_tempo_bpm(tracker),
           btt_get_tempo_certainty(tracker), consumed);
    btt_destroy(tracker);
    return 0;
}
