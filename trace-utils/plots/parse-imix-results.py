#=========================================================================
# parse-imix-results.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : February 20th, 2018
#
# Quick and dirty script to parse results

import os
import sys
import re
import subprocess

from common import *

#-------------------------------------------------------------------------
# Utility Function
#-------------------------------------------------------------------------

def execute(cmd):
  try:
    #print cmd
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    return err

#-------------------------------------------------------------------------
# global variables
#-------------------------------------------------------------------------

g_prefix_path = "../final/"

g_configs_dict = {}

#-------------------------------------------------------------------------
# isclose
#-------------------------------------------------------------------------
# copylifted:
# https://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

#-------------------------------------------------------------------------
# populate_configs()
#-------------------------------------------------------------------------

def populate_configs():
  subfolders = os.listdir( g_prefix_path )
  short_name = None
  for subfolder in subfolders:
    if "serial" in subfolder:
      short_name = "serial"
    else:
      short_name = re.sub("results-", "", subfolder)
      short_name = re.sub("-limit-1", "-1", short_name)
      short_name = re.sub("-limit-250", "-250", short_name)
      short_name = re.sub("-limit-500", "-500", short_name)
      short_name = re.sub("-limit-1000", "-1000", short_name)
      short_name = re.sub("conjoined-", "conj-", short_name)
    g_configs_dict[subfolder] = short_name
    print "{:^40s} {:^40s}".format( subfolder, short_name )
  print "Total number of configs are: ", len( g_configs_dict )

#-------------------------------------------------------------------------
# summarize()
#-------------------------------------------------------------------------

def summarize():

  res_file = 'imix-results.csv'

  with open( res_file, 'w' ) as out:

    columns  = 'app,config,total_insts,'
    columns += 'integer,load,store,amo,fpu,mdu,'
    columns += 'total_spmd,total_wsrt,total_rt,total_task\n'
    out.write( columns )

    for config_dir,config in g_configs_dict.iteritems():
      resultsdir_path = g_prefix_path + config_dir
      if not os.path.isdir(resultsdir_path):
        continue
      subfolders      = os.listdir( resultsdir_path )
      for subfolder in subfolders:
        try:
          app = re.sub("-parc", '', subfolder)
          app = re.sub("-small", '', app)
          app = re.sub("-mtpull", '', app)
          app = re.sub("-mt", '', app)

          if not app in app_short_name_dict.keys() and config != "serial":
            continue

          res_file =  resultsdir_path + '/' + subfolder + '/' + subfolder + '.out'
          cmd      = 'grep -r -A 90 "Serial steps in stats region =" %(res_file)s' % { 'res_file' : res_file }
          lines    = execute( cmd )

          total_insts = 0
          int_insts   = 0
          load_insts  = 0
          store_insts = 0
          amo_insts   = 0
          fpu_insts   = 0
          mdu_insts   = 0

          total_spmd  = 0
          total_wsrt  = 0
          total_rt    = 0
          total_task  = 0

          for line in lines.split('\n'):
            if line != '':
              if   'Total steps in stats region' in line:
                steps = int( line.split()[-1] )
              elif 'Total insts in parallel regions' in line:
                total_insts = int( line.split()[-1] )
              elif 'integer =' in line:
                int_insts = int( line.split()[-1] )
              elif 'load    =' in line:
                load_insts = int( line.split()[-1] )
              elif 'store   =' in line:
                store_insts = int( line.split()[-1] )
              elif 'amo     =' in line:
                amo_insts = int( line.split()[-1] )
              elif 'fpu     =' in line:
                fpu_insts = int( line.split()[-1] )
              elif 'mdu     =' in line:
                mdu_insts = int( line.split()[-1] )
              elif "Total insts in spmd region" in line:
                total_spmd = int(line.split()[-1])
              elif "Total insts in wsrt region" in line:
                total_wsrt = int(line.split()[-1])
              elif "Total insts in runtime" in line:
                total_rt = int(line.split()[-1])
              elif "Total insts in tasks" in line:
                total_task = int(line.split()[-1])

          base_str = '{},'*11 + '{}\n'
          if config == "serial":
            out.write(
              base_str.format(
                app,config,total_insts,
                int_insts,load_insts,store_insts,amo_insts,fpu_insts,mdu_insts,
                total_spmd,total_wsrt,total_rt,total_task
              )
            )
          else:
            out.write(
              base_str.format(
                app_short_name_dict[app],config,total_insts,
                int_insts,load_insts,store_insts,amo_insts,fpu_insts,mdu_insts,
                total_spmd,total_wsrt,total_rt,total_task
              )
            )
        except:
          print "{} {}: Results file not present".format( config, subfolder )
          if config == "serial":
            out.write( base_str.format(app,config,0,0,0,0,0,0,0,0,0,0,0) )
          else:
            out.write( base_str.format(app_short_name_dict[app],config,0,0,0,0,0,0,0,0,0,0,0) )
          continue

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  populate_configs()
  summarize()
