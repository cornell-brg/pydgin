#=========================================================================
# tpa-scatter-plots.py
#=========================================================================
# Script creates scatter subplots for all the configurations where the
# rows vary the fixed instruction and data bandwidth while the columns vary
# the llfu bandwidth. In each subplot the variations of the reconvergence
# scheme, l0-buffer-sz, and lockstep execution values are varied. The
# script is fairly automated but will need minimal changes as required for
# a given design-space. Currently, there are two options available:
#
#  In the main function
#
#   per_app_plot : toggle the value to obtain scatter plots for each app
#   spmd, wsrt   : toggle the variables to plot spmd or wsrt data
#   isavings     : toggle to plot inst vs. data redundancy
#
# Author : Shreesha Srinath
# Date   : January 2nd, 2018

import brg_plot

import re
import math
import sys
import pandas as pd

from common import *

#-------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------

g_config_str = "%s-%dc-%dl0-%dip-%ddp-%dlp-%dl-%dr"

g_ncores = 4

#-------------------------------------------------------------------------
# plot_all()
#-------------------------------------------------------------------------
# NOTE: Each data-point is a list of lists where each nested list
# represents a unique configuration and each configuration list is in turn
# a nested list of x,y points for the scatter plot
#
# Example:
#  data = [
#    [[1,1],[2,2]], # group 1
#    [[3,3],[4,4]], # group 2
#   ]

def plot_all( opts, df, spmd=True, wsrt=True, isavings=True ):

  opts.num_cols = 4
  opts.num_rows = 4

  # select a set of configs
  index = 0
  for l0_buffer_sz in [1]:
    for ports in range( 1, g_ncores+1 ):
      for llfus in range( 1, g_ncores+1 ):
        configs = []
        labels = []

        if spmd:
          for lockstep in range( 2 ):
            for analysis in range( 3 ):
              config = g_config_str % ( 'spmd', g_ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
              configs.append( config )
              labels.append( 'spmd-%dc-%dl0-%dl-%dr' % ( g_ncores, l0_buffer_sz, lockstep, analysis ) )

        if wsrt:
          for lockstep in range( 2 ):
            for analysis in range( 3 ):
              config = g_config_str % ( 'wsrt', g_ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
              configs.append( config )
              labels.append( 'wsrt-%dc-%dl0-%dl-%dr' % ( g_ncores, l0_buffer_sz, lockstep, analysis ) )

        data = []
        for config in configs:
          temp = []
          for app in  app_list:
            try:
              speedup  = df[(df.config == config) & (df.app == app)].iloc[0]['speedup']
              if isavings:
                savings = df[(df.config == config) & (df.app == app)].iloc[0]['isavings']
              else:
                savings = df[(df.config == config) & (df.app == app)].iloc[0]['dsavings']
              temp.append( [speedup, savings] )
            except:
              temp.append( [float('nan')]*2 )
          data.append( temp )

        opts.data           = data
        opts.labels         = [[],labels]
        opts.legend_ncol    = len(configs)
        opts.rotate_labels  = True
        opts.plot_idx       = index+1
        opts.colors         = brg_plot.colors['unique20']
        opts.title          = '(%dip-%ddp,%dlp)' % ( ports, ports, llfus )

        if (index+1) % opts.num_cols == 0:
          opts.legend_enabled = True
          opts.legend_ncol    = len(configs)/3
          opts.legend_bbox    = (-1.8,1.1,1.,0.1)
        else:
          opts.legend_enabled = False
        if index == opts.num_cols*opts.num_rows - 1:
          opts.file_name       = 'scatter-all.pdf'
          opts.subplots_hspace = 0.5
          opts.fig.text(0.5, 0, 'Speedup', ha='center', fontsize=14)
          if isavings:
            opts.fig.text(-0.02, 0.5, 'Inst. Redundancy', va='center', rotation='vertical', fontsize=14)
          else:
            opts.fig.text(-0.02, 0.5, 'Data. Redundancy', va='center', rotation='vertical', fontsize=14)

        # plot data
        brg_plot.add_plot( opts )
        index = index + 1

#-------------------------------------------------------------------------
# plot_per_app()
#-------------------------------------------------------------------------
# NOTE: Each data-point is a list of lists where each nested list
# represents a unique configuration and each configuration list is in turn
# a nested list of x,y points for the scatter plot
#
# Example:
#  data = [
#    [[1,1],[2,2]], # group 1
#    [[3,3],[4,4]], # group 2
#   ]

def plot_per_app( app, opts, df, spmd=True, wsrt=True, isavings=True ):

  opts.num_cols = 4
  opts.num_rows = 4

  # select a set of configs
  index = 0
  for l0_buffer_sz in [1]:
    for ports in range( 1, g_ncores+1 ):
      for llfus in range( 1, g_ncores+1 ):
        configs = []
        labels = []

        if spmd:
          for lockstep in range( 2 ):
            for analysis in range( 3 ):
              config = g_config_str % ( 'spmd', g_ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
              configs.append( config )
              labels.append( 'spmd-%dc-%dl0-%dl-%dr' % ( g_ncores, l0_buffer_sz, lockstep, analysis ) )

        if wsrt:
          for lockstep in range( 2 ):
            for analysis in range( 3 ):
              config = g_config_str % ( 'wsrt', g_ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
              configs.append( config )
              labels.append( 'wsrt-%dc-%dl0-%dl-%dr' % ( g_ncores, l0_buffer_sz, lockstep, analysis ) )

        data = []
        for config in configs:
          try:
            speedup  = df[(df.config == config) & (df.app == app)].iloc[0]['speedup']
            if isavings:
              savings = df[(df.config == config) & (df.app == app)].iloc[0]['isavings']
            else:
              savings = df[(df.config == config) & (df.app == app)].iloc[0]['dsavings']
            data.append( [[speedup, savings]] )
          except:
            data.append( [[float('nan')]*2] )

        opts.data           = data
        opts.labels         = [[],labels]
        opts.legend_ncol    = len(configs)
        opts.rotate_labels  = True
        opts.plot_idx       = index+1
        opts.colors         = brg_plot.colors['unique20']
        opts.title          = '(%dip-%ddp,%dlp)' % ( ports, ports, llfus )

        if (index+1) % opts.num_cols == 0:
          opts.legend_enabled = True
          opts.legend_ncol    = len(configs)/3
          opts.legend_bbox    = (-1.8,1.1,1.,0.1)
        else:
          opts.legend_enabled = False
        if index == opts.num_cols*opts.num_rows - 1:
          opts.file_name       = '%(app)s-scatter.pdf' % { 'app' : app }
          opts.subplots_hspace = 0.5
          opts.fig.text(0.5, 0, 'Speedup', ha='center', fontsize=14)
          if isavings:
            opts.fig.text(-0.02, 0.5, 'Inst. Redundancy', va='center', rotation='vertical', fontsize=14)
          else:
            opts.fig.text(-0.02, 0.5, 'Data. Redundancy', va='center', rotation='vertical', fontsize=14)
          opts.fig.text(0.5, 1.05, app, ha='center', fontsize=14)

        # plot data
        brg_plot.add_plot( opts )
        index = index + 1

#-------------------------------------------------------------------------
# plot
#-------------------------------------------------------------------------

def plot( df, per_app_plot, spmd, wsrt, isavings ):

  #-----------------------------------------------------------------------
  # scatter plot
  #-----------------------------------------------------------------------

  if per_app_plot:
    for app in  app_list:
      # create plot options dict
      opts = brg_plot.PlotOptions()
      attribute_dict = \
      {
        'show'            : False,
        'plot_type'       : 'scatter',
        'figsize'         : (16.0, 16.0),
        'rotate_labels'   : False,
        'markersize'      : 50,
        'labels_fontsize' : 1,
        'legend_enabled'  : False,
      }
      for name, value in attribute_dict.iteritems():
        setattr( opts, name, value )

      plot_per_app( app, opts, df, spmd, wsrt, isavings )
  else:
    # create plot options dict
    opts = brg_plot.PlotOptions()
    attribute_dict = \
    {
      'show'            : False,
      'plot_type'       : 'scatter',
      'figsize'         : (16.0, 16.0),
      'rotate_labels'   : False,
      'markersize'      : 50,
      'labels_fontsize' : 1,
      'legend_enabled'  : False,
    }
    for name, value in attribute_dict.iteritems():
      setattr( opts, name, value )

    plot_all( opts, df, spmd, wsrt, isavings )

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":

  # concatenate all the result csv files
  df_list = []
  for res_file in file_list:
    df_list.append( pd.read_csv( res_file ) )
  df = pd.concat(df_list)

  # get the baseline dataframe for serial configs
  base_df = df[df.config == "serial"].copy()

  # loop through configs and normalize results
  for app in app_list:
    # serial steps
    ts, = base_df[(base_df.app == app_normalize_map[app])]['steps']
    # update steps to speedup inplace
    df.loc[(df.app == app) & (df.config != 'serial'), ['steps']] = \
      float(ts) / df.loc[(df.app == app) & (df.config != 'serial'), ['steps']]

  # replace any value that is zero with float 'nan' to skip plotting
  df[df==0] = float('nan')

  # column steps renamed to speedup
  df = df.rename(columns = { 'steps': 'speedup' })

  # save the results
  df.to_csv('all-results.csv',index=False)

  # option to plot all results or just per app-kernel
  per_app_plot = False

  # option to plot only spmd data
  spmd = True

  # option to plot only wsrt data
  wsrt = True

  # option to isavings or dsavings
  isavings = False

  # create plots
  plot( df, per_app_plot, spmd, wsrt, isavings )
