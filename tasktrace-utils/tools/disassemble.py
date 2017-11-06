#=========================================================================
# disassemble.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : November 5th, 2017
#
# Given a binary for an application the script simply dumps a pandas frame
# that has all the pc values that are call sites for statically known
# functions i.e. all jal locations

import csv
import os
import pandas as pd
import re
import sys
import subprocess

#-------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------

def execute(cmd):
  #print cmd
  try:
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

#-------------------------------------------------------------------------
# g_objdump_cmd
#-------------------------------------------------------------------------

g_objdump_cmd = "maven-objdump -dC %(app)s"

#-------------------------------------------------------------------------
# disassemble()
#-------------------------------------------------------------------------

def disassemble( app, outdir ):
  # parse the objdump for lookup
  objdump_cmd  = g_objdump_cmd % { 'app' : app }
  disasm_insts = execute( objdump_cmd ).split("\n")
  insts_list   = []
  for inst in disasm_insts:
    inst = re.sub(":", "", inst)
    inst = inst.split()
    if len( inst ) >= 4:
      insts_list.append( [inst[0]] + [inst[2]] + [inst[3].split(",")[0]] )
  disasm_df         = pd.DataFrame(insts_list,columns=["pc", "asm", "dest"])

  # get a frame from the disassembly for jal instructions
  jal_df  = disasm_df[disasm_df.asm.isin(["jal"])]

  jal_df.to_csv(
    "%(outdir)s/jal.csv" % {'outdir' : outdir},
    index=False
  )
