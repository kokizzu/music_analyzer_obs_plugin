# Music Analyzer Documentation

## Audacious Song Title in the OBS Overlay

On Linux, the OBS plugin replaces the input/source-name text in the `MUSIC ANALYZER` header with Audacious's cleaned **Title** field. Audacious Artist and Album metadata are deliberately ignored. This is OBS-only; the standalone and Android renderers keep their existing input/source labels.

### Detection and display rules

- The normal fast path asks only `audtool current-song-tuple-data title` for the dedicated Title field.
- Artist and Album are ignored. In the reported setup, Artist is `music-yt`, Album is `flac_output`, and the wanted `GMS Live - Sambut Sang Raja ...` text is already entirely inside Title.
- For example, `GMS Live - Sambut Sang Raja (Official Music Video) [drKw4ogAqsAJ]` becomes `GMS Live - Sambut Sang Raja [drKw4ogAqsAJ]`.
- Presentation-only groups are removed selectively. Recognized forms include `(Live)`, `(Official Video)`, `(Official Music Video)`, `(Official Video Music)`, `(Official Lyric Video)`, `(Official Lyrics Video)`, official-audio/visualizer equivalents, and the same labels in square brackets.
- Ordinary descriptive groups are preserved. For example, `OCEANS (Pop-Punk Cover) [OVvN_YzWEgc]` remains unchanged.
- YouTube ID groups are preserved with their brackets. Trailing transport markers such as `music-yt` and `.music-yt` are removed, so `OCEANS (Official Video Music) [OVvN_YzWEgc] music-yt` becomes `OCEANS [OVvN_YzWEgc]`.
- If the dedicated Title tuple is unavailable, the plugin checks Audacious through Linux `/proc`, reads `wmctrl -lx`, and selects the most likely Audacious playback window.
- The customized titlebar fallback accepts `playlist - output - artist - song title/filename`; the first two fields are discarded and the remaining artist/title portion is retained.
- Optional Audacious application decorations such as ` - Audacious`, `[Audacious]`, and an `Audacious - ` prefix are removed.
- When neither the tuple nor a usable window title is available, including native Wayland windows hidden from `wmctrl`, the plugin falls back to `audtool current-song`, then to the basename from `audtool current-song-filename`.
- Before the first background check completes, the header shows `AUDACIOUS CHECKING`.
- When Audacious is not running, the header shows `AUDACIOUS NOT RUNNING`.
- When Audacious is running but no usable title is available, the header shows `AUDACIOUS TITLE UNAVAILABLE`.
- Long titles advance one UTF-8 code point every 250 ms and loop with a visible separator. Multibyte characters are never split.
- Japanese and other Unicode text is rasterized directly into the analyzer's existing RGBA pixel buffer through the system Pango/Cairo runtime. No nested OBS source, source-registration change, or alternate texture path is used.
- If the runtime Unicode libraries are unavailable, the renderer reruns the original bitmap path as a safety fallback; failure of the title layer cannot remove the keyboard, guitar, drums, or status display.

### Build paths

- `make install-user` is supported through the root `GNUmakefile`, which includes the existing `Makefile` and adds the Audacious and Unicode-title objects plus OBS-only renderer redirection.
- OBS source registration and final texture drawing remain untouched.
- Pango and Cairo are loaded dynamically at runtime, so no additional development headers are required to compile the plugin.
- CMake builds include the same sources and link through the platform dynamic-loader library.
- The Makefile path forces `plugin.o` to rebuild after this integration is pulled, preventing a stale object from being reinstalled.
- Run `make test-audacious-title` for metadata-cleanup and UTF-8 marquee tests.
- Run `make test-audacious-unicode` for an actual Japanese text rasterization test.

### Efficiency requirements

- Audacious metadata detection runs only in a lazy background poller, at most once per second.
- The usual tuple path launches one short `audtool` Title query per poll and skips `/proc` plus `wmctrl` when successful.
- `/proc`, `wmctrl`, and the additional fallback commands run only when the Title tuple path fails.
- The render path uses only the cached metadata and current marquee window; it performs no external metadata command.
- Unicode rendering touches only the small header region in the existing CPU pixel buffer.
- The analyzer audio callback, analyzer ring buffer, DSP worker, OBS source registration, and texture upload path are unchanged.
- The poller starts lazily when the OBS-aware renderer is first used and stops cleanly when the plugin unloads.

### Runtime dependencies

- `audtool` supplies the preferred Title tuple and fallback title/filename data.
- The normal Pop!_OS/Ubuntu desktop Pango, PangoCairo, Cairo, and GLib runtime libraries provide Unicode rasterization. The plugin loads their versioned shared libraries dynamically.
- An installed Japanese-capable system font, such as Noto Sans CJK, is required for Japanese glyphs. Pango automatically chooses an appropriate fallback font.
- Linux `/proc` is used for fallback process detection.
- `wmctrl` is used for titlebar fallback. Missing `wmctrl` does not disable song-title display when `audtool` is available.
