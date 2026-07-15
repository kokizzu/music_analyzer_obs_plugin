#!/usr/bin/env python3

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise SystemExit(f"check_standalone_isolation: {message}")


def main():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    plugin = (ROOT / "src" / "plugin.cpp").read_text(encoding="utf-8")
    standalone = (ROOT / "src" / "standalone.cpp").read_text(encoding="utf-8")
    renderer = (ROOT / "src" / "visualizer_renderer.cpp").read_text(encoding="utf-8")

    require("SDL2_CFLAGS" in makefile and "SDL2_LIBS" in makefile, "Makefile must define SDL flags")
    require("$(BUILD_DIR)/standalone.o" in makefile, "standalone object rule missing")
    require("$(BUILD_DIR)/standalone_bass_guitar.o" in makefile, "bass-guitar standalone object rule missing")
    require("$(SDL2_CFLAGS)" in makefile, "standalone compile rule must use SDL cflags")
    require("$(SDL2_LIBS)" in makefile, "standalone link rule must use SDL libs")
    require("MAO_STANDALONE_VERSION" in makefile, "Makefile standalone version macro missing")
    require("MAO_STANDALONE_BASS_GUITAR=1" in makefile, "Makefile bass-guitar standalone macro missing")

    plugin_rule = makefile.split("$(BUILD_DIR)/plugin.o:", 1)[1].split("\n\n", 1)[0]
    plugin_link = makefile.split("$(BUILD_DIR)/music-analyzer-obs.so:", 1)[1].split("\n\n", 1)[0]
    require("SDL2_CFLAGS" not in plugin_rule, "OBS plugin compile rule must not use SDL cflags")
    require("MAO_STANDALONE_WITH_SDL" not in plugin_rule, "OBS plugin compile rule must not set standalone macro")
    require("MAO_STANDALONE_VERSION" not in plugin_rule, "OBS plugin compile rule must not set standalone version")
    require("SDL2_LIBS" not in plugin_link, "OBS plugin link rule must not use SDL libs")
    require("standalone.o" not in plugin_link, "OBS plugin link rule must not include standalone object")

    require("#include <SDL.h>" not in plugin, "OBS plugin source must not include SDL")
    require("SDL_" not in plugin, "OBS plugin source must not call SDL")
    require("#include <SDL.h>" not in renderer, "shared renderer must not include SDL")
    require("SDL_" not in renderer, "shared renderer must not call SDL")
    require("c == 'p'" in renderer and "c == 'o'" in renderer and "c == 'w'" in renderer,
            "renderer must preserve lowercase pow chord suffix")
    require("simplify_major_minor_chord_label" in renderer,
            "sustain column must normalize to plain major/minor chords")
    require('"BASS+GUITAR"' not in renderer,
            "compact layout name should stay in the window title, not the rendered header")
    require("cpu_percent" in renderer and "free_memory_percent" in renderer and '" FREE %.0f%%"' in renderer,
            "renderer status line must expose optional CPU and free-memory metrics")

    require("#pragma GCC diagnostic push" in standalone, "standalone SDL include must be warning-guarded")
    require("#pragma GCC diagnostic pop" in standalone, "standalone SDL include guard must be closed")
    require("MAO_STANDALONE_WITH_SDL" in standalone, "standalone compile guard missing")
    close_process = standalone.split("void close_process()", 1)[1].split("\n\t}\n};", 1)[0]
    sigkill_index = close_process.find("(void)kill(pid, SIGKILL);")
    close_index = close_process.find("close(read_fd)")
    require("drain_available_stdout();" in close_process,
            "standalone ffmpeg shutdown must drain child stdout while waiting")
    require(sigkill_index >= 0 and close_index > sigkill_index,
            "standalone ffmpeg shutdown must not close stdout pipe before killing child")

    obs_cmake = cmake.split("add_library(music-analyzer-obs MODULE", 1)[1].split(")", 1)[0]
    require("src/visualizer_renderer.cpp" in obs_cmake, "CMake OBS target must use shared renderer")
    require("src/standalone.cpp" not in obs_cmake, "CMake OBS target must not include standalone source")
    require("SDL2_LIBRARIES" not in cmake.split("target_link_libraries(music-analyzer-obs", 1)[1].split(")", 1)[0],
            "CMake OBS target must not link SDL")
    require("add_music_analyzer_standalone(music-analyzer-standalone)" in cmake, "CMake standalone target missing")
    require("add_music_analyzer_standalone(music-analyzer-bass-guitar)" in cmake,
            "CMake bass-guitar standalone target missing")
    require("MAO_STANDALONE_BASS_GUITAR=1" in cmake, "CMake bass-guitar standalone macro missing")
    require("MAO_STANDALONE_VERSION" in cmake, "CMake standalone version macro missing")

    print("check_standalone_isolation: ok")


if __name__ == "__main__":
    main()
