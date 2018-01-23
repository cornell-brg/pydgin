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

g_prefix_path = "../../all-results/"

g_configs_dict = {}

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
      short_name = re.sub("-limit-1", "", short_name)
      short_name = re.sub("-limit-250", "-hint", short_name)
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

    out.write('app,config,steps,iredundancy,isavings\n')

    for config_dir,config in g_configs_dict.iteritems():
      resultsdir_path = g_prefix_path + config_dir
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
          cmd      = 'grep -r -A 60 "Serial steps in stats region =" %(res_file)s' % { 'res_file' : res_file }
          lines    = execute( cmd )

          steps       = 0
          iredundancy = 0
          isavings    = 0

          for line in lines.split('\n'):
            if line != '':
              if   'Total steps in stats region' in line:
                steps = int( line.split()[-1] )
              elif 'Redundancy in parallel regions' in line:
                iredundancy = float( line.split()[-1] )
              elif 'Savings for instruction accesses in parallel regions' in line:
                isavings = float( line.split()[-1] )

          if config == "serial":
            out.write('{},{},{},{},{}\n'.format(app,config,steps,iredundancy,isavings))
          else:
            out.write('{},{},{},{},{}\n'.format(app_short_name_dict[app],config,steps,iredundancy,isavings))
        except:
          print "{} {}: Results file not present".format( config, subfolder )
          if config == "serial":
            out.write('{},{},{},{},{}\n'.format(app,0,0,0,0))
          else:
            out.write('{},{},{},{},{}\n'.format(app_short_name_dict[app],0,0,0,0))
          continue

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  populate_configs()
  summarize()
