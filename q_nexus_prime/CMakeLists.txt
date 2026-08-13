cmake_minimum_required(VERSION 3.20)
project(QNexusPrime LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization Flags
if(MSVC)
    add_compile_options(/O2 /Zi /W4 /execution-character-set:utf-8)
else()
    add_compile_options(-O3 -g -Wall -Wextra -pthread)
endif()

# Directories
include_directories(include)

# Source Files
set(CORE_SOURCES
    src/core/half_edge.cpp
    src/core/remesher.cpp
    src/core/baker.cpp
)

# Core Library
add_library(q_nexus_core STATIC ${CORE_SOURCES})

# Tests
enable_testing()
add_executable(test_manifold tests/test_manifold.cpp)
target_link_libraries(test_manifold q_nexus_core)
add_test(NAME ManifoldTest COMMAND test_manifold)

add_executable(test_remesh tests/test_remesh.cpp)
target_link_libraries(test_remesh q_nexus_core)
add_test(NAME RemeshTest COMMAND test_remesh)

add_executable(test_bake tests/test_bake.cpp)
target_link_libraries(test_bake q_nexus_core)
add_test(NAME BakeTest COMMAND test_bake)

add_executable(test_industrial tests/test_industrial_v6.cpp)
target_link_libraries(test_industrial q_nexus_core)
add_test(NAME IndustrialTest COMMAND test_industrial)
