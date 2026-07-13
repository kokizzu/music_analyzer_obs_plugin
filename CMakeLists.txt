cmake_minimum_required(VERSION 3.16)

project(music_analysis_obs_plugin VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBOBS REQUIRED libobs)
pkg_get_variable(LIBOBS_INCLUDEDIR libobs includedir)

set(LIBOBS_CXX_FLAGS ${LIBOBS_CFLAGS_OTHER})
list(REMOVE_ITEM LIBOBS_CXX_FLAGS "-std=gnu17" "-Werror")
set(LOCAL_SIMDE_INCLUDE "${CMAKE_CURRENT_SOURCE_DIR}/build/deps/usr/include")
set(LOCAL_SIMDE_INCLUDE_DIRS)
if(EXISTS "${LOCAL_SIMDE_INCLUDE}/simde/x86/sse2.h")
    list(APPEND LOCAL_SIMDE_INCLUDE_DIRS "${LOCAL_SIMDE_INCLUDE}")
endif()

add_library(music-analysis-obs MODULE
    src/analyzer.cpp
    src/plugin.cpp
)

target_include_directories(music-analysis-obs PRIVATE
    ${LIBOBS_INCLUDE_DIRS}
    ${LOCAL_SIMDE_INCLUDE_DIRS}
    ${LIBOBS_INCLUDEDIR}/obs
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_compile_options(music-analysis-obs PRIVATE
    ${LIBOBS_CXX_FLAGS}
    -Wall
    -Wextra
)
target_link_directories(music-analysis-obs PRIVATE ${LIBOBS_LIBRARY_DIRS})
target_link_libraries(music-analysis-obs PRIVATE ${LIBOBS_LIBRARIES} pthread)
set_target_properties(music-analysis-obs PROPERTIES PREFIX "")

add_executable(analyzer_smoke tests/analyzer_smoke.cpp src/analyzer.cpp)
target_include_directories(analyzer_smoke PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(analyzer_smoke PRIVATE -Wall -Wextra)

enable_testing()
add_test(NAME analyzer_smoke COMMAND analyzer_smoke)
