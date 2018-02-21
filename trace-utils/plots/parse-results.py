#=========================================================================
# parse-results.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : January 22nd, 2018
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

g_prefix_path = "../new-spin/"

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

  res_file = 'sim-results.csv'

  with open( res_file, 'w' ) as out:

    columns  = 'app,config,steps,total_insts,'
    columns += 'unique_iaccess,total_iaccess,total_l0_hits,total_coalesces,'
    columns += 'unique_frontend,total_frontend,'
    columns += 'unique_execute,total_execute,'
    columns += 'unique_daccess,total_daccess,'
    columns += 'unique_work,total_work\n'
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

          steps           = 0
          unique_iaccess  = 0
          unique_frontend = 0
          unique_execute  = 0
          unique_daccess  = 0
          total_iaccess   = 0
          total_frontend  = 0
          total_execute   = 0
          total_daccess   = 0
          total_l0_hits   = 0
          total_coalesces = 0
          total_insts     = 0

          for line in lines.split('\n'):
            if line != '':
              if   'Total steps in stats region' in line:
                steps = int( line.split()[-1] )
              elif 'Total insts in parallel regions' in line:
                total_insts = int( line.split()[-1] )
              elif 'Total instruction accesses in parallel regions' in line:
                total_iaccess = int( line.split()[-1] )
              elif 'Unique instruction accesses in parallel regions' in line:
                unique_iaccess = int( line.split()[-1] )
              elif 'Total hits in Core L0 buffer' in line:
                total_l0_hits = int( line.split()[-1] )
              elif 'Total number of coalesced instruction accesses' in line:
                total_coalesces = int( line.split()[-1] )
              elif 'Total frontend accesses in parallel regions' in line:
                total_frontend = int( line.split()[-1] )
              elif 'Unique frontend accesses in parallel regions' in line:
                unique_frontend = int( line.split()[-1] )
              elif 'Total number of executed instructions' in line:
                total_execute = int( line.split()[-1] )
              elif 'Unique executed instructions' in line:
                unique_execute = int( line.split()[-1] )
              elif 'Total data accesses in parallel regions' in line:
                total_daccess = int( line.split()[-1] )
              elif 'Unique data accesses in parallel regions' in line:
                unique_daccess = int( line.split()[-1] )

          total_work    = total_iaccess + total_frontend + total_execute + total_daccess
          unique_work   = unique_iaccess + unique_frontend + unique_execute + unique_daccess

          #total_savings = 100*float( total_work - unique_work )/total_work
          #l0_hits       = 100*float( total_l0_hits )/total_work
          #icoalesces    = 100*float( total_coalesce )/total_work
          #frontend_redn = 100*float( total_front - unique_front )/total_work
          #value_redn    = 100*float( total_execute - unique_execute )/total_work
          #dsavings      = 100*float( total_daccess - unique_daccess )/total_work
          #isavings      = 100*float( total_iaccess - unique_iaccess )/total_work

          base_str = '{},'*15 + '{}\n'
          if config == "serial":
            out.write(
              base_str.format(
                app,config,steps,total_insts,
                unique_iaccess,total_iaccess,total_l0_hits,total_coalesces,
                unique_frontend,total_frontend,
                unique_execute,total_execute,
                unique_daccess,total_daccess,
                unique_work,total_work
              )
            )
          else:
            out.write(
              base_str.format(
                app_short_name_dict[app],config,steps,total_insts,
                unique_iaccess,total_iaccess,total_l0_hits,total_coalesces,
                unique_frontend,total_frontend,
                unique_execute,total_execute,
                unique_daccess,total_daccess,
                unique_work,total_work
              )
            )
        except:
          print "{} {}: Results file not present".format( config, subfolder )
          if config == "serial":
            out.write( base_str.format(app,config,0,0,0,0,0,0,0,0,0,0,0,0,0,0) )
          else:
            out.write( base_str.format(app_short_name_dict[app],config,0,0,0,0,0,0,0,0,0,0,0,0,0,0) )
          continue

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  populate_configs()
  summarize()
