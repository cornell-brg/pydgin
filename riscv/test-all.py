#!/usr/bin/env python

usage = """Usage:
  ./test-all.py <options>
Options:
  --help, -h          Print this help message
  --interp <interp>   Use the specified interpreter instead of interpreted
                      Pydgin
  --test-dir <dir>    Find tests in dir
"""

import glob
import sys
import subprocess

in_dir = "/Users/berkin/work/tmp/riscv/riscv-tests/isa/"
interp = None
if "--help" in sys.argv or "-h" in sys.argv:
  print usage
  sys.exit(0)
if "--interp" in sys.argv:
  interp = sys.argv[ sys.argv.index( "--interp" ) + 1 ]
if "--test-dir" in sys.argv:
  in_dir = sys.argv[ sys.argv.index( "--test-dir" ) + 1 ]

if interp:
  print "using interpreter:", interp
else:
  print "using interpreted pydgin"
print "looking for tests in", in_dir

dumps = glob.glob( in_dir + "/*.dump" )

num_tests  = 0
num_passed = 0
num_failed = 0
num_error  = 0

for dump in sorted( dumps ):
  bin_name = dump[:-5]
  try:
    out = subprocess.check_output( interp.split() + ["--test", bin_name] if interp else
                                   ["python", "../riscv/riscv-sim.py", "--test", bin_name],
                                   stderr=subprocess.STDOUT )
  except subprocess.CalledProcessError as e:
    out = e.output

  num_tests += 1

  if "Pass!" in out:
    out_str = "pass"
    num_passed += 1
  elif "Fail!" in out:
    out_str = "FAILED"
    num_failed += 1
  else:
    out_str = "ERROR"
    num_error += 1
  test_name = bin_name[ bin_name.rfind('/')+1 : ]
  print "Test {:<20} {}".format( test_name, out_str )

print "Number of tests: {} passed: {} failed: {} error: {}" \
    .format( num_tests, num_passed, num_failed, num_error  )

# return non-zero value if we had any failures or errors
if num_failed > 0 or num_error > 0:
  sys.exit( 1 )

