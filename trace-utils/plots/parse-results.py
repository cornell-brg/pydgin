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

g_prefix_path = "../"

g_configs_dict = {
  'results-serial-small'                      : 'serial',
  'results-mimd-spmd-1'                       : 'mimd-spmd',
  'results-mimd-spmd-250'                     : 'mimd-spmd-hint',
  'results-mimd-wsrt-1'                       : 'mimd-wsrt',
  'results-mimd-wsrt-250'                     : 'mimd-wsrt-hint',
  'results-conjoined-cores-spmd-1-limit-1'    : 'conj-cores-1-spmd',
  'results-conjoined-cores-spmd-1-limit-250'  : 'conj-cores-1-spmd-hint',
  'results-conjoined-cores-spmd-2-limit-1'    : 'conj-cores-2-spmd',
  'results-conjoined-cores-spmd-2-limit-250'  : 'conj-cores-2-spmd-hint',
  'results-conjoined-cores-wsrt-1-limit-1'    : 'conj-cores-1-wsrt',
  'results-conjoined-cores-wsrt-1-limit-250'  : 'conj-cores-1-wsrt-hint',
  'results-conjoined-cores-wsrt-2-limit-1'    : 'conj-cores-2-wsrt',
  'results-conjoined-cores-wsrt-2-limit-250'  : 'conj-cores-2-wsrt-hint',
  'results-simt-spmd-1-2-limit-1'             : 'simt-1-2-spmd',
  'results-simt-spmd-1-2-limit-250'           : 'simt-1-2-spmd-hint',
  'results-simt-spmd-1-4-limit-1'             : 'simt-1-4-spmd',
  'results-simt-spmd-1-4-limit-250'           : 'simt-1-4-spmd-hint',
  'results-simt-spmd-2-2-limit-1'             : 'simt-2-2-spmd',
  'results-simt-spmd-2-2-limit-250'           : 'simt-2-2-spmd-hint',
  'results-simt-spmd-2-4-limit-1'             : 'simt-2-4-spmd',
  'results-simt-spmd-2-4-limit-250'           : 'simt-2-4-spmd-hint',
  'results-simt-wsrt-1-2-limit-1'             : 'simt-1-2-wsrt',
  'results-simt-wsrt-1-2-limit-250'           : 'simt-1-2-wsrt-hint',
  'results-simt-wsrt-1-4-limit-1'             : 'simt-1-4-wsrt',
  'results-simt-wsrt-1-4-limit-250'           : 'simt-1-4-wsrt-hint',
  'results-simt-wsrt-2-2-limit-1'             : 'simt-2-2-wsrt',
  'results-simt-wsrt-2-2-limit-250'           : 'simt-2-2-wsrt-hint',
  'results-simt-wsrt-2-4-limit-1'             : 'simt-2-4-wsrt',
  'results-simt-wsrt-2-4-limit-250'           : 'simt-2-4-wsrt-hint',
}

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
          continue

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  summarize()

