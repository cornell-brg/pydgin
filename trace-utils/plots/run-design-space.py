#=========================================================================
# run-design-space.py
#=========================================================================
# Script runs the design space

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

  # 1. mimd results
  for rt in ['spmd','wsrt']:
    cmd = 'mkdir -p results/mimd/%s' % rt
    execute( cmd )
    cmds = []
    plot  = './tpa-mimd-dsa --%s' % rt
    plot += ' --norm-insts' if norm_insts else ''
    cmds.append( plot )
    cmds.append( 'cp *.pdf results/mimd/%s/.' % rt )
    cmds.append( 'rm *.pdf' )
    with open( 'results/mimd/%s/%s.log' % ( rt, rt ), 'w' ) as out:
      for cmd in cmds:
        log = execute( cmd )
        out.write( log )

  # 2. mimd-static results
  for rt in ['spmd','wsrt']:
    for insn_ports in [1,2]:
      cmd = 'mkdir -p results/mimd-static-%dI/%s' % ( insn_ports, rt )
      execute( cmd )
      cmds = []
      plot  = './tpa-mimd-static-dsa --g_ncores 4 --g_insn_ports %d --g_resources 4 --%s' % ( insn_ports, rt )
      plot += ' --norm-insts' if norm_insts else ''
      cmds.append( plot )
      cmds.append( 'cp *.pdf results/mimd-static-%dI/%s/.' % ( insn_ports, rt ) )
      cmds.append( 'rm *.pdf' )
      with open( 'results/mimd-static-%dI/%s/%s.log' % ( insn_ports, rt, rt ), 'w' ) as out:
        for cmd in cmds:
          log = execute( cmd )
          out.write( log )

  # 3. ccores results
  for rt in ['spmd','wsrt']:
    for insn_ports in [1,2]:
      for resources in [1,2]:
        cmd = 'mkdir -p results/ccores-%dI-%dL/%s' % ( insn_ports, resources, rt )
        execute( cmd )
        cmds = []
        plot  = './tpa-ccores-dsa --g_ncores 4 --g_insn_ports %d --g_resources %d --%s' % ( insn_ports, resources, rt )
        plot += ' --norm-insts' if norm_insts else ''
        cmds.append( plot )
        cmds.append( 'cp *.pdf results/ccores-%dI-%dL/%s/.' % ( insn_ports, resources, rt ) )
        cmds.append( 'rm *.pdf' )
        with open( 'results/ccores-%dI-%dL/%s/%s.log' % ( insn_ports, resources, rt, rt ), 'w' ) as out:
          for cmd in cmds:
            log = execute( cmd )
            out.write( log )

  # 4. simt-static results
  for rt in ['spmd','wsrt']:
    for insn_ports in [1,2]:
      cmd = 'mkdir -p results/simt-static-%dI/%s' % ( insn_ports, rt )
      execute( cmd )
      cmds = []
      plot  = './tpa-simt-static-dsa --g_ncores 4 --g_insn_ports %d --g_resources 4 --%s' % ( insn_ports, rt )
      plot += ' --norm-insts' if norm_insts else ''
      cmds.append( plot )
      cmds.append( 'cp *.pdf results/simt-static-%dI/%s/.' % ( insn_ports, rt ) )
      cmds.append( 'rm *.pdf' )
      with open( 'results/simt-static-%dI/%s/%s.log' % ( insn_ports, rt, rt ), 'w' ) as out:
        for cmd in cmds:
          log = execute( cmd )
          out.write( log )

  # 5. simt results
  for rt in ['spmd','wsrt']:
    for insn_ports in [1,2]:
      for resources in [1,2]:
        cmd = 'mkdir -p results/simt-%dI-%dL/%s' % ( insn_ports, resources, rt )
        execute( cmd )
        cmds = []
        plots  = './tpa-simt-dsa --g_ncores 4 --g_insn_ports %d --g_resources %d --%s' % ( insn_ports, resources, rt )
        plots += ' --norm-insts' if norm_insts else ''
        cmds.append( plot )
        cmds.append( 'cp *.pdf results/simt-%dI-%dL/%s/.' % ( insn_ports, resources, rt ) )
        cmds.append( 'rm *.pdf' )
        with open( 'results/simt-%dI-%dL/%s/%s.log' % ( insn_ports, resources, rt, rt ), 'w' ) as out:
          for cmd in cmds:
            log = execute( cmd )
            out.write( log )

  # 6. mt results
  for rt in ['spmd','wsrt']:
    cmd = 'mkdir -p results/mt/%s' % rt
    execute( cmd )
    cmds = []
    plot  = './tpa-mt-dsa --%s' % rt
    plot += ' --norm-insts' if norm_insts else ''
    cmds.append( plot )
    cmds.append( 'cp *.pdf results/mt/%s/.' % rt )
    cmds.append( 'rm *.pdf' )
    with open( 'results/mt/%s/%s.log' % ( rt, rt ), 'w' ) as out:
      for cmd in cmds:
        log = execute( cmd )
        out.write( log )

  cmd = 'cp common.py results/.'
  execute( cmd )

  cmd = 'cp summarize-results.py results/.'
  execute( cmd )
