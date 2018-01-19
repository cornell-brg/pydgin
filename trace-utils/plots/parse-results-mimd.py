#=========================================================================
# parse-results-mimd.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : January 18th, 2018
#
# Quick and dirty script to parse results for wsrt similarity on the
# abstract MIMD architecture

import os
import sys
import re
import subprocess

import pandas as pd

from collections import OrderedDict

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

# map showing the shorter names used.
# NOTE: This data-structure is an OrderedDict which means the order here
# determines the order of all the plots
app_short_name_dict = OrderedDict([
  ('pbbs-bfs-deterministicBFS'    , 'bfs-d'),
  ('pbbs-bfs-ndBFS'               , 'bfs-nd'),
  ('pbbs-dict-deterministicHash'  , 'dict'),
  #('pbbs-knn-octTree2Neighbors'   , 'knn'),
  ('pbbs-mis-ndMIS'               , 'mis'),
  #('pbbs-nbody-parallelBarnesHut' , 'nbody'),
  ('pbbs-rdups-deterministicHash' , 'rdups'),
  ('pbbs-sa-parallelRange'        , 'sarray'),
  ('pbbs-st-ndST'                 , 'sptree'),
  #('pbbs-isort-blockRadixSort'    , 'radix-1'),
  #('pbbs-isort-blockRadixSort-1'  , 'radix-2'),
  ('pbbs-csort-quickSort'         , 'qsort'),
  ('pbbs-csort-quickSort-1'       , 'qsort-1'),
  ('pbbs-csort-quickSort-2'       , 'qsort-2'),
  ('pbbs-csort-sampleSort'        , 'sampsort'),
  ('pbbs-csort-sampleSort-1'      , 'sampsort-1'),
  ('pbbs-csort-sampleSort-2'      , 'sampsort-2'),
  ('pbbs-hull-quickHull'          , 'hull'),
  #('cilk-cholesky'                , 'clsky'),
  ('cilk-cilksort'                , 'cilksort'),
  ('cilk-heat'                    , 'heat'),
  ('cilk-knapsack'                , 'ksack'),
  ('cilk-matmul'                  , 'matmul'),
])

g_resultsdir_path = "../results-wsrt-similarity-limit-%d"

#-------------------------------------------------------------------------
# summarize
#-------------------------------------------------------------------------

def summarize():

  data = []
  #for limit in [1,50,100,250,500,1000]:
  for limit in [1,250]:
    resultsdir_path = g_resultsdir_path % limit
    subfolders = os.listdir( resultsdir_path )
    for subfolder in subfolders:
      try:
        app = re.sub("-parc", '', subfolder)
        app = re.sub("-small", '', app)
        app = re.sub("-mtpull", '', app)

        if not app in app_short_name_dict.keys():
          continue

        res_file =  resultsdir_path + '/' + subfolder + '/' + subfolder + '.out'
        cmd = 'grep -r -A 35 "Serial steps in stats region =" %(res_file)s' % { 'res_file' : res_file }
        lines = execute( cmd )
        total = 0
        isavings = 0
        for line in lines.split('\n'):
          if line != '':
            if 'Total steps' in line:
              total = int(line.split()[-1])
            elif 'Redundancy in parallel regions' in line:
              isavings = line.split()[-1]

        config = "mimd-limit-%d" % limit
        data.append([app_short_name_dict[app],config,total,isavings])
      except:
        print "limit-{} {}: Results file not present".format( limit, subfolder )
        continue

  columns = ['app','config','steps','isavings']
  df = pd.DataFrame(data,columns=columns)
  return df

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  df = summarize()

  base_df = df[df.config == "mimd-limit-1"].copy()

  for app in app_short_name_dict.values():
    ts = base_df.loc[base_df.app == app,['steps']].iloc[0]
    df.loc[df.app == app, ['steps']] = \
      float(ts)/df.loc[df.app == app, ['steps']]

  configs = df.config.unique()
  print "{:^21s}".format("kernel") + ("{:^21s}"*len(configs)).format(*configs)
  for app in app_short_name_dict.values():
    out = "{:^18s}".format(app)
    for config in configs:
      perf = df.loc[(df.app == app) & (df.config == config), ['steps']].iloc[0]
      red  = df.loc[(df.app == app) & (df.config == config), ['isavings']].iloc[0]
      out += "{:^10.2f} {:^10.2f}".format( float(perf), float(red) )
    print out

  df.to_csv('test.csv',index=False)
