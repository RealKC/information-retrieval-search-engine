#!/usr/bin/env bash

set -e

cd $(dirname $0)

mkdir -p build

g++ -Wall -Werror -std=c++23 -Og -g3 main.cpp -o build/main

# gdb --args build/main $1
build/main $1 
