#============================================================================
# cluser-resubmit.py
#============================================================================
# Quick and dirty script for resubmitting failed jobs on cluster
# NOTE: Need to find out why this happens in the first place

import os
import re
import subprocess

#-------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------

def execute(cmd):
  print cmd
  try:
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":

  cmd = 'find .. -name "*.out" -exec grep -Lr DONE {} \;'
  lines = execute( cmd )
  failed_jobs = []
  for line in lines.split():
    line = re.sub("results-small", "sim-pydgin", line)
    line = line.split("/")
    failed_jobs.append( line[1] + ":" + line[2] )

  resubmit_cmd = "doit  " + ' '.join( failed_jobs )
  execute( resubmit_cmd )
