#============================================================================
# resubmit.py
#============================================================================
# Quick and dirty script for resubmitting failed jobs on cluster
# NOTE: Need to find out why this happens in the first place

import os
import re
import subprocess
import sys

sys.path.extend(['../plots'])
from common import *

#-------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------

def execute(cmd):
  try:
    print cmd
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":

  runtime               = 'spmd'
  runtime_custom_string = '-mt'
  runtime_string        = '-parc-small'
  custom_list = []
  other_list = []
  with open( '../plots/final-resubmit.csv', 'r' ) as in_file:
    for line in in_file:
      if runtime in line:
        line = line.split(',')
        app = line[0]
        task = line[1]
        task = re.sub('conj-', 'conjoined-', task)
        task = task.split('-')
        task[-3] = 'limit-1' if task[-3] == '1' else 'limit-1000'
        task = '-'.join( task )
        task = 'sim-' + task
        for key,val in app_short_name_dict.iteritems():
          if val == app:
            if 'pbbs' in key or 'cilk' in key:
              #print task + ":" + key + runtime_string
              other_list.append( task + ":" + key + runtime_string )
            else:
              #print task + ":" + key + runtime_custom_string
              custom_list.append( task + ":" + key + runtime_custom_string )

  for item in other_list:
    #print item
    cmd = 'doit ' + item
    execute( cmd )
