#=========================================================================
# results-spmd.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : December 28th, 2017
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
# Global variable
#-------------------------------------------------------------------------

app_short_name_dict = {
  'pbbs-bfs-deterministicBFS'    : 'bfs-d',
  'pbbs-bfs-ndBFS'               : 'bfs-nd',
  'pbbs-csort-quickSort'         : 'qsort',
  'pbbs-csort-quickSort-1'       : 'qsort-1',
  'pbbs-csort-quickSort-2'       : 'qsort-2',
  'pbbs-csort-sampleSort'        : 'sampsort',
  'pbbs-csort-sampleSort-1'      : 'sampsort-1',
  'pbbs-csort-sampleSort-2'      : 'sampsort-2',
  'pbbs-dict-deterministicHash'  : 'dict',
  'pbbs-hull-quickHull'          : 'hull',
  'pbbs-isort-blockRadixSort'    : 'radix-1',
  'pbbs-isort-blockRadixSort-1'  : 'radix-2',
  'pbbs-knn-octTree2Neighbors'   : 'knn',
  'pbbs-mis-ndMIS'               : 'mis',
  'pbbs-nbody-parallelBarnesHut' : 'nbody',
  'pbbs-rdups-deterministicHash' : 'rdups',
  'pbbs-sa-parallelRange'        : 'sarray',
  'pbbs-st-ndST'                 : 'sptree',
  'cilk-cholesky'                : 'clsky',
  'cilk-cilksort'                : 'cilksort',
  'cilk-heat'                    : 'heat',
  'cilk-knapsack'                : 'ksack',
  'cilk-matmul'                  : 'matmul',
}

#-------------------------------------------------------------------------
# results_summary()
#-------------------------------------------------------------------------

ncores = 4
g_resultsdir_path = "../tpa-results-l0/results-small-spmd-%dc-%dl0-%dip-%ddp-%dlp-%dl-%dr"

def results_summary():

  with open('results-spmd.csv', 'w') as out:
    out.write('app,config,serial,steps,isavings,dsavings\n')
    for l0_buffer_sz in [1]:
      for ports in range( 1, ncores+1 ):
        for llfus in range( 1, ncores+1 ):
          for lockstep in range( 2 ):
            for analysis in range( 3 ):
              resultsdir_path = g_resultsdir_path % ( ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
              subfolders = os.listdir( resultsdir_path )
              for subfolder in subfolders:
                trace_file =  resultsdir_path + '/' + subfolder + '/trace-analysis.txt'
                cmd = "grep -r -A 5 Overall %(out)s" % { 'out' : trace_file }
                try:
                  app = re.sub("-parc", '', subfolder)
                  app = re.sub("-small", '', app)
                  app = re.sub("-mtpull", '', app)

                  if not app in app_short_name_dict.keys():
                    continue

                  # Performance
                  res_file =  resultsdir_path + '/' + subfolder + '/' + subfolder + '.out'
                  cmd = 'grep -r -A 35 "Serial steps in stats region =" %(res_file)s' % { 'res_file' : res_file }
                  lines = execute( cmd )
                  total = 0
                  serial = 0
                  isavings = 0
                  dsavings = 0
                  config = "spmd-%dc-%dl0-%dip-%ddp-%dlp-%dl-%dr" % ( ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
                  for line in lines.split('\n'):
                    if line != '':
                      if 'Serial steps' in line:
                        serial = int(line.split()[-1])
                      elif 'Total steps' in line:
                        total = int(line.split()[-1])
                      elif 'Redundancy in parallel regions' in line:
                        isavings = line.split()[-1]
                      elif 'Redundancy for data accesses in parallel regions' in line:
                        dsavings = line.split()[-1]

                  config = "spmd-%dc-%dl0-%dip-%ddp-%dlp-%dl-%dr" % ( ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
                  out.write('{},{},{},{},{},{}\n'.format(app_short_name_dict[app],config,serial,total,isavings,dsavings))
                except:
                  print "{}: Results file not present".format( subfolder )
                  continue

results_summary()
