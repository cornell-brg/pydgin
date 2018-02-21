#=========================================================================A
# imix-sanity.py
#=========================================================================
# Quick and dirty script for instruction mix sanity checks

import pandas as pd

if __name__ == '__main__':

  df = pd.read_csv( 'imix-results.csv' )

  spmd_base = 'mimd-spmd-1-0AH'
  print 'SPMD'
  for app in df.app.unique():
    try:
      #base_spmd = df.loc[ (df.app == app) & (df.config == spmd_base),'total_insts'].iloc[0]
      #df.loc[(df.app==app) & (df.config.str.contains('spmd')),'total_insts'] = \
      #  df.loc[(df.app==app) & (df.config.str.contains('spmd')),'total_insts'] / base_spmd
      print
      print '-' * 72
      print app, ''
      print df[(df.app==app) & (df.config.str.contains('spmd'))][['total_insts']].describe().T
      print '-' * 72
      print
    except:
      continue

  wsrt_base = 'mimd-wsrt-1-0AH'
  print 'WSRT'
  for app in df.app.unique():
    try:
      #base_wsrt = df.loc[ (df.app == app) & (df.config == wsrt_base),'total_insts'].iloc[0]
      #df.loc[(df.app==app) & (df.config.str.contains('wsrt')),'total_insts'] = \
      #  df.loc[(df.app==app) & (df.config.str.contains('wsrt')),'total_insts'] / base_wsrt
      print
      print '-' * 72
      print app, ''
      print df[(df.app==app) & (df.config.str.contains('wsrt'))][['total_insts']].describe().T
      print '-' * 72
      print
    except:
      continue
