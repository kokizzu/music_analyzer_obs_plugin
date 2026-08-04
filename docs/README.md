# Music Analyzer Documentation

## Audacious Song Title in the OBS Overlay

On Linux, the OBS plugin replaces the input/source-name text in the `MUSIC ANALYZER` header with Audacious's current song title or filename. This is OBS-only; the standalone and Android renderers keep their existing input/source labels.

### Detection and display rules

- Audacious process state is checked directly through Linux `/proc`; the process check does not spawn `pgrep` or another command.
- A lazy background poller checks Audacious metadata at most once per second. No Audacious process/window query runs in the OBS audio callback or visualizer/render thread.
- When Audacious is running, the poller reads `wmctrl -lx` and selects the most likely Audacious playback window.
- The expected titlebar format is `Artist - Album - Song title/filename`. The first two fields are removed, so only `Song title/filename` is shown.
- A two-field title such as `Artist - filename.flac` shows the second field. A plain title or filename is shown unchanged.
- Optional decorations such as ` - Audacious`, `[Audacious]`, and an `Audacious - ` prefix are removed.
- When `wmctrl` cannot expose the playback title, which can occur for native Wayland windows, the plugin falls back to `audtool current-song`, then to the basename from `audtool current-song-filename`.
- Before the first background check completes, the header shows `AUDACIOUS CHECKING`.
- When Audacious is not running, the header shows `AUDACIOUS NOT RUNNING`.
- When Audacious is running but no usable title is available, the header shows `AUDACIOUS TITLE UNAVAILABLE`.
- Titles of 34 characters or fewer remain static. Longer titles use a 34-character marquee, advance one character every 250 ms, and loop with a visible `---` separator.
- The built-in overlay font currently supports ASCII. Unsupported UTF-8 characters are replaced with `?` instead of corrupting the rendered text.

### Efficiency requirements

- Audacious process and metadata detection runs only in the background poller.
- The `/proc` process check does not create a subprocess.
- `wmctrl` and fallback `audtool` queries run at most once per second.
- The render path copies cached state under a short mutex and calculates the marquee position from elapsed time; it performs no external command or per-frame polling.
- The marquee resets only when the detected song or Audacious running state changes.
- The analyzer audio callback, analyzer ring buffer, and DSP worker are unchanged.
- The poller starts lazily when the OBS Audacious-aware renderer is first used and stops cleanly when the plugin is unloaded.

### Runtime dependencies

- Linux `/proc` is used to detect the `audacious` process.
- `wmctrl` is used for titlebar detection.
- `audtool` is the title and filename fallback. Missing `wmctrl` does not disable song-title display when `audtool` is available.
