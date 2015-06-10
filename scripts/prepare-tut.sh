#!/usr/bin/env bash

# remove, mkdir and configure build dirs for tutorial preparation
echo "cleaning parc/asm_tests"
cd ../parc/asm_tests;
rm -rf build/;
mkdir build;
cd build/;
../configure --host=maven

echo "cleaning bmarks"
cd ../../../bmarks;
rm -rf build/;
mkdir build;
cd build/;
../configure --host=maven

echo "done!"
