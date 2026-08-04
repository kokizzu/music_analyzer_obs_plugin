# Music Analyzer Documentation

## Audacious Song Title in the OBS Overlay

On Linux, the OBS plugin replaces the input/source-name text in the `MUSIC ANALYZER` header with Audacious's current `Artist - Song title`. This is OBS-only; the standalone and Android renderers keep their existing input/source labels.

### Detection and display rules

- The normal fast path asks `audtool current-song-tuple-data artist` and `audtool current-song-tuple-data title` for dedicated metadata fields. This avoids depending on a customized or truncated titlebar such as `playlist - output - artist - song title`.
- The displayed value combines the available fields as `Artist - Song title`; if either field is missing, the available field is shown by itself.
- Presentation-only groups are removed selectively. Recognized suffixes include `(Live)`, `(Official Video)`, `(Official Music Video)`, `(Official Lyric Video)`, `(Official Lyrics Video)`, official-audio/visualizer equivalents, and the same labels in square brackets.
- Ordinary descriptive groups are preserved. For example, `OCEANS (Pop-Punk Cover) [OVvN_YzWEgc]` remains exactly unchanged, and video-ID groups are not removed.
- If the dedicated title tuple is unavailable, the plugin checks Audacious through Linux `/proc`, reads `wmctrl -lx`, and selects the most likely Audacious playback window.
- The titlebar fallback accepts `Artist - Album - Song title/filename`, a two-field `Artist - filename.flac`, or a plain title/filename.
- Optional Audacious application decorations such as ` - Audacious`, `[Audacious]`, and an `Audacious - ` prefix are removed.
- When neither the tuple nor a usable window title is available, including native Wayland windows hidden from `wmctrl`, the plugin falls back to `audtool current-song`, then to the basename from `audtool current-song-filename`.
- Before the first background check completes, the header shows `AUDACIOUS CHECKING`.
- When Audacious is not running, the header shows `AUDACIOUS NOT RUNNING`.
- When Audacious is running but no usable title is available, the header shows `AUDACIOUS TITLE UNAVAILABLE`.
- The OBS header uses a private FreeType text source with a Japanese-capable system font selected through `fontconfig`. UTF-8 titles such as `愛昧ショコラーテ -PandaBoYremix- [0qomiyjPNDc]` are preserved and rendered as Unicode instead of being replaced with `?`.
- Titles wider than the available header area scroll smoothly by pixels and loop with a visible gap. Scrolling never slices UTF-8 byte sequences.

### Build paths

- `make install-user` is supported through the root `GNUmakefile`, which includes the existing `Makefile` and adds the Audacious sources plus OBS-only renderer/draw redirection.
- CMake builds include the same Audacious sources and redirection.
- The Makefile path forces `plugin.o` to rebuild after this integration is pulled, preventing a stale pre-Audacious object from being reinstalled.
- Run `make test-audacious-title` for focused metadata cleanup and UTF-8 marquee tests.

### Efficiency requirements

- Audacious metadata detection runs only in a lazy background poller, at most once per second.
- The usual tuple path launches short `audtool` queries per poll and skips `/proc` plus `wmctrl` when successful.
- `/proc`, `wmctrl`, and the additional fallback commands run only when the tuple-title path fails.
- The FreeType source is updated only when the displayed metadata changes.
- The render path reads cached metadata, clips the title to the header area, and calculates the pixel scroll offset from elapsed time; it performs no external command or per-frame metadata polling.
- The analyzer audio callback, analyzer ring buffer, and DSP worker are unchanged.
- The poller and private text source start lazily when the OBS overlay is first rendered and are released when the plugin unloads.

### Runtime dependencies

- `audtool` supplies the preferred artist/title tuples and fallback title/filename data.
- OBS's standard `Text (FreeType 2)` module provides Unicode rendering.
- `fontconfig`/`fc-match` selects an installed font suitable for Japanese text. Install a Japanese font such as Noto Sans CJK if the system has no Japanese-capable font.
- Linux `/proc` is used for fallback process detection.
- `wmctrl` is used for titlebar fallback. Missing `wmctrl` does not disable song-title display when `audtool` is available.
