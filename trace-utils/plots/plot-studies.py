#=========================================================================
# plot-studies.py
#=========================================================================
# Summarize the story

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

  # clean up the existing results
  if os.path.exists( "results" ):
    cmd = 'rm -r results'
    execute( cmd )
  cmd = 'rm *.pdf'
  execute( cmd )

  # 1. is there redundancy?
  cmd = 'mkdir -p results/redundancy'
  execute( cmd )
  cmds = []
  for runtime in ['spmd','wsrt']:
    plot = './tpa-redundancy-plot --runtime %s' % ( runtime )
    cmds.append( plot )
    cmds.append( 'mv %s-redundancy.pdf results/redundancy/.' % ( runtime ) )
  for cmd in cmds:
    execute( cmd )

  # 2. what is the potential to exploit insn. access redundancy dynamically?
  cmd = 'mkdir -p results/dynamic'
  execute( cmd )
  cmds = []
  for runtime in ['spmd','wsrt']:
    plot = './tpa-mimd-dynamic-bar-plot --runtime %s' % ( runtime )
    cmds.append( plot )
    cmds.append( 'mv %s-mimd-dynamic-bar.pdf results/dynamic/.' % ( runtime ) )
  for cmd in cmds:
    execute( cmd )

  # 3. what are the results for statically sharing the imem port?
  cmd = 'mkdir -p results/imem-only'
  execute( cmd )
  cmds = []
  for runtime in ['spmd','wsrt']:
    for insn_ports in [1,2]:
      plot = './tpa-imem-only-bar-plot --runtime %s --insn_ports %d' % ( runtime, insn_ports )
      cmds.append( plot )
      cmds.append( 'mv %s-imem-only-%d-insn_ports-bar.pdf results/imem-only/.' % ( runtime, insn_ports ) )
      plot = './tpa-imem-only-scatter-plot --runtime %s --insn_ports %d' % ( runtime, insn_ports )
      cmds.append( plot )
      cmds.append( 'mv %s-imem-only-%d-insn_ports-scatter.pdf results/imem-only/.' % ( runtime, insn_ports ) )
    cmds.append( './tpa-imem-only-one-vs-two-plot --runtime %s' %  ( runtime ) )
    cmds.append( 'mv %s-imem-only-one-vs-two.pdf results/imem-only/.'  % ( runtime ) )
  for cmd in cmds:
    execute( cmd )

  # 4. what are the results for statically sharing imem and frontend only?
  cmd = 'mkdir -p results/imem-fe-only'
  execute( cmd )
  cmds = []
  for runtime in ['spmd','wsrt']:
    for frontend in [1,2]:
      plot = './tpa-imem-fe-only-bar-plot --runtime %s --frontend %d' % ( runtime, frontend )
      cmds.append( plot )
      cmds.append( 'mv %s-imem-fe-only-%d-frontend-bar.pdf results/imem-fe-only/.' % ( runtime, frontend ) )
      plot = './tpa-imem-fe-only-scatter-plot --runtime %s --frontend %d' % ( runtime, frontend )
      cmds.append( plot )
      cmds.append( 'mv %s-imem-fe-only-%d-frontend-scatter.pdf results/imem-fe-only/.' % ( runtime, frontend ) )
    cmds.append( './tpa-imem-fe-only-one-vs-two-plot --runtime %s' % ( runtime ) )
    cmds.append( 'mv %s-imem-fe-only-one-vs-two.pdf results/imem-fe-only/.' % ( runtime ) )
  for cmd in cmds:
    execute( cmd )

  # 5. what are the results for statically sharing imem and llfus only?
  cmd = 'mkdir -p results/imem-llfu-only'
  execute( cmd )
  cmds = []
  for runtime in ['spmd','wsrt']:
    for resources in [1,2]:
      plot = './tpa-imem-llfu-only-bar-plot --runtime %s --resources %d' % ( runtime, resources )
      cmds.append( plot )
      cmds.append( 'mv %s-imem-llfu-only-%d-resources-bar.pdf results/imem-llfu-only/.' % ( runtime, resources ) )
      plot = './tpa-imem-llfu-only-scatter-plot --runtime %s --resources %d' % ( runtime, resources )
      cmds.append( plot )
      cmds.append( 'mv %s-imem-llfu-only-%d-resources-scatter.pdf results/imem-llfu-only/.' % ( runtime, resources ) )
    cmds.append( './tpa-imem-llfu-only-one-vs-two-plot --runtime %s' % ( runtime ) )
    cmds.append( 'mv %s-imem-llfu-only-one-vs-two.pdf results/imem-llfu-only/.' % ( runtime ) )
  for cmd in cmds:
    execute( cmd )

  # 6. what are the results for statically sharing imem, frontend, and llfus?
  cmd = 'mkdir -p results/imem-fe-llfu'
  execute( cmd )
  cmds = []
  for runtime in ['spmd','wsrt']:
    for resources in [1,2]:
      plot = './tpa-imem-fe-llfu-bar-plot --runtime %s --resources %d' % ( runtime, resources )
      cmds.append( plot )
      cmds.append( 'mv %s-imem-fe-llfu-%d-resources-bar.pdf results/imem-fe-llfu/.' % ( runtime, resources ) )
      plot = './tpa-imem-fe-llfu-scatter-plot --runtime %s --resources %d' % ( runtime, resources )
      cmds.append( plot )
      cmds.append( 'mv %s-imem-fe-llfu-%d-resources-scatter.pdf results/imem-fe-llfu/.' % ( runtime, resources ) )
    cmds.append( './tpa-imem-fe-llfu-one-vs-two-plot --runtime %s' % ( runtime ) )
    cmds.append( 'mv %s-imem-fe-llfu-one-vs-two.pdf results/imem-fe-llfu/.' % ( runtime ) )
  for cmd in cmds:
    execute( cmd )

  # 7. what are the results for sharing everything (mt) ?
  cmd = 'mkdir -p results/share-all'
  execute( cmd )
  cmds = []
  for runtime in ['spmd', 'wsrt']:
    plot = './tpa-share-all-bar-plot --runtime %s' % ( runtime )
    cmds.append( plot )
    cmds.append( 'mv %s-share-all-bar.pdf results/share-all/.' % ( runtime ) )
    plot = './tpa-share-all-scatter-plot --runtime %s' % ( runtime )
    cmds.append( plot )
    cmds.append( 'mv %s-share-all-scatter.pdf results/share-all/.' % ( runtime ) )
  for cmd in cmds:
    execute( cmd )

  # save all the csvs
  cmds = []
  cmds.append( 'cp sim-l0-results.csv results/.'        )
  cmds.append( 'cp sim-results-final.csv results/.'     )
  cmds.append( 'cp sim-results-formatted.csv results/.' )
  for cmd in cmds:
    execute( cmd )
