#=========================================================================A
# sanity-checks.py
#=========================================================================
# Quick and dirty script for sanity checks

import pandas as pd

pd.set_option('display.width', 100)

if __name__ == '__main__':

  df = pd.read_csv( 'sim-results.csv' )

  spmd_base = 'mimd-spmd-1-0AH'
  print '=' * 100
  print 'SPMD'
  print '=' * 100
  for app in df.app.unique():
    try:
      base_spmd = df.loc[ (df.app == app) & (df.config == spmd_base),'total_insts'].iloc[0]
      base_steps = df.loc[ (df.app == app) & (df.config == spmd_base),'steps'].iloc[0]
      df.loc[(df.app==app) & (df.config.str.contains('spmd')),'total_insts'] = \
        df.loc[(df.app==app) & (df.config.str.contains('spmd')),'total_insts'] / base_spmd
      df.loc[(df.app==app) & (df.config.str.contains('spmd')),'steps'] = \
        df.loc[(df.app==app) & (df.config.str.contains('spmd')),'steps'] / base_steps
      print
      print '-' * 100
      print app, ''
      print df[(df.app==app) & (df.config.str.contains('spmd'))][['total_insts']].describe().T
      print df[(df.app==app) & (df.config.str.contains('spmd'))][['steps']].describe().T
      print '-' * 100
      print
    except:
      continue

  wsrt_base = 'mimd-wsrt-1-0AH'
  print '=' * 100
  print 'WSRT'
  print '=' * 100
  for app in df.app.unique():
    try:
      base_wsrt = df.loc[ (df.app == app) & (df.config == wsrt_base),'total_insts'].iloc[0]
      base_steps = df.loc[ (df.app == app) & (df.config == wsrt_base),'steps'].iloc[0]
      df.loc[(df.app==app) & (df.config.str.contains('wsrt')),'total_insts'] = \
        df.loc[(df.app==app) & (df.config.str.contains('wsrt')),'total_insts'] / base_wsrt
      df.loc[(df.app==app) & (df.config.str.contains('wsrt')),'steps'] = \
        df.loc[(df.app==app) & (df.config.str.contains('wsrt')),'steps'] / base_steps
      print
      print '-' * 100
      print app, ''
      print df[(df.app==app) & (df.config.str.contains('wsrt'))][['total_insts']].describe().T
      print df[(df.app==app) & (df.config.str.contains('wsrt'))][['steps']].describe().T
      print '-' * 100
      print
    except:
      continue
