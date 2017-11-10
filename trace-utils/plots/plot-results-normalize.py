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
  #('pbbs-knn-octTree2Neighbors'   , 'knn'), didn't complete for wsrt
  ('pbbs-mis-ndMIS'               , 'mis'),
  #('pbbs-nbody-parallelBarnesHut' , 'nbody'), looks like an outlier works but don't visualize
  #('pbbs-isort-blockRadixSort'    , 'radix-1'), didn't complete for spmd
  #('pbbs-isort-blockRadixSort-1'  , 'radix-2'), didn't complete for spmd
  ('pbbs-rdups-deterministicHash' , 'rdups'),
  ('pbbs-sa-parallelRange'        , 'sarray'),
  ('pbbs-st-ndST'                 , 'sptree'),
  ('pbbs-csort-quickSort'         , 'qsort'),
  ('pbbs-csort-quickSort-1'       , 'qsort-1'),
  ('pbbs-csort-quickSort-2'       , 'qsort-2'),
  ('pbbs-csort-sampleSort'        , 'sampsort'),
  ('pbbs-csort-sampleSort-1'      , 'sampsort-1'),
  ('pbbs-csort-sampleSort-2'      , 'sampsort-2'),
  ('pbbs-hull-quickHull'          , 'hull'),
  ('cilk-cholesky'                , 'clsky'),
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
  'task1-maxshare',
  'task1-minpc',
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

def parse_savings( stat, df, base_df=None ):
  data = []
  for app in app_list:
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

  opts = brg_plot.PlotOptions()
  attribute_dict = \
  {
    'show'            : False,
    'plot_type'       : 'bar',
    'figsize'         : (12.0, 8.0),
    'rotate_labels'   : False,
    'markersize'      : 8,
    'labels_fontsize' : 1,
    'legend_enabled'  : False,
  }
  for name, value in attribute_dict.iteritems():
    setattr( opts, name, value )

  opts.num_rows = 2
  opts.num_cols = 1

  # 1. plot the potential savings
  opts.data           = parse_savings( 'savings', df )
  opts.labels         = [app_list,configs]
  opts.legend_ncol    = len(configs)
  opts.title          = "Savings"
  opts.ylabel         = "Potential insn. fetch savings (%)"
  opts.rotate_labels  = True
  opts.colors         = brg_plot.colors['qualitative']
  opts.legend_enabled = True
  opts.plot_idx       = 1
  opts.legend_ncol    = 4
  opts.legend_bbox    = (0.,1.1,1.,0.1)

  # plot data
  brg_plot.add_plot( opts )

  # 2. plot the performance
  # make a copy of the baseline data used for normalization
  base_df = df[df.config == "serial"].copy()

  opts.data           = parse_savings( 'steps', df, base_df )
  opts.labels         = [app_list,configs]
  opts.legend_ncol    = len(configs)
  opts.title          = "Timesteps"
  opts.ylabel         = "Dyn Insts"
  opts.rotate_labels  = True
  opts.colors         = brg_plot.colors['qualitative']
  opts.legend_enabled = False
  opts.plot_idx       = 2
  opts.file_name      = 'results.pdf'

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
