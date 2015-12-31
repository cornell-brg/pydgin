#!/usr/bin/env python
#=========================================================================
# get-test-list.py
#=========================================================================
# Generates a list of tests in a directory

usage = """Usage:
  ./get-test-list.py dir [extension]
Prints the list of tests in a python-friendly fashion in dir. Extension
can be specified to determine which files are tests (which will be
stripped). By default, the extension is ".d"."""

import os
import sys

if len( sys.argv ) < 2:
  print usage
  sys.exit(1)

dir = sys.argv[1]
ext = sys.argv[2] if len( sys.argv ) >= 3 else ".d"
ext_len = len( ext )

ext_files  = filter( lambda f : f.endswith( ext ), os.listdir( dir ) )
test_files = sorted( map( lambda f : f[:-ext_len], ext_files ) )

print "tests = [\n ",
print ",\n  ".join( map( '"{}"'.format, test_files ) )
print "]"

