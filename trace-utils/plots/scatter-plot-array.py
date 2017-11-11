#=========================================================================
# plot-results.py
#=========================================================================
# Quick and super dirty script to summarize results

import brg_plot

import re
import sys

import pandas as pd

from collections import OrderedDict

#-------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------

app_short_name_dict = OrderedDict([
  ('pbbs-bfs-deterministicBFS'    , 'bfs-d'),
  ('pbbs-bfs-ndBFS'               , 'bfs-nd'),
  ('pbbs-dict-deterministicHash'  , 'dict'),
  #('pbbs-knn-octTree2Neighbors'   , 'knn'),    # didn't complete for wsrt
  ('pbbs-mis-ndMIS'               , 'mis'),
  #('pbbs-nbody-parallelBarnesHut' , 'nbody'),  # fails for wsrt
  ('pbbs-rdups-deterministicHash' , 'rdups'),
  ('pbbs-sa-parallelRange'        , 'sarray'),
  ('pbbs-st-ndST'                 , 'sptree'),
  ('pbbs-isort-blockRadixSort'    , 'radix-1'), # didn't complete for spmd
  ('pbbs-isort-blockRadixSort-1'  , 'radix-2'), # didn't complete for spmd
  ('pbbs-csort-quickSort'         , 'qsort'),
  ('pbbs-csort-quickSort-1'       , 'qsort-1'),
  ('pbbs-csort-quickSort-2'       , 'qsort-2'),
  ('pbbs-csort-sampleSort'        , 'sampsort'),
  ('pbbs-csort-sampleSort-1'      , 'sampsort-1'),
  ('pbbs-csort-sampleSort-2'      , 'sampsort-2'),
  ('pbbs-hull-quickHull'          , 'hull'),
  #('cilk-cholesky'                , 'clsky'),  # fails for wsrt
  ('cilk-cilksort'                , 'cilksort'),
  ('cilk-heat'                    , 'heat'),
  ('cilk-knapsack'                , 'ksack'),
  ('cilk-matmul'                  , 'matmul'),
])

app_normalize_map = {
  'sampsort'   : 'pbbs-csort-serialSort',
  'sampsort-1' : 'pbbs-csort-serialSort-1',
  'sampsort-2' : 'pbbs-csort-serialSort-2',
  'qsort'      : 'pbbs-csort-serialSort',
  'qsort-1'    : 'pbbs-csort-serialSort-1',
  'qsort-2'    : 'pbbs-csort-serialSort-2',
  'radix-1'    : 'pbbs-isort-serialRadixSort',
  'radix-2'    : 'pbbs-isort-serialRadixSort-1',
  'nbody'      : 'pbbs-nbody-serialBarnesHut',
  'bfs-d'      : 'pbbs-bfs-serialBFS',
  'bfs-nd'     : 'pbbs-bfs-serialBFS',
  'dict'       : 'pbbs-dict-serialHash',
  'knn'        : 'pbbs-knn-serialNeighbors',
  'sarray'     : 'pbbs-sa-serialKS',
  'sptree'     : 'pbbs-st-serialST',
  'rdups'      : 'pbbs-rdups-serialHash',
  'mis'        : 'pbbs-mis-serialMIS',
  'hull'       : 'pbbs-hull-serialHull',
  'matmul'     : 'cilk-matmul',
  'heat'       : 'cilk-heat',
  'ksack'      : 'cilk-knapsack',
  'cilksort'   : 'cilk-cilksort',
  'clsky'      : 'cilk-cholesky',
}

app_list = app_short_name_dict.values()

configs = [
  'spmd-maxshare',
  'spmd-minpc',
  'wsrt-maxshare',
  'wsrt-minpc',
  'task2-maxshare',
  'task2-minpc',
]

file_list = [
  'results-spmd.csv',
  'results-wsrt.csv',
  'results-task.csv',
  'results-serial.csv',
]

#-------------------------------------------------------------------------
# parse
#-------------------------------------------------------------------------

def parse_savings( stat, app, df, base_df=None ):
  data = []
  if stat == 'steps':
    ts, = base_df[(base_df.app == app_normalize_map[app]) & (base_df.config == 'serial') & (base_df.stat == stat)]['value']
  temp = []
  for config in configs:
    try:
      val, = df[(df.config == config) & (df.app == app) & (df.stat == stat)]['value']
      if stat == 'steps':
        temp.append(ts/float(val))
      else:
        temp.append(val)
    except:
      temp.append(0)
  data.append( temp )
  return data

#-------------------------------------------------------------------------
# plot
#-------------------------------------------------------------------------

def plot( df ):

  #-----------------------------------------------------------------------
  # Plot savings
  #-----------------------------------------------------------------------

  base_df = df[df.config == "serial"].copy()
  opts = brg_plot.PlotOptions()
  attribute_dict = \
  {
    'show'            : False,
    'plot_type'       : 'scatter',
    'figsize'         : (16.0, 20.0),
    'rotate_labels'   : False,
    'markersize'      : 50,
    'labels_fontsize' : 1,
    'legend_enabled'  : False,
    'ylabel'          : 'Inst. Redundancy',
    'xlabel'          : 'Speedup',
  }
  for name, value in attribute_dict.iteritems():
    setattr( opts, name, value )

  opts.num_cols = 4
  opts.num_rows = len( app_list ) / 4

  for index,app in enumerate( app_list ):
    steps = parse_savings( 'steps', app, df, base_df )
    savings = parse_savings( 'savings', app, df )
    data = []
    for x,y in zip(steps,savings):
      temp = []
      for c,d in zip(x,y):
        temp.append([c, d])
      data.append(temp)
    data = map(list,zip(*data))

    opts.data           = data
    opts.labels         = [[],configs]
    opts.legend_ncol    = len(configs)
    opts.rotate_labels  = True
    opts.title          = app
    opts.colors         = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#f77f00', '#a65628', '#f781bf', '#999999']
    opts.plot_idx       = index+1
    if index == len(app_list) - 1:
      opts.legend_enabled = True
      opts.legend_ncol    = 3
      #opts.legend_bbox    = (-2.7,8.7,1.,0.1) # fig ( 8, 10)
      opts.legend_bbox    = (-1.85,6.3,1.,0.1) # fig (16, 20)
      opts.file_name      = 'scatter.pdf'

    # plot data
    brg_plot.add_plot( opts )

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  df_list = []
  for res_file in file_list:
    df_list.append( pd.read_csv( res_file ) )
  df = pd.concat(df_list)
  df.to_csv('combined.csv',index=False)
  plot( df )
