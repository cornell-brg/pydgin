#=========================================================================
# results.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : October 10th, 2017
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

def results_summary():
  resultsdir_path = '../results-small'
  with open('results-task.csv', 'w') as out:
    out.write('app,config,stat,value\n')
    subfolders = os.listdir( resultsdir_path )
    for subfolder in subfolders:
      trace_file =  resultsdir_path + '/' + subfolder + '/trace-analysis.txt'
      cmd = "grep -r -A 5 Overall %(out)s" % { 'out' : trace_file }
      try:
        lines = execute( cmd )
        stats = defaultdict(list)
        for line in lines.split('\n'):
          line = line.split(':')
          line = [ re.sub('%', '', token).rstrip() for token in line ]
          if 'savings' in line[0]:
            stats['savings'].append( line[1] )
          elif 'steps' in line[0]:
            stats['steps'].append( int(line[1]) )
          elif 'total' in line[0]:
            stats['total'].append( int(line[1]) )

        app = re.sub("-parc", '', subfolder)
        app = re.sub("-small", '', app)
        app = re.sub("-tiny", '', app)
        app = re.sub("-mtpull", '', app)

        if not app in app_short_name_dict.keys():
          continue

        # Instruction redundancy
        out.write('{},{},{},{}\n'.format(app_short_name_dict[app],'task1-maxshare','savings',stats['savings'][0]))
        out.write('{},{},{},{}\n'.format(app_short_name_dict[app],'task1-minpc','savings',stats['savings'][1]))
        out.write('{},{},{},{}\n'.format(app_short_name_dict[app],'task2-maxshare','savings',stats['savings'][2]))
        out.write('{},{},{},{}\n'.format(app_short_name_dict[app],'task2-minpc','savings',stats['savings'][3]))

        # Performance
        res_file =  resultsdir_path + '/' + subfolder + '/' + subfolder + '.out'

        cmd = 'grep -r -A 10 "Core 0 Instructions Executed in Stat Region" %(out)s' % { 'out' : res_file }
        lines = execute( cmd )
        total = 0
        serial = 0
        runtime = 0
        for line in lines.split('\n'):
          if 'Stat Region' in line:
            total = int(line.split()[-1])
          elif 'serial' in line:
            serial = int(line.split()[-1])
          elif 'runtime' in line:
            runtime = int(line.split()[-1])

        # Sanity check
        print app, total, serial+runtime+stats['total'][0], total- (serial+runtime+stats['total'][0])

        out.write('{},{},{},{}\n'.format(app_short_name_dict[app],'task1-maxshare','steps',stats['steps'][0]+serial))
        out.write('{},{},{},{}\n'.format(app_short_name_dict[app],'task1-minpc','steps',stats['steps'][1]+serial))
        out.write('{},{},{},{}\n'.format(app_short_name_dict[app],'task2-maxshare','steps',stats['steps'][2]+serial))
        out.write('{},{},{},{}\n'.format(app_short_name_dict[app],'task2-minpc','steps',stats['steps'][3]+serial))

      except:
        print "{}: Trace file not present".format( subfolder )
        continue

results_summary()
