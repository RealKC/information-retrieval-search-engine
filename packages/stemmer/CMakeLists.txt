cmake_minimum_required(VERSION 3.15)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_core MODULE src/main.cpp src/stem.hpp src/stem.c)
install(TARGETS _core DESTINATION ${SKBUILD_PROJECT_NAME})

set_target_properties(_core PROPERTIES CXX_STANDARD 23 CXX_STANDARD_REQUIRED ON)
