#=========================================================================
# plot-all-groups.py
#=========================================================================
# Script plots the design space

import os
import re
import sys
import subprocess

#-------------------------------------------------------------------------
# Utility Function
#-------------------------------------------------------------------------

def execute(cmd):
  try:
    print cmd
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    return err

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":

  norm_insts = False

  # clean up the existing results
  if os.path.exists( "results" ):
    cmd = 'rm -r results'
    execute( cmd )

  cmd = 'rm *.pdf'
  execute( cmd )
  cmd = 'mkdir -p results/'
  execute( cmd )

  # 1. mimd-static results
  for rt in ['spmd','wsrt']:
    cmds = []
    for app_group in ['custom','pbbs','cilk']:
      if app_group == 'cilk' and rt == 'spmd':
        continue
      plot  = './tpa-mimd-static-bar-plot --runtime %s ' % rt
      plot += '--app-group %s ' % app_group
      plot += '--g_ncores 4 '
      plot += '--g_resources 4 '
      cmds.append( plot )
    for cmd in cmds:
      execute( cmd )

  # 2. ccores results
  for rt in ['spmd','wsrt']:
    cmds = []
    for app_group in ['custom','pbbs','cilk']:
      if app_group == 'cilk' and rt == 'spmd':
        continue
      plot  = './tpa-ccores-bar-plot --runtime %s ' % rt
      plot += '--app-group %s ' % app_group
      plot += '--g_ncores 4 '
      cmds.append( plot )
    for cmd in cmds:
      execute( cmd )

  # 3. simt-static results
  for rt in ['spmd','wsrt']:
    cmds = []
    for app_group in ['custom','pbbs','cilk']:
      if app_group == 'cilk' and rt == 'spmd':
        continue
      plot  = './tpa-simt-static-bar-plot --runtime %s ' % rt
      plot += '--app-group %s ' % app_group
      plot += '--g_resources 4 '
      cmds.append( plot )
    for cmd in cmds:
      execute( cmd )

  # 4. simt results
  for rt in ['spmd','wsrt']:
    cmds = []
    for app_group in ['custom','pbbs','cilk']:
      if app_group == 'cilk' and rt == 'spmd':
        continue
      plot  = './tpa-simt-bar-plot --runtime %s ' % rt
      plot += '--app-group %s ' % app_group
      cmds.append( plot )
    for cmd in cmds:
      execute( cmd )

  # 5. mt results
  for rt in ['spmd','wsrt']:
    cmds = []
    for app_group in ['custom','pbbs','cilk']:
      if app_group == 'cilk' and rt == 'spmd':
        continue
      plot  = './tpa-mt-bar-plot --runtime %s ' % rt
      plot += '--app-group %s ' % app_group
      cmds.append( plot )
    for cmd in cmds:
      execute( cmd )

  cmd = 'cp *.pdf results/.'
  execute( cmd )

  cmd = 'cp plot-all-groups.py results/.'
  execute( cmd )
