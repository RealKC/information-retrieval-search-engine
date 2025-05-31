#!/usr/bin/env bash

set -e

cd $(dirname $0)

mkdir -p build

g++ -Wall -Werror -Wno-sign-compare -std=c++23 -Og -g3 -I../../packages/bplustree/include main.cpp -o build/main

# gdb --args build/main $1 $2
# valgrind --leak-check=full build/main $1 $2
build/main $1 $2
