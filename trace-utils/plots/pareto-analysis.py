#=========================================================================
# pareto_analysis.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : February 25th, 2018
#
# Script that is useful for pareto analysis

import pandas as pd
pd.set_option('display.width', 1000)

from scipy.stats.mstats import gmean

from common import *
from common_configs import *

#-------------------------------------------------------------------------
# is_pareto_front()
#-------------------------------------------------------------------------
# reference:
# http://hinnefe2.github.io/python/tools/2015/09/21/mario-kart.html

def is_pareto_front(row, stats, xlabel, ylabel):
  x = row[xlabel]
  y = row[ylabel]

  # look for points with the same y value but smaller x value
  is_min_x = stats.loc[stats[ylabel]==y].max()[xlabel] >= x
  # look for points with the same x value but smaller y value
  is_min_y = stats.loc[stats[xlabel]==x].max()[ylabel] >= y

  # look for points that are smaller in both x and y
  is_min_xy = len(stats.loc[(stats[xlabel]<x) & (stats[ylabel]<y)])==0

  return is_min_x and is_min_y and is_min_xy

#-------------------------------------------------------------------------
# normalize results
#-------------------------------------------------------------------------
# computes normalized delay and normalized work for each config

def normalize_results( df ):
  df['normalized_delay'] = df['steps']
  df['normalized_work']  = df['unique_work']
  for runtime in ['spmd','wsrt']:
    base_cfg = g_mimd_base_str % runtime
    for app in app_list:
      try:
        base_steps = float(df.loc[(df.app == app) & (df.config == base_cfg), 'steps'].iloc[0])
        df.loc[(df.app==app) & df.config.str.contains(runtime), 'normalized_delay'] = \
          df.loc[(df.app==app) & df.config.str.contains(runtime), 'normalized_delay'] / base_steps
        base_work = float(df.loc[(df.app == app) & (df.config == base_cfg), 'total_work'].iloc[0])
        df.loc[(df.app==app) & df.config.str.contains(runtime), 'normalized_work'] = \
          df.loc[(df.app==app) & df.config.str.contains(runtime), 'normalized_work'] * 100/ base_work
      except:
        continue
  return df

#-------------------------------------------------------------------------
# per_app
#-------------------------------------------------------------------------

def per_app( df, group_dict, configs_dict ):
  for runtime in ['spmd','wsrt']:
    rt_df = df.loc[df.config.str.contains(runtime)]
    for app in app_list:
      if app not in rt_df.app.unique():
        continue
      data = []
      for group, configs_list in group_dict.iteritems():
        for cfg in configs_list:
          if runtime not in cfg:
            continue
          delay = rt_df.loc[(rt_df.app==app) & (rt_df.config==cfg), 'normalized_delay'].iloc[0]
          work  = rt_df.loc[(rt_df.app==app) & (rt_df.config==cfg), 'normalized_work'].iloc[0]
          data.append( [cfg, delay, work] )

      columns   = ['config','delay','work']
      stats     = pd.DataFrame(data,columns=columns)
      is_pareto = stats.apply(lambda row: is_pareto_front(row, stats, 'delay', 'work'), axis=1)

      pareto_configs = [configs_dict[x] for x in stats.loc[is_pareto,'config'].tolist()]
      print "#"  + '-'*73
      print "# " + app + '-' + runtime
      print "#"  + '-'*73, "\n"
      for cfg in pareto_configs:
        print "{:32s}".format( cfg )
      print

#-------------------------------------------------------------------------
# geo_mean
#-------------------------------------------------------------------------

def geo_mean( df, group_dict, configs_dict ):
  for runtime in ['spmd','wsrt']:
    rt_df = df.loc[df.config.str.contains(runtime)]
    data = []
    for group, configs_list in group_dict.iteritems():
      for cfg in configs_list:
        if cfg not in rt_df.config.unique():
          continue
        delay = gmean(rt_df.loc[rt_df.config==cfg, 'normalized_delay'])
        work  = gmean(rt_df.loc[rt_df.config==cfg, 'normalized_work'])
        data.append( [cfg, delay, work] )

    columns   = ['config','delay','work']
    stats     = pd.DataFrame(data,columns=columns)
    is_pareto = stats.apply(lambda row: is_pareto_front(row, stats, 'delay', 'work'), axis=1)

    pareto_configs = [configs_dict[x] for x in stats.loc[is_pareto,'config'].tolist()]
    print "#"  + '-'*73
    print "# " + runtime
    print "#"  + '-'*73, "\n"
    for cfg in pareto_configs:
      print "{:32s}".format( cfg )
    print

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  # skip limited-lockstep and adaptive_hints
  basic = True

  # runtime
  runtime = 'spmd'

  # read the results
  df = pd.read_csv( "sim-results.csv" )

  # only select non-zero values as zero is missing data at the moment
  df = df[df!=0]

  # normalize the results for each runtime
  df = normalize_results( df )

  # get the configs seperated based on the uarch
  group_dict   = populate_configs( basic )
  configs_dict = format_config_names( basic )

  # per app pareto optimal configs
  per_app( df, group_dict, configs_dict )

  # geo-mean pareto optimal configs
  geo_mean( df, group_dict, configs_dict )
