# Music Analyzer OBS Plugin

Native OBS Studio plugin that analyzes a music mix and displays an instrument-oriented overlay:

- Drums: bass drum/kick, snare, hi-hat, crash, tom, and ride hit indicators
- Bass: detected note
- Guitar, keyboard, vocal, and other instruments: detected note or chord label

The analyzer is designed for real-time OBS use. It uses bounded DSP heuristics rather than a large ML stem-separation model: audio is downmixed into a fixed ring buffer, analyzer windows are copied to a worker thread at a configurable interval, and the OBS audio callback returns immediately after lightweight buffering. The overlay source renders a single reusable RGBA texture.

## OBS Usage

1. Build the plugin.
2. Copy `build/music-analyzer-obs.so` to an OBS plugin directory, for example:

   ```sh
   mkdir -p ~/.config/obs-studio/plugins/music-analyzer-obs/bin/64bit
   cp build/music-analyzer-obs.so ~/.config/obs-studio/plugins/music-analyzer-obs/bin/64bit/
   ```

3. Restart OBS.
4. Add the `Music Analyzer Filter` audio filter to the music/audio source you want analyzed.
5. Add the `Music Analyzer Overlay` source to the scene to show the overlay.

## Build

With the Makefile:

```sh
make
```

If the system OBS headers require SIMDe and `libsimde-dev` is not installed, `make` fetches and extracts that header-only package under `build/deps` without using sudo.

Run the analyzer smoke tests:

```sh
make test
```

Optional CMake build, assuming the OBS development dependencies are installed system-wide:

```sh
/usr/bin/cmake -S . -B build-cmake -DCMAKE_BUILD_TYPE=Release
/usr/bin/cmake --build build-cmake
```

## Performance Notes

The plugin intentionally avoids expensive per-frame work:

- No allocation in the OBS audio callback after source creation.
- Analyzer work runs on a worker thread and drops stale windows instead of queueing unbounded work.
- Fixed 4096-sample windows and configurable update intervals bound CPU use.
- Notes/chords use precomputed Goertzel probes instead of per-callback FFT allocation.
- The overlay updates a single texture at a capped frame rate.

This is approximate mix detection, not true isolated stem separation. For precise separation of crowded mixes, an offline or GPU-backed ML stem separator would be needed before OBS receives the audio.
