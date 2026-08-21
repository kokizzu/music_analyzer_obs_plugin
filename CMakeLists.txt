cmake_minimum_required(VERSION 3.16)

project(music_analyzer_obs_plugin VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBOBS REQUIRED libobs)
pkg_get_variable(LIBOBS_INCLUDEDIR libobs includedir)

set(LIBOBS_CXX_FLAGS ${LIBOBS_CFLAGS_OTHER})
list(REMOVE_ITEM LIBOBS_CXX_FLAGS "-std=gnu17" "-Werror")
set(LOCAL_SIMDE_INCLUDE "${CMAKE_CURRENT_SOURCE_DIR}/build/deps/usr/include")
set(PERMISSIVE_BEAT_TRACKER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/beat_and_tempo_tracking")
file(GLOB PERMISSIVE_BEAT_TRACKER_SOURCES "${PERMISSIVE_BEAT_TRACKER_DIR}/src/*.c")

add_library(music-analyzer-obs MODULE
    src/analyzer.cpp
    src/beat_this_sidecar_client.cpp
    ${PERMISSIVE_BEAT_TRACKER_SOURCES}
    src/audacious_title.cpp
    src/audacious_overlay.cpp
    src/unicode_title_renderer.cpp
    src/visualizer_renderer.cpp
    src/plugin.cpp
)

add_executable(beat_this_sidecar_client_tests tests/beat_this_sidecar_client.cpp src/beat_this_sidecar_client.cpp)
target_include_directories(beat_this_sidecar_client_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_compile_options(beat_this_sidecar_client_tests PRIVATE -Wall -Wextra)

# Keep Audacious title replacement exclusive to the Linux OBS plugin. Source
# registration and final texture drawing retain the original implementation.
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set_property(SOURCE src/plugin.cpp APPEND PROPERTY COMPILE_OPTIONS
        "-include"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/audacious_plugin_redirect.hpp"
    )
endif()

target_include_directories(music-analyzer-obs PRIVATE
    ${LIBOBS_INCLUDE_DIRS}
    ${LOCAL_SIMDE_INCLUDE}
    ${LIBOBS_INCLUDEDIR}/obs
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${PERMISSIVE_BEAT_TRACKER_DIR}
)
target_compile_options(music-analyzer-obs PRIVATE
    ${LIBOBS_CXX_FLAGS}
    -Wall
    -Wextra
)
target_link_directories(music-analyzer-obs PRIVATE ${LIBOBS_LIBRARY_DIRS})
target_link_libraries(music-analyzer-obs PRIVATE ${LIBOBS_LIBRARIES} pthread ${CMAKE_DL_LIBS})
set_target_properties(music-analyzer-obs PROPERTIES PREFIX "")

add_executable(analyzer_smoke tests/analyzer_smoke.cpp src/analyzer.cpp ${PERMISSIVE_BEAT_TRACKER_SOURCES})
target_include_directories(analyzer_smoke PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/tests
    ${PERMISSIVE_BEAT_TRACKER_DIR}
)
target_compile_options(analyzer_smoke PRIVATE -Wall -Wextra)

add_executable(analyzer_cases tests/analyzer_cases.cpp src/analyzer.cpp ${PERMISSIVE_BEAT_TRACKER_SOURCES})
target_include_directories(analyzer_cases PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/tests
    ${PERMISSIVE_BEAT_TRACKER_DIR}
)
target_compile_options(analyzer_cases PRIVATE -Wall -Wextra)

add_executable(fret_control_tests tests/fret_control.cpp src/fret_control.cpp)
target_include_directories(fret_control_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_compile_options(fret_control_tests PRIVATE -Wall -Wextra)

add_executable(audacious_title_tests tests/audacious_title.cpp src/audacious_title.cpp)
target_include_directories(audacious_title_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_compile_options(audacious_title_tests PRIVATE -Wall -Wextra)

add_executable(unicode_title_renderer_tests tests/unicode_title_renderer.cpp src/unicode_title_renderer.cpp)
target_include_directories(unicode_title_renderer_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_compile_options(unicode_title_renderer_tests PRIVATE -Wall -Wextra)
target_link_libraries(unicode_title_renderer_tests PRIVATE ${CMAKE_DL_LIBS})

pkg_check_modules(SDL2 sdl2)
if(SDL2_FOUND)
    string(TIMESTAMP STANDALONE_BUILD_TIME "%Y.%m%d.%H%M")
    execute_process(
        COMMAND git rev-parse --short HEAD
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        OUTPUT_VARIABLE STANDALONE_BUILD_COMMIT
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    if(NOT STANDALONE_BUILD_COMMIT)
        set(STANDALONE_BUILD_COMMIT unknown)
    endif()
    set(STANDALONE_VERSION "${STANDALONE_BUILD_TIME}.${STANDALONE_BUILD_COMMIT}")

    function(add_music_analyzer_standalone target_name)
        add_executable(${target_name}
            src/analyzer.cpp
            ${PERMISSIVE_BEAT_TRACKER_SOURCES}
            src/visualizer_renderer.cpp
            src/standalone.cpp
        )
        target_include_directories(${target_name} PRIVATE
            ${SDL2_INCLUDE_DIRS}
            ${CMAKE_CURRENT_SOURCE_DIR}/src
            ${PERMISSIVE_BEAT_TRACKER_DIR}
        )
        target_compile_definitions(${target_name} PRIVATE MAO_STANDALONE_WITH_SDL=1)
        target_compile_definitions(${target_name} PRIVATE MAO_STANDALONE_VERSION="${STANDALONE_VERSION}")
        target_compile_options(${target_name} PRIVATE
            ${SDL2_CFLAGS_OTHER}
            -Wall
            -Wextra
        )
        target_link_directories(${target_name} PRIVATE ${SDL2_LIBRARY_DIRS})
        target_link_libraries(${target_name} PRIVATE ${SDL2_LIBRARIES} pthread m)
    endfunction()

    add_music_analyzer_standalone(music-analyzer-standalone)
    add_music_analyzer_standalone(music-analyzer-bass-guitar)
    target_compile_definitions(music-analyzer-bass-guitar PRIVATE MAO_STANDALONE_BASS_GUITAR=1)
endif()

enable_testing()
add_test(NAME analyzer_smoke COMMAND analyzer_smoke)
add_test(NAME analyzer_cases COMMAND analyzer_cases)
add_test(NAME fret_control_tests COMMAND fret_control_tests)
add_test(NAME audacious_title_tests COMMAND audacious_title_tests)
add_test(NAME unicode_title_renderer_tests COMMAND unicode_title_renderer_tests)
add_test(NAME beat_this_sidecar_client_tests COMMAND beat_this_sidecar_client_tests ${CMAKE_CURRENT_SOURCE_DIR}/tests/fake_beat_this_sidecar.py)
if(SDL2_FOUND)
    add_test(NAME standalone_self_test COMMAND music-analyzer-standalone --self-test)
    set_tests_properties(standalone_self_test PROPERTIES
        ENVIRONMENT "SDL_VIDEODRIVER=dummy;SDL_AUDIODRIVER=dummy"
    )
    add_test(NAME standalone_bass_guitar_self_test COMMAND music-analyzer-bass-guitar --self-test)
    set_tests_properties(standalone_bass_guitar_self_test PROPERTIES
        ENVIRONMENT "SDL_VIDEODRIVER=dummy;SDL_AUDIODRIVER=dummy"
    )
endif()
