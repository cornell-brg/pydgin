#!/usr/bin/env python

import os
import subprocess

assembler = "arm-unknown-linux-uclibcgnueabi-gcc -nostdlib"

# try creating a build dir

cmd = "mkdir -p build"
print cmd
subprocess.check_call( cmd, shell=True )

# build the binaries

for asm_file in filter( lambda s : s.endswith( ".S" ), os.listdir( "." ) ):

  elf_file = asm_file[:-2]

  cmd = "{assembler} {asm_file} -o build/{elf_file}".format( **locals() )
  print cmd
  subprocess.check_call( cmd, shell=True )

