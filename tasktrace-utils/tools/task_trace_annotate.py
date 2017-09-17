#!/usr/bin/env python
#=========================================================================
# task_trace_annotate.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : September 16th, 2017
#
# Given a task-trace and the corresponding runtime metadata file the tool
# annotates the task-trace with runtime function names

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
# annotate_trace()
#-------------------------------------------------------------------------

def annotate_trace( app, trace, metadata, outdir ):
  # parse the runtime metadata
  metadata_file  = open( metadata, 'rb' )
  line           = metadata_file.readline().strip().split(",")
  addr_list      = [ int(n) for n in line ]
  name_list      = metadata_file.readline().strip().split(",")
  runtime_dict   = dict(zip(addr_list,name_list))

  # parse the objdump for lookup
  objdump_cmd  = g_objdump_cmd % { 'app' : app }
  disasm_insts = execute( objdump_cmd ).split("\n")
  insts_list   = []
  for inst in disasm_insts:
    inst = re.sub(":", "", inst)
    inst = inst.split()
    if len( inst ) >= 4:
      insts_list.append( [inst[0]] + [inst[2]] + inst[3].split(",") )
  disasm_df         = pd.DataFrame(insts_list,columns=["pc", "asm", "dest", "src0", "src1"])
  disasm_df["pc"]   = disasm_df["pc"].apply(hex2int)
  disasm_df["dest"] = disasm_df["dest"].apply(hex2int)

  # read the task trace
  task_trace_df   = pd.read_csv(trace)

  # get a frame from the disassembly for jal instructions
  jal_df  = disasm_df[disasm_df.asm.isin(["jal"])]
  # get a frame of pc's in the task_trace that have jal's
  jal_df  = jal_df[jal_df.pc.isin(task_trace_df["pc"].unique())]

  # for each pc and the target in the jal_df, annotate original trace if
  # the pc if the target corresponds to runtime functions
  for pc,tgt in zip(jal_df.pc.values,jal_df.dest.values):
    if tgt in runtime_dict.keys():
      task_trace_df.loc[task_trace_df.pc == pc, "nan"] = runtime_dict[tgt]

  task_trace_df.to_csv(
    "%(outdir)s/task-trace-annotated.csv" % {'outdir' : outdir},
    index=False
  )
