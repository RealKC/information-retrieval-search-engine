#!/usr/bin/env bash

mkdir -p build

g++ -Wall -Werror -std=c++23 main.cpp -o build/main

build/main
