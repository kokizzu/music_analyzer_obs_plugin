# MIR-1K Clean Vocal Fixtures

This directory contains 221 deterministic 0.5-second clean-vocal excerpts selected from the MIR-1K dataset's right-channel singing tracks. Each excerpt is aligned to a manually labelled MIDI-pitch region and is used only for automated detector regression tests.

Source dataset: MIR-1K, 1,000 karaoke-song clips with accompaniment and singing voice in separate stereo channels, manual pitch contours, and a CC BY 4.0 Figshare distribution: https://figshare.com/articles/dataset/MIR-1K_rar/5802891

The original archive is not included. `scripts/import_mir1k_vocal_archive.py` and `scripts/prepare_mir1k_vocal_fixtures.py` reproduce the curated subset from the source archive; the committed `manifest.tsv` records the expected note for each clip.
