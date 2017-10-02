# Quick and dirty script to parse results

import os
import sys
import subprocess

def execute(cmd):
  try:
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

def results_summary():
  resultsdir_path = '../results'

  with open('summary-unbounded.txt', 'w') as out:
    subfolders = os.listdir( resultsdir_path )
    for subfolder in subfolders:
      trace_file =  resultsdir_path + '/' + subfolder + '/trace-analysis.txt'
      cmd = "tail -1 %(out)s" % { 'out' : trace_file }
      lines = execute( cmd )
      out.write(subfolder+"\n")
      out.write(lines)

  resultsdir_path = '../results-bounded'
  with open('summary-bounded.txt', 'w') as out:
    subfolders = os.listdir( resultsdir_path )
    for subfolder in subfolders:
      trace_file =  resultsdir_path + '/' + subfolder + '/trace-analysis.txt'
      cmd = "tail -1 %(out)s" % { 'out' : trace_file }
      lines = execute( cmd )
      out.write(subfolder+"\n")
      out.write(lines)

  with open("summary-unbounded.txt") as xh:
    with open('summary-bounded.txt') as yh:
      with open("summary.txt","w") as zh:
        #Read first file
        xlines = xh.readlines()
        #Read second file
        ylines = yh.readlines()
        #Combine content of both lists  and Write to third file
        for line1, line2 in zip(xlines, ylines):
          zh.write("{} | {}\n".format(line1.rstrip(), line2.rstrip()))

results_summary()
