#=========================================================================
# summarize.py
#=========================================================================
# Quick and dirty script to merge PDF files

import os
import re
import sys
import subprocess

from common import *

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
# summarize
#-------------------------------------------------------------------------

def summarize():

  if os.path.exists( "summarized-results" ):
    cmd = 'rm -r summarized-results'
    execute( cmd )

  cmd = 'mkdir summarized-results'
  execute( cmd )

  # 1. mimd
  config = 'mimd'
  for rt in ['spmd','wsrt']:
    merge_files = []
    folder = 'results/mimd/%s/' % rt
    for app in app_list:
      if not os.path.isfile( folder + app + '-%s.pdf' % config ):
        continue
      merge_files.append( folder + app + '-%s.pdf' % config )
    merge_files = ' '.join( merge_files )
    cmd = 'pdftk ' + merge_files + ' output summarized-results/mimd-%s.pdf' % rt
    execute( cmd )

  # 2. mimd-static
  for insn_ports in [1,2]:
    config = 'ccores'
    for rt in ['spmd','wsrt']:
      merge_files = []
      folder = 'results/mimd-static-%dI/%s/' % ( insn_ports, rt )
      for app in app_list:
        if not os.path.isfile( folder + app + '-%s.pdf' % config ):
          continue
        merge_files.append( folder + app + '-%s.pdf' % config )
      merge_files = ' '.join( merge_files )
      cmd = 'pdftk ' + merge_files + ' output summarized-results/mimd-static-%dI-%s.pdf' % ( insn_ports, rt )
      execute( cmd )

  # 3. ccores
  for insn_ports in [1,2]:
    for resources in [1,2]:
      config = 'ccores'
      for rt in ['spmd','wsrt']:
        merge_files = []
        folder = 'results/ccores-%dI-%dL/%s/' % ( insn_ports, resources, rt )
        for app in app_list:
          if not os.path.isfile( folder + app + '-%s.pdf' % config ):
            continue
          merge_files.append( folder + app + '-%s.pdf' % config )
        merge_files = ' '.join( merge_files )
        cmd = 'pdftk ' + merge_files + ' output summarized-results/ccores-%dI-%dL-%s.pdf' % ( insn_ports, resources, rt )
        execute( cmd )

  # 4. simt-static
  for insn_ports in [1,2]:
    config = 'simt'
    for rt in ['spmd','wsrt']:
      merge_files = []
      folder = 'results/simt-static-%dI/%s/' % ( insn_ports, rt )
      for app in app_list:
        if not os.path.isfile( folder + app + '-%s.pdf' % config ):
          continue
        merge_files.append( folder + app + '-%s.pdf' % config )
      merge_files = ' '.join( merge_files )
      cmd = 'pdftk ' + merge_files + ' output summarized-results/simt-static-%dI-%s.pdf' % ( insn_ports, rt )
      execute( cmd )

  # 5. simt
  for insn_ports in [1,2]:
    for resources in [1,2]:
      config = 'simt'
      for rt in ['spmd','wsrt']:
        merge_files = []
        folder = 'results/simt-%dI-%dL/%s/' % ( insn_ports, resources, rt )
        for app in app_list:
          if not os.path.isfile( folder + app + '-%s.pdf' % config ):
            continue
          merge_files.append( folder + app + '-%s.pdf' % config )
        merge_files = ' '.join( merge_files )
        cmd = 'pdftk ' + merge_files + ' output summarized-results/simt-%dI-%dL-%s.pdf' % ( insn_ports, resources, rt )
        execute( cmd )

  # 6. mt
  config = 'mt'
  for rt in ['spmd','wsrt']:
    merge_files = []
    folder = 'results/mt/%s/' % rt
    for app in app_list:
      if not os.path.isfile( folder + app + '-%s.pdf' % config ):
        continue
      merge_files.append( folder + app + '-%s.pdf' % config )
    merge_files = ' '.join( merge_files )
    cmd = 'pdftk ' + merge_files + ' output summarized-results/mt-%s.pdf' % rt
    execute( cmd )

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  summarize()
