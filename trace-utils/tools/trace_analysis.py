#=========================================================================
# trace_analysis.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : October 4th, 2017
#

import os
import sys
import subprocess

import pandas as pd

from collections import Counter
from collections import defaultdict

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
# maximal_sharing
#-------------------------------------------------------------------------

def maximal_sharing( strands ):
  unique = 0
  total  = 0
  streams = strands.values()
  if len(streams) == 1:
    unique = unique + len(streams[0])
    total = total + len(streams[0])
    return (unique,total)

  timesteps = 0
  for stream in streams:
    if len(stream) > timesteps:
      timesteps = len(stream)
    total = total + len(stream)

  if timesteps:
    for step in range(timesteps):
      pc_list = []
      for stream in streams:
        try:
          pc_list.append(stream[step])
        except IndexError:
          continue
      pc_counts = Counter(pc_list)
      unique = unique + len(set(pc_counts))
  return (unique,total)

#-------------------------------------------------------------------------
# trace_analyze()
#-------------------------------------------------------------------------

def trace_analyze(trace,outdir):
  trace_df = pd.read_csv(trace,
                         converters = {
                           'pid'    : lambda x : int( x, 16 ),
                           'cid'    : lambda x : int( x, 16 ),
                           'ret_cnt': lambda x : int( x, 16 ),
                         }
                        )
  parallel_regions = trace_df['pid'].unique()

  with open("%(outdir)s/trace-analysis.txt" % {'outdir':outdir}, "w") as out:
    g_unique_insts = 0
    g_total_insts = 0
    for region in parallel_regions:
      trace = trace_df[trace_df['pid']==region]
      num_cores = trace['cid'].unique().tolist()
      strands = {}
      for core in range(len(num_cores)):
        strands[core] = trace[trace['cid']==core]['pc'].values.tolist()

      (unique_insts, total_insts) = maximal_sharing( strands )

      g_unique_insts = g_unique_insts + unique_insts
      g_total_insts  = g_total_insts + total_insts

      out.write("Parallel region %(region)s:\n"  % {'region':region})
      out.write("  unique    insts: %(insts)d\n" % {'insts' :unique_insts})
      out.write("  total     insts: %(insts)d\n" % {'insts' :total_insts})
      out.write("  redundant insts: %(insts)d\n" % {'insts' :(total_insts-unique_insts)})
      try:
        out.write("  savings: %(savings).2f%%\n" % {'savings':((total_insts-unique_insts)/float(total_insts))*100})
      except ZeroDivisionError:
        out.write("  savings: 0%\n")

    out.write("Overall stats\n")
    out.write("  unique    insts: %(insts)d\n" % {'insts' :g_unique_insts})
    out.write("  total     insts: %(insts)d\n" % {'insts' :g_total_insts})
    out.write("  redundant insts: %(insts)d\n" % {'insts' :(g_total_insts-g_unique_insts)})
    try:
      out.write("  savings: %(savings).2f%%\n" % {'savings':((g_total_insts-g_unique_insts)/float(g_total_insts))*100})
    except ZeroDivisionError:
      out.write("  savings: 0%\n")
