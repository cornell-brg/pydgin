#=========================================================================
# process_data.py
#=========================================================================
# Common functions for plots

import pandas as pd

#-------------------------------------------------------------------------
# process_data
#-------------------------------------------------------------------------

def process_data( prefix_str, base_str, config_list, speedup, savings ):
  # read the raw dataframe
  all_results_df = pd.read_csv( "sim-results.csv" )
  df = all_results_df[all_results_df.config.isin(config_list)].copy()

  # new dataframe for parsed stats
  stats = pd.DataFrame()

  #-----------------------------------------------------------------------
  # collect savings vs. work
  #-----------------------------------------------------------------------
  if savings:
    stats['app']      = df.apply( lambda row: row.app,    axis=1)
    stats['config']   = df.apply( lambda row: row.config, axis=1)
    stats['steps']    = df.apply( lambda row: row.steps,  axis=1)
    stats['imem']     = df.apply( lambda row:
                          100.0*(row.total_iaccess-row.unique_iaccess)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
    stats['frontend'] = df.apply( lambda row:
                          100.0*(row.total_frontend-row.unique_frontend)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
    stats['dmem']     = df.apply( lambda row:
                          100.0*(row.total_daccess-row.unique_daccess)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
    stats['backend']  = df.apply( lambda row:
                          100.0*(row.total_execute-row.unique_execute)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
    stats['total']    = df.apply( lambda row:
                          100.0*(row.total_work-row.unique_work)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
  else:
    stats['app']      = df.apply( lambda row: row.app,    axis=1)
    stats['config']   = df.apply( lambda row: row.config, axis=1)
    stats['steps']    = df.apply( lambda row: row.steps,  axis=1)
    stats['imem']     = df.apply( lambda row:
                          100.0*(row.unique_iaccess)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
    stats['frontend'] = df.apply( lambda row:
                          100.0*(row.unique_frontend)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
    stats['dmem']     = df.apply( lambda row:
                          100.0*(row.unique_daccess)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
    stats['backend']  = df.apply( lambda row:
                          100.0*(row.unique_execute)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
    stats['total']    = df.apply( lambda row:
                          100.0*(row.unique_work)/row.total_work if row.total_work != 0 else float('nan'),
                          axis=1)
  #-----------------------------------------------------------------------

  # get the baseline dataframe for baseline
  base_str = prefix_str + base_str
  base_df = stats[stats.config == base_str].copy()

  #-----------------------------------------------------------------------
  # loop through configs and calculate norm. speedup or execution-time
  #-----------------------------------------------------------------------
  # speedup
  if speedup:
    for app in df.app.unique():
      try:
        # baseline
        ts, = base_df[base_df.app == app]['steps']
        # update steps to speedup inplace
        stats.loc[stats.app == app, 'steps'] = float(ts) / stats.loc[stats.app == app, 'steps']
      except:
        continue
  # execution-time
  else:
    for app in df.app.unique():
      try:
        # baseline
        ts, = base_df[base_df.app == app]['steps']
        # update steps to speedup inplace
        stats.loc[stats.app == app, ['steps']] =  stats.loc[ stats.app == app, ['steps']] / float(ts)
      except:
        continue
  #-----------------------------------------------------------------------

  # replace any value that is zero with float 'nan' to skip plotting
  stats[stats==0] = float('nan')

  # save the results
  stats.to_csv('%s-results.csv' % base_str, index=False)

  #-----------------------------------------------------------------------
  # Sanity check
  for app in df.app.unique():
    try:
      print app,
      base_insts = df.loc[ (df.app == app) & (df.config == base_str),'total_insts'].iloc[0]
      df.loc[df.app == app, 'total_insts'] = df.loc[df.app==app,'total_insts'] / base_insts
      print (df.loc[df.app == app, 'total_insts'].describe()[['mean','std']].to_frame().T)
    except:
      continue
  #-----------------------------------------------------------------------

  return stats
