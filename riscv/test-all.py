#!/usr/bin/env python
# Usage:
#  ./test-all.py <dir for tests>

import glob
import sys
import subprocess

in_dir = "/Users/berkin/work/tmp/riscv/riscv-tests/isa/"
if len( sys.argv ) > 1:
  in_dir = sys.argv[1]

print "looking for tests in", in_dir

dumps = glob.glob( in_dir + "/*.dump" )

for dump in dumps:
  bin_name = dump[:-5]
  try:
    out = subprocess.check_output( ["python", "riscv-sim.py", bin_name],
                                   stderr=subprocess.STDOUT )
  except subprocess.CalledProcessError as e:
    out = e.output

  out_str = "Error"
  if "Pass!" in out:
    out_str = "Passed"
  elif "Fail!" in out:
    out_str = "Failed"
  test_name = bin_name[ bin_name.rfind('/')+1 : ]
  print "Test {} \t {}".format( test_name, out_str )
