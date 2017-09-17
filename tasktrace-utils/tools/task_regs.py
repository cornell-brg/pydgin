#=========================================================================
# task_regs.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : September 15th, 2017
#
# Given, a binary file and the corresponding serial task execution trace
# the get_regs will analyze the maximum number of registers that are
# used to execute a given task

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
# maven_gpr_names
#-------------------------------------------------------------------------
# The register names used in maven-binutils for register specifiers, based
# on "mips_gpr_names_newabi" in maven-sys-xcc/src/opcodes/mips-maven-dis.c

maven_gpr_names = [
  "zero", "at",   "v0",   "v1",   "a0",   "a1",   "a2",   "a3",
  "a4",   "a5",   "a6",   "a7",   "t0",   "t1",   "t2",   "t3",
  "s0",   "s1",   "s2",   "s3",   "s4",   "s5",   "s6",   "s7",
  "t8",   "t9",   "k0",   "k1",   "gp",   "sp",   "s8",   "ra",
]

#-------------------------------------------------------------------------
# g_operand_columns
#-------------------------------------------------------------------------
# A global list of operand column names

g_operand_columns = ["dest","src0","src1"]

#-------------------------------------------------------------------------
# g_objdump_cmd
#-------------------------------------------------------------------------

g_objdump_cmd = "maven-objdump -dC %(app)s"

#-------------------------------------------------------------------------
# hex2int()
#-------------------------------------------------------------------------
# Utility function for pandas processing
# Function to convert a hex string value entry to integer as the dumps in
# the task-trace are integer values

def hex2int( x ):
  try:
    return int(x, 16)
  except ValueError:
    return x

#-------------------------------------------------------------------------
# convert2regs()
#-------------------------------------------------------------------------
# Utility function for pandas processing
# Function to convert a column entry to the maven-based register names

def convert_to_regs( x ):
  for reg in maven_gpr_names:
    if reg in str(x):
      return reg

#-------------------------------------------------------------------------
# get_regs()
#-------------------------------------------------------------------------
# given a app-binary file and the corresponding task_trace file, the
# function returns a set of unique register specifiers used in the trace

def get_regs( app, task_trace, outdir ):
  objdump_cmd  = g_objdump_cmd % { 'app' : app }
  disasm_insts = execute( objdump_cmd ).split("\n")
  insts_list   = []
  for inst in disasm_insts:
    inst = re.sub(":", "", inst)
    inst = inst.split()
    if len( inst ) >= 4:
      insts_list.append( [inst[0]] + inst[3].split(",") )
  disasm_df       = pd.DataFrame(insts_list,columns=['pc', 'dest', 'src0', 'src1'])
  disasm_df['pc'] = disasm_df['pc'].apply(hex2int)
  task_trace_df   = pd.read_csv(task_trace)
  pcall_sections  = task_trace_df['pid'].unique()
  with open("%(outdir)s/regs.out" % {'outdir' : outdir}, "w") as output:
    for pid in pcall_sections:
      regs_df = disasm_df[disasm_df['pc'].isin(task_trace_df[task_trace_df['pid']==pid]['pc'].unique())]
      unique_regs_map = set()
      for col in g_operand_columns:
        for reg in regs_df[col].apply(convert_to_regs).unique():
          unique_regs_map.add( reg )
      unique_regs_map = filter(None,unique_regs_map)
      output.write("Number of unique registers in section %(pid)s: %(regs)d\n" % { 'pid': pid, 'regs': len( unique_regs_map ) })
      output.write(str(list(unique_regs_map))+"\n")
