# Music Analyzer Documentation

## Audacious Song Title in the OBS Overlay

On Linux, the OBS plugin replaces the input/source-name text in the `MUSIC ANALYZER` header with Audacious's current `Artist - Song title`. This is OBS-only; the standalone and Android renderers keep their existing input/source labels.

### Detection and display rules

- The normal fast path asks `audtool current-song-tuple-data artist` and `audtool current-song-tuple-data title` for dedicated metadata fields. This avoids depending on a customized or truncated titlebar such as `playlist - output - artist - song title`.
- The displayed value combines the available fields as `Artist - Song title`; if either field is missing, the available field is shown by itself.
- Presentation-only groups are removed selectively. Recognized suffixes include `(Live)`, `(Official Video)`, `(Official Music Video)`, `(Official Lyric Video)`, `(Official Lyrics Video)`, official-audio/visualizer equivalents, and the same labels in square brackets.
- Ordinary descriptive groups are preserved. For example, `OCEANS (Pop-Punk Cover) [OVvN_YzWEgc]` remains unchanged, and video-ID groups are not removed.
- If the dedicated title tuple is unavailable, the plugin checks Audacious through Linux `/proc`, reads `wmctrl -lx`, and selects the most likely Audacious playback window.
- The titlebar fallback accepts `Artist - Album - Song title/filename`, a two-field `Artist - filename.flac`, or a plain title/filename.
- Optional Audacious application decorations such as ` - Audacious`, `[Audacious]`, and an `Audacious - ` prefix are removed.
- When neither the tuple nor a usable window title is available, including native Wayland windows hidden from `wmctrl`, the plugin falls back to `audtool current-song`, then to the basename from `audtool current-song-filename`.
- Before the first background check completes, the header shows `AUDACIOUS CHECKING`.
- When Audacious is not running, the header shows `AUDACIOUS NOT RUNNING`.
- When Audacious is running but no usable title is available, the header shows `AUDACIOUS TITLE UNAVAILABLE`.
- Long titles use the existing bitmap marquee, advancing one character every 250 ms and looping with a visible separator.
- The stabilized renderer intentionally uses the analyzer's original bitmap text path. Non-ASCII characters currently appear as `?`; the experimental nested OBS FreeType compositor was removed because it could make the entire analyzer source transparent.

### Build paths

- `make install-user` is supported through the root `GNUmakefile`, which includes the existing `Makefile` and adds the Audacious title sources plus OBS-only renderer redirection.
- OBS source registration and final texture drawing remain untouched.
- CMake builds include the same Audacious sources and renderer redirection.
- The Makefile path forces `plugin.o` to rebuild after this integration is pulled, preventing a stale object from being reinstalled.
- Run `make test-audacious-title` for focused metadata-cleanup and marquee tests.

### Efficiency requirements

- Audacious metadata detection runs only in a lazy background poller, at most once per second.
- The usual tuple path launches short `audtool` queries per poll and skips `/proc` plus `wmctrl` when successful.
- `/proc`, `wmctrl`, and the additional fallback commands run only when the tuple-title path fails.
- The render path reads cached metadata and calculates the marquee position in memory; it performs no external command or per-frame metadata polling.
- The analyzer audio callback, analyzer ring buffer, DSP worker, OBS source registration, and texture upload path are unchanged.
- The poller starts lazily when the OBS-aware renderer is first used and stops cleanly when the plugin unloads.

### Runtime dependencies

- `audtool` supplies the preferred artist/title tuples and fallback title/filename data.
- Linux `/proc` is used for fallback process detection.
- `wmctrl` is used for titlebar fallback. Missing `wmctrl` does not disable song-title display when `audtool` is available.
