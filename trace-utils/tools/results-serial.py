#=========================================================================
# results-serial.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : January 2nd, 2018
#
# Quick and dirty script to parse results

import os
import sys
import re
import subprocess

from collections import defaultdict

#-------------------------------------------------------------------------
# Utility Function
#-------------------------------------------------------------------------

def execute(cmd):
  try:
    #print cmd
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    return err

#-------------------------------------------------------------------------
# results_summary()
#-------------------------------------------------------------------------

def results_summary():
  resultsdir_path = '../results-serial-small'
  with open('results-serial.csv', 'w') as out:
    out.write('app,config,serial,steps,isavings,dsavings\n')
    subfolders = os.listdir( resultsdir_path )
    for subfolder in subfolders:
      res_file =  resultsdir_path + '/' + subfolder + '/' + subfolder + '.out'
      cmd = 'grep -r -A 5 "Core 0 Instructions Executed in Stat Region" %(out)s' % { 'out' : res_file }
      try:
        lines = execute( cmd )
        for line in lines.split('\n'):
          if 'Stat Region' in line:
            total = int(line.split()[-1])

        app = re.sub("-parc", '', subfolder)
        app = re.sub("-small", '', app)
        app = re.sub("-tiny", '', app)
        app = re.sub("-mtpull", '', app)

        out.write('{},{},{},{},{},{}\n'.format(app,'serial',0,total,0,0))
      except:
        print "{}: Trace file not present".format( subfolder )
        continue

results_summary()
