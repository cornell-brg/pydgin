#=========================================================================
# app-table.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : March 13th, 2018
#
# Script to dump the app table

import re

import pandas as pd
pd.set_option('display.width', 100)

from collections import OrderedDict

from common import *
from common_configs import *

#-------------------------------------------------------------------------
# add_column
#-------------------------------------------------------------------------

def add_column( df, table, column_name, stats_label, apps_list ):
  stats = []
  for app in apps_list:
    try:
      total_insts = float(df.loc[(df.config == base_cfg) & (df.app == app),'total_insts'].iloc[0])
      insts = float(df.loc[(df.config == base_cfg) & (df.app == app),stats_label].iloc[0])
      stats.append( "{:4.2f}".format( 100*float(insts/total_insts) ) )
    except:
      # need this to skip spmd apps that don't exist
      dyn_insts.append("")
      continue
  table[column_name] = stats

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  # read the results
  df = pd.read_csv( "imix-results.csv" )

  # create and fill an empty dataframe for the table
  table = pd.DataFrame()

  # add the apps column
  apps_list = app_spmd_list
  table['Name'] = apps_list

  # collect dynamic instruction counts in millions for spmd first
  base_cfg = 'mimd-spmd-1-0AH'
  dyn_insts = []
  million = 1000000.0
  for app in apps_list:
    try:
      insts = float(df.loc[(df.config == base_cfg) & (df.app == app),'total_insts'].iloc[0])
      insts = insts/million
      dyn_insts.append( "{:4.2f}".format( insts ) )
    except:
      # need this to skip spmd apps that don't exist
      dyn_insts.append("")
      continue
  table['Dyn. Insts'] = dyn_insts

  # stats labels
  stats_labels_dict = OrderedDict()
  stats_labels_dict['integer'] = 'Integer'
  stats_labels_dict['load'] = 'Load'
  stats_labels_dict['store'] = 'Store'
  stats_labels_dict['amo'] = 'AMO'
  stats_labels_dict['mdu'] = 'MDU'
  stats_labels_dict['fpu'] = 'FPU'

  for stats_label, column_name in stats_labels_dict.iteritems():
    add_column( df, table, column_name, stats_label, apps_list )

  print table.to_latex(index=False)
