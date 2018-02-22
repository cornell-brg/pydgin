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
# app_short_name_dict
#-------------------------------------------------------------------------

# map showing the shorter names used.
# NOTE: This data-structure is an OrderedDict which means the order here
# determines the order of all the plots
app_short_name_dict = OrderedDict([

  # custom
  ('bilateral'                    , 'bilateral'),
  ('dct8x8m'                      , 'dct8x8m'),
  ('mriq'                         , 'mriq'),
  ('rgb2cmyk'                     , 'rgb2cmyk'),
  ('strsearch'                    , 'strsearch'),
  ('uts'                          , 'uts'),
  #('dither'                       , 'dither'), # debug simt configs
  #('viterbi'                      , 'viterbi'), # debug simt configs

  # pbbs
  ('pbbs-bfs-deterministicBFS'    , 'bfs-d'),
  ('pbbs-bfs-ndBFS'               , 'bfs-nd'),
  ('pbbs-dict-deterministicHash'  , 'dict'),
  ('pbbs-mis-ndMIS'               , 'mis'),
  ('pbbs-rdups-deterministicHash' , 'rdups'),
  ('pbbs-sa-parallelRange'        , 'sarray'),
  ('pbbs-csort-quickSort'         , 'qsort'),
  ('pbbs-csort-quickSort-1'       , 'qsort-1'),
  ('pbbs-csort-quickSort-2'       , 'qsort-2'),
  ('pbbs-csort-sampleSort'        , 'sampsort'),
  ('pbbs-csort-sampleSort-1'      , 'sampsort-1'),
  ('pbbs-csort-sampleSort-2'      , 'sampsort-2'),
  ('pbbs-hull-quickHull'          , 'hull'),
  #('pbbs-knn-octTree2Neighbors'   , 'knn'),
  #('pbbs-nbody-parallelBarnesHut' , 'nbody'),
  #('pbbs-st-ndST'                 , 'sptree'), # debug simt configs
  #('pbbs-isort-blockRadixSort'    , 'radix-1'),
  #('pbbs-isort-blockRadixSort-1'  , 'radix-2'),

  # cilk
  ('cilk-cilksort'                , 'cilksort'),
  ('cilk-heat'                    , 'heat'),
  ('cilk-knapsack'                , 'ksack'),
  ('cilk-matmul'                  , 'matmul'),
  #('cilk-cholesky'                , 'clsky'),
])

# list of application kernels
app_list = app_short_name_dict.values()

# spmd app list
filter_spmd_dict = OrderedDict([
  # pbbs
  ('pbbs-csort-quickSort'         , 'qsort'),
  ('pbbs-csort-quickSort-1'       , 'qsort-1'),
  ('pbbs-csort-quickSort-2'       , 'qsort-2'),
  ('pbbs-csort-sampleSort'        , 'sampsort'),
  ('pbbs-csort-sampleSort-1'      , 'sampsort-1'),
  ('pbbs-csort-sampleSort-2'      , 'sampsort-2'),
  # cilk
  ('cilk-cilksort'                , 'cilksort'),
  ('cilk-heat'                    , 'heat'),
  ('cilk-knapsack'                , 'ksack'),
  ('cilk-matmul'                  , 'matmul'),
])

filter_spmd_list = filter_spmd_dict.values()
app_spmd_list = []
for app in app_list:
  if app not in filter_spmd_list:
    app_spmd_list.append( app )

#-------------------------------------------------------------------------
# normalize_map
#-------------------------------------------------------------------------
# shows the which serial implementation to use for normalization

# dictionary which shows the baseline normalization map
app_normalize_map = {
  'vvmult'     : 'ubmark-tpa-vvmult-scalar',
  'bilateral'  : 'bilateral-scalar',
  'dct8x8m'    : 'dct8x8m-scalar',
  'dither'     : 'dither-scalar',
  'mriq'       : 'mriq-scalar',
  'rgb2cmyk'   : 'rgb2cmyk-scalar',
  'strsearch'  : 'strsearch-scalar',
  'viterbi'    : 'viterbi-scalar',
  'uts'        : 'uts-scalar',
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

#-------------------------------------------------------------------------
# app_groups
#-------------------------------------------------------------------------
# names of apps based on custom, pbbs, cilk app groups

app_group_custom = OrderedDict([
  # custom
  ('bilateral'                    , 'bilateral'),
  ('dct8x8m'                      , 'dct8x8m'),
  ('mriq'                         , 'mriq'),
  ('rgb2cmyk'                     , 'rgb2cmyk'),
  ('strsearch'                    , 'strsearch'),
  ('uts'                          , 'uts'),
])
app_custom_list = app_group_custom.values()

app_group_pbbs = OrderedDict([
  # pbbs
  ('pbbs-bfs-deterministicBFS'    , 'bfs-d'),
  ('pbbs-bfs-ndBFS'               , 'bfs-nd'),
  ('pbbs-dict-deterministicHash'  , 'dict'),
  ('pbbs-mis-ndMIS'               , 'mis'),
  ('pbbs-rdups-deterministicHash' , 'rdups'),
  ('pbbs-sa-parallelRange'        , 'sarray'),
  ('pbbs-csort-quickSort'         , 'qsort'),
  ('pbbs-csort-quickSort-1'       , 'qsort-1'),
  ('pbbs-csort-quickSort-2'       , 'qsort-2'),
  ('pbbs-csort-sampleSort'        , 'sampsort'),
  ('pbbs-csort-sampleSort-1'      , 'sampsort-1'),
  ('pbbs-csort-sampleSort-2'      , 'sampsort-2'),
  ('pbbs-hull-quickHull'          , 'hull'),
  #('pbbs-knn-octTree2Neighbors'   , 'knn'),
  #('pbbs-nbody-parallelBarnesHut' , 'nbody'),
  #('pbbs-st-ndST'                 , 'sptree'), # debug simt configs
  #('pbbs-isort-blockRadixSort'    , 'radix-1'),
  #('pbbs-isort-blockRadixSort-1'  , 'radix-2'),
])
app_pbbs_list = app_group_pbbs.values()

app_group_cilk = OrderedDict([
  # cilk
  ('cilk-cilksort'                , 'cilksort'),
  ('cilk-heat'                    , 'heat'),
  ('cilk-knapsack'                , 'ksack'),
  ('cilk-matmul'                  , 'matmul'),
  #('cilk-cholesky'                , 'clsky'),
])
app_cilk_list = app_group_cilk.values()

#-------------------------------------------------------------------------
# Misc
#-------------------------------------------------------------------------

# list of files required to parse all the results
file_list = [
  'results-spmd.csv',
  'results-wsrt.csv',
  'results-serial.csv',
]

insn_file_list = [
  'insn-mix-spmd.csv',
  'insn-mix-wsrt.csv',
]
