# Audacious overlay integration

## Audacious Song Title in the OBS Overlay

On Linux, the OBS plugin replaces the input/source-name text in the `MUSIC ANALYZER` header with Audacious's cleaned **Title** field. Audacious Artist and Album metadata are deliberately ignored. This is OBS-only; the standalone and Android renderers keep their existing input/source labels.

### Detection and display rules

- The normal fast path asks only `audtool current-song-tuple-data title` for the dedicated Title field.
- Artist and Album are ignored. In the reported setup, Artist is `music-yt`, Album is `flac_output`, and the wanted `GMS Live - Sambut Sang Raja ...` text is already entirely inside Title.
- The exact fallback format is `Artist - Album - Title (extra) [youtubeID]`. The first two fields are discarded, and only the cleaned `Title [youtubeID]` portion is rendered.
- For example, `music-yt - flac_output - GMS Live - Sambut Sang Raja (Official Music Video) [drKw4ogAqsAJ]` becomes `GMS Live - Sambut Sang Raja [drKw4ogAqsAJ]`.
- Presentation-only groups are removed selectively. Recognized forms include `(Live)`, `(Official Video)`, `(Official Music Video)`, `(Official Video Music)`, `(Official Lyric Video)`, `(Official Lyrics Video)`, official-audio/visualizer equivalents, and the same labels in square brackets.
- Ordinary descriptive groups are preserved. For example, `OCEANS (Pop-Punk Cover) [OVvN_YzWEgc]` remains unchanged.
- YouTube ID groups are preserved with their brackets. Trailing transport markers such as `music-yt` and `.music-yt` are removed, so `OCEANS (Official Video Music) [OVvN_YzWEgc] music-yt` becomes `OCEANS [OVvN_YzWEgc]`.
- If the dedicated Title tuple is unavailable, the plugin checks Audacious through Linux `/proc`, reads `wmctrl -lx`, and selects the most likely Audacious playback window.
- Optional Audacious application decorations such as ` - Audacious`, `[Audacious]`, and an `Audacious - ` prefix are removed.
- When neither the tuple nor a usable window title is available, including native Wayland windows hidden from `wmctrl`, the plugin falls back to `audtool current-song`, then to the basename from `audtool current-song-filename`.
- Before the first background check completes, the header shows `AUDACIOUS CHECKING`.
- When Audacious is not running, the header shows `AUDACIOUS NOT RUNNING`.
- When Audacious is running but no usable title is available, the header shows `AUDACIOUS TITLE UNAVAILABLE`.
- The title starts immediately after the existing `MUSIC ANALYZER` heading at x=316.
- The muted/silent microphone marker starts at `width - 52`. The title ends 8 pixels before it, so the title region is `width - 376` pixels wide. At the default 960-pixel source width, the title receives the full 584-pixel region from x=316 through x=899.
- Long Unicode titles scroll by pixels across that entire region at 52 pixels per second and loop with an 80-pixel gap. They are no longer limited to a fixed 34-character window.
- Japanese and other Unicode text is rasterized directly into the analyzer's existing RGBA pixel buffer through the system Pango/Cairo runtime. No nested OBS source, source-registration change, or alternate texture path is used.
- If the runtime Unicode libraries are unavailable, the renderer reruns the original bitmap path as a safety fallback; failure of the title layer cannot remove the keyboard, guitar, drums, or status display.

### Build paths

- `make install-user` is supported through the root `GNUmakefile`, which includes the existing `Makefile` and adds the Audacious and Unicode-title objects plus OBS-only renderer redirection.
- OBS source registration and final texture drawing remain untouched.
- Pango and Cairo are loaded dynamically at runtime, so no additional development headers are required to compile the plugin.
- CMake builds include the same sources and link through the platform dynamic-loader library.
- The Makefile path forces `plugin.o` to rebuild after this integration is pulled, preventing a stale object from being reinstalled.
- Run `make test-audacious-title` for metadata-cleanup and UTF-8 marquee tests.
- Run `make test-audacious-unicode` for Japanese rasterization, full-width clipping, and scrolling coverage.

### Efficiency requirements

- Audacious metadata detection runs in a lazy background poller once per second. Each wait is measured from the start of the previous probe, so a slow probe is followed immediately by the next attempt instead of adding another full-second delay.
- The usual tuple path launches one short `audtool` Title query per poll and skips `/proc` plus `wmctrl` when successful.
- `/proc`, `wmctrl`, and the additional fallback commands run only when the Title tuple path fails.
- The render path uses only cached metadata and elapsed time; it performs no external metadata command.
- Unicode rendering touches only the small title region in the existing CPU pixel buffer.
- The analyzer audio callback, analyzer ring buffer, DSP worker, OBS source registration, and texture upload path are unchanged.
- The poller starts lazily when the OBS-aware renderer is first used and stops cleanly when the plugin unloads.

### Runtime dependencies

- `audtool` supplies the preferred Title tuple and fallback title/filename data.
- The normal Pop!_OS/Ubuntu desktop Pango, PangoCairo, Cairo, and GLib runtime libraries provide Unicode rasterization. The plugin loads their versioned shared libraries dynamically.
- An installed Japanese-capable system font, such as Noto Sans CJK, is required for Japanese glyphs. Pango automatically chooses an appropriate fallback font.
- Linux `/proc` is used for fallback process detection.
- `wmctrl` is used for titlebar fallback. Missing `wmctrl` does not disable song-title display when `audtool` is available.
