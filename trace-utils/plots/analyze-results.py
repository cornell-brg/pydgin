#=========================================================================
# analyze-results.py
#=========================================================================
#
#  -h --help           Display this message
#
#  --imix              Analyze imix
#  --pareto-points     Analyze speedup
#  --absolute          Show absolute instruction counts
#  --no-spmd           Turn off spmd data-points
#  --no-wsrt           Turn off wsrt data-points
#  --no-isavings       Turn off isavings (enable dsavings)
#
# Quick and dirty script to analyze data
#
# Author : Shreesha Srinath
# Date   : January 4th, 2018

import argparse
import re
import math
import sys

import pandas as pd

from common import *

#-------------------------------------------------------------------------
# Command line processing
#-------------------------------------------------------------------------

class ArgumentParserWithCustomError(argparse.ArgumentParser):
  def error( self, msg = "" ):
    if ( msg ): print("\n ERROR: %s" % msg)
    print("")
    file = open( sys.argv[0] )
    for ( lineno, line ) in enumerate( file ):
      if ( line[0] != '#' ): sys.exit(msg != "")
      if ( (lineno == 2) or (lineno >= 4) ): print( line[1:].rstrip("\n") )

def parse_cmdline():
  p = ArgumentParserWithCustomError( add_help=False )

  # Standard command line arguments

  p.add_argument( "-h", "--help", action="store_true" )

  # Additional commane line arguments for the simulator

  p.add_argument( "--imix",          action="store_true",  default=False )
  p.add_argument( "--absolute",      action="store_true",  default=False )
  p.add_argument( "--no-spmd",       action="store_false", default=True  )
  p.add_argument( "--no-wsrt",       action="store_false", default=True  )
  p.add_argument( "--pareto-points", action="store_true",  default=False )
  p.add_argument( "--no-isavings",   action="store_false", default=True  )

  opts = p.parse_args()
  if opts.help: p.error()
  return opts

#-------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------

# template configuration string
g_config_str = "%s-%dc-%dl0-%dip-%ddp-%dlp-%dl-%dr"

# global num cores
g_ncores     = 4

# select a global configuration
g_config = {
  'l0_buffer_sz' : [1],
  'ports'        : range(1,g_ncores+1),
  'llfus'        : range(1,g_ncores+1),
  'lockstep'     : range(2),
  'analysis'     : range(3),
}

#-------------------------------------------------------------------------
# Configuration struct
#-------------------------------------------------------------------------

class Config():

  def __init__(s, **kwargs):
    s.l0_buffer_sz = kwargs.get('l0_buffer_sz', range(1,2))
    s.ports        = kwargs.get('ports',        range(1,g_ncores+1))
    s.llfus        = kwargs.get('llfus',        range(1,g_ncores+1))
    s.lockstep     = kwargs.get('lockstep',     range(2))
    s.analysis     = kwargs.get('analysis',     range(3))
    s.spmd         = kwargs.get('spmd',         True)
    s.wsrt         = kwargs.get('wsrt',         True)
    s.isavings     = kwargs.get('isavings',     True)

  def __str__(s):
    sb = []
    for key in s.__dict__:
      if key not in ['spmd','wsrt','isavings']:
        sb.append("{key}='{value}'".format(key=key, value=s.__dict__[key]))
    return ', '.join(sb)

  def __repr__(s):
    return s.__str__()

#-------------------------------------------------------------------------
# is_pareto_front()
#-------------------------------------------------------------------------
# reference:
# http://hinnefe2.github.io/python/tools/2015/09/21/mario-kart.html

def is_pareto_front(row, stats, xlabel, ylabel):
  x = row[xlabel]
  y = row[ylabel]

  # look for points with the same y value but larger x value
  is_max_x = stats.loc[stats[ylabel]==y].max()[xlabel] <= x
  # look for points with the same x value but larger y value
  is_max_y = stats.loc[stats[xlabel]==x].max()[ylabel] <= y

  # look for points that are larger in both x and y
  is_double = len(stats.loc[(stats[xlabel]>x) & (stats[ylabel]>y)])==0

  return is_max_x and is_max_y and is_double

#-------------------------------------------------------------------------
# analyze_per_app()
#-------------------------------------------------------------------------

def analyze_per_app( df, app, cfg ):
  print app
  print cfg

  savings = 'isavings' if cfg.isavings else 'dsavings'
  for l0_buffer_sz in cfg.l0_buffer_sz:
    for ports in cfg.ports:
      for llfus in cfg.llfus:
        configs = []

        if cfg.spmd:
          for lockstep in cfg.lockstep:
            for analysis in cfg.analysis:
              config = g_config_str % ( 'spmd', g_ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
              configs.append( config )

        if cfg.wsrt:
          for lockstep in cfg.lockstep:
            for analysis in cfg.analysis:
              config = g_config_str % ( 'wsrt', g_ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
              configs.append( config )

        stats = pd.DataFrame()
        for config in configs:
          stats = stats.append( df.loc[(df.config == config) & (df.app == app), ['config', 'speedup', savings]] )

        is_pareto = stats.apply(lambda row: is_pareto_front(row, stats, 'speedup', savings),axis=1)
        config_pareto = stats.ix[is_pareto].sort_values(by='speedup')
        print "Possible combinations : ", stats.shape[0]
        print "Optimal combinations  : ", len(config_pareto)
        print stats.ix[is_pareto][['config','speedup',savings]].sort_values('speedup').to_string(index=False)
        print
  print

#-------------------------------------------------------------------------
# analyze_savings()
#-------------------------------------------------------------------------

def analyze_savings(spmd=True,wsrt=True,isavings=True):
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

  # loop through applications
  config          = Config(**g_config)
  config.spmd     = spmd
  config.wsrt     = wsrt
  config.isavings = isavings
  for app in  app_list:
    analyze_per_app( df, app, config )

#-------------------------------------------------------------------------
# describe_insn_type()
#-------------------------------------------------------------------------

def describe_insn_type( app, df, insn_type ):
  temp = df[df.app == app][[insn_type]].describe().T
  temp.insert(loc=0,column='app',value=app)
  temp.insert(loc=1,column='insn_type',value=insn_type)
  return temp

#-------------------------------------------------------------------------
# analyze_imix()
#-------------------------------------------------------------------------

def analyze_imix(absolute=True):

  # concatenate all the result csv files
  df_list = []
  for res_file in insn_file_list:
    df_list.append( pd.read_csv( res_file ) )
  df = pd.concat(df_list)

  # calculate percent breakdowns
  if not absolute:
    df.loc[:,['integer','load','store','amo','mdu','fpu']] = df.loc[:,['integer','load','store','amo','mdu','fpu']].div(df.total, axis=0)
    df.loc[:,['integer','load','store','amo','mdu','fpu']] = df.loc[:,['integer','load','store','amo','mdu','fpu']].multiply(100, axis=0)

  # analyze the values for each application
  new_df = pd.DataFrame()
  for app in app_list:
    new_df = new_df.append( describe_insn_type( app, df, "integer" ) )
    new_df = new_df.append( describe_insn_type( app, df, "load" ) )
    new_df = new_df.append( describe_insn_type( app, df, "store" ) )
    new_df = new_df.append( describe_insn_type( app, df, "amo" ) )
    new_df = new_df.append( describe_insn_type( app, df, "mdu" ) )
    new_df = new_df.append( describe_insn_type( app, df, "fpu" ) )

  new_df.to_csv("imix-analysis.csv", index=False)

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  opts = parse_cmdline()

  if opts.imix:
    analyze_imix(opts.absolute)

  if opts.pareto_points:
    analyze_savings(spmd=opts.no_spmd,wsrt=opts.no_wsrt,isavings=opts.no_isavings)
