#=========================================================================
# common.py
#=========================================================================
# List of all appliations and the short names for paper format. The data
# structures present in this file are mean't to be accessed by other plot
# scripts.
#
# NOTE: The app list is populated based on the current apps enabled and as
# present in the doit automation.
#
# Author : Shreesha Srinath
# Date   : January 2nd, 2017

from collections import OrderedDict

#-------------------------------------------------------------------------
# Global variables
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

# dictionary which shows the baseline normalization map
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

# list of application kernels t
app_list = app_short_name_dict.values()

# list of files required to parse all the results
file_list = [
  'results-spmd.csv',
  'results-wsrt.csv',
  'results-serial.csv',
]
