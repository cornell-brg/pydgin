# Quick and dirty script to parse results

import os
import sys
import re
import subprocess

def execute(cmd):
  try:
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

def common_entries(*dcts):
  for i in set(dcts[0]).intersection(*dcts[1:]):
    yield (i,) + tuple(d[i] for d in dcts)

def results_summary():
  resultsdir_path = '../results'
  with open('summary.txt', 'w') as out:
    subfolders = os.listdir( resultsdir_path )
    for subfolder in subfolders:
      trace_file =  resultsdir_path + '/' + subfolder + '/trace-analysis.txt'
      cmd = "tail -1 %(out)s" % { 'out' : trace_file }
      lines = execute( cmd )
      out.write(subfolder+":")
      out.write(lines)

results_summary()
