#=========================================================================
# plot-results.py
#=========================================================================
# Quick and super dirty script to summarize results

import brg_plot
import re

import pandas as pd

#-------------------------------------------------------------------------
# parse
#-------------------------------------------------------------------------

def parse_savings( stat, app_names, configs, df ):
  data = []
  for app in app_names:
    temp = []
    for config in configs:
      val, = df[(df.config == config) & (df.app == app) & (df.stat == stat)]['value']
      temp.append(val)
    data.append( temp )
  return data

#-------------------------------------------------------------------------
# plot
#-------------------------------------------------------------------------

def plot( df ):

  app_names = df['app'].unique().tolist()
  configs = df['config'].unique().tolist()

  #-----------------------------------------------------------------------
  # Plot savings
  #-----------------------------------------------------------------------

  opts = brg_plot.PlotOptions()
  attribute_dict = \
  {
    'show'            : False,
    'plot_type'       : 'bar',
    'figsize'         : (12.0, 4.0),
    'rotate_labels'   : False,
    'ylabel'          : "Potential insn. fetch savings (%)",
    'markersize'      : 8,
    'labels_fontsize' : 1,
    'legend_enabled'  : True,
  }
  for name, value in attribute_dict.iteritems():
    setattr( opts, name, value )

  opts.data          = parse_savings('savings',app_names,configs,df)
  opts.labels        = [app_names,configs]
  opts.legend_ncol   = len(configs)
  opts.file_name     = "savings.pdf"
  opts.rotate_labels = True
  opts.colors        = brg_plot.colors['qualitative']

  # plot data
  brg_plot.add_plot( opts )

  #-----------------------------------------------------------------------
  # Plot steps
  #-----------------------------------------------------------------------

  opts = brg_plot.PlotOptions()
  attribute_dict = \
  {
    'title'           : "Performance overhead in timsteps",
    'show'            : False,
    'plot_type'       : 'bar',
    'figsize'         : (12.0, 4.0),
    'rotate_labels'   : False,
    'ylabel'          : "Normalized to maxshare",
    'markersize'      : 8,
    'labels_fontsize' : 1,
    'legend_enabled'  : True,
    'normalize_line'  : 1,
  }
  for name, value in attribute_dict.iteritems():
    setattr( opts, name, value )

  # Plot savings
  data = parse_savings('steps',app_names,configs,df)
  norm_data = []
  for d in data:
    base = d[0]
    norm_data.append([float(x/d[0]) for x in d])

  opts.data          = norm_data
  opts.labels        = [app_names,configs]
  opts.legend_ncol   = len(configs)
  opts.file_name     = "steps.pdf"
  opts.rotate_labels = True
  opts.colors        = brg_plot.colors['qualitative']
  opts.legend_bbox   = (.15, 1)

  # plot data
  brg_plot.add_plot( opts )

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  dataframe = pd.read_csv("results.csv")
  plot(dataframe)
