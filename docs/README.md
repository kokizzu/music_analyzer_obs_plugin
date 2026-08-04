# Music Analyzer Documentation

## Audacious Song Title in the OBS Overlay

On Linux, the OBS plugin replaces the input/source-name text in the `MUSIC ANALYZER` header with Audacious's current song title or filename. This is OBS-only; the standalone and Android renderers keep their existing input/source labels.

### Detection and display rules

- The normal fast path asks `audtool current-song-tuple-data title` for the dedicated song-title field. This avoids depending on a customized or truncated titlebar such as `playlist - output - artist - song title`.
- If the dedicated title tuple is unavailable, the plugin checks Audacious through Linux `/proc`, reads `wmctrl -lx`, and selects the most likely Audacious playback window.
- The titlebar fallback accepts `Artist - Album - Song title/filename`, a two-field `Artist - filename.flac`, or a plain title/filename.
- Optional decorations such as ` - Audacious`, `[Audacious]`, and an `Audacious - ` prefix are removed.
- When neither the tuple nor a usable window title is available, including native Wayland windows hidden from `wmctrl`, the plugin falls back to `audtool current-song`, then to the basename from `audtool current-song-filename`.
- Before the first background check completes, the header shows `AUDACIOUS CHECKING`.
- When Audacious is not running, the header shows `AUDACIOUS NOT RUNNING`.
- When Audacious is running but no usable title is available, the header shows `AUDACIOUS TITLE UNAVAILABLE`.
- Titles of 34 characters or fewer remain static. Longer titles use a 34-character marquee, advance one character every 250 ms, and loop with a visible `---` separator.
- The built-in overlay font currently supports ASCII. Unsupported UTF-8 characters are replaced with `?` instead of corrupting the rendered text.

### Build paths

- `make install-user` is supported through the root `GNUmakefile`, which includes the existing `Makefile` and adds the Audacious sources plus OBS-only renderer redirection.
- CMake builds include the same Audacious sources and redirection.
- The Makefile path forces `plugin.o` to rebuild after this integration is pulled, preventing a stale pre-Audacious object from being reinstalled.
- Run `make test-audacious-title` for the focused parser and marquee test.

### Efficiency requirements

- Audacious metadata detection runs only in a lazy background poller, at most once per second.
- The usual tuple-title path launches one short `audtool` query per poll and skips `/proc` plus `wmctrl` when successful.
- `/proc`, `wmctrl`, and the additional fallback commands run only when the tuple-title path fails.
- The render path copies cached state under a short mutex and calculates the marquee position from elapsed time; it performs no external command or per-frame polling.
- The marquee resets only when the detected song or Audacious running state changes.
- The analyzer audio callback, analyzer ring buffer, and DSP worker are unchanged.
- The poller starts lazily when the OBS Audacious-aware renderer is first used and stops cleanly when the plugin is unloaded.

### Runtime dependencies

- `audtool` supplies the preferred dedicated title tuple and fallback title/filename data.
- Linux `/proc` is used for fallback process detection.
- `wmctrl` is used for titlebar fallback. Missing `wmctrl` does not disable song-title display when `audtool` is available.
