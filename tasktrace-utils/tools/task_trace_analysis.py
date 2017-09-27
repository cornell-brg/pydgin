#=========================================================================
# task_trace_analysis.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : September 25th, 2017
#

import os
import sys
import subprocess

import pandas as pd
import networkx as nx

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
# asap_schedule()
#-------------------------------------------------------------------------
# given a task-graph which is a DAG, returns the asap_labels for the nodes
# in the task-graph

def asap_schedule( tg, source ):
  # initialize all node labels to value 0
  asap_labels = {}
  for node in tg.nodes():
    asap_labels[node] = 0

  # assign the source node a timestamp 1
  asap_labels[source] = 1

  # for each node get the timestamp based on the predecessor value
  for node in tg.nodes():
    # if a label is not assigned
    if asap_labels[node] == 0:
      # get the parents
      parents = tg.predecessors(node)
      # labels for parents
      parent_labels = []
      for parent in parents:
        parent_labels.append( asap_labels[parent] )
      # label the current node
      asap_labels[node] = max( parent_labels ) + 1

  # group the nodes by the assigned label values
  schedule = defaultdict(list)
  for node, label in sorted(asap_labels.iteritems()):
    schedule[label].append(node)
  return schedule

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

def trace_analyze(graph,trace,outdir):
  task_trace_df = pd.read_csv(trace,
                              converters = {
                                'pid'   : lambda x : int( x, 16 ),
                                'tid'   : lambda x : int( x, 16 ),
                                'stype' : lambda x : int( x, 16 ),
                              }
                             )
  task_graph_df = pd.read_csv(graph)
  parallel_regions = task_trace_df['pid'].unique()

  with open("%(outdir)s/trace-analysis.txt" % {'outdir':outdir}, "w") as out:
    for region in parallel_regions:
      trace_df = task_trace_df[task_trace_df['pid']==region]
      graph_df = task_graph_df[task_graph_df['pid']==region]
      region_type = trace_df['ptype'].unique()
      unique_insts = 0
      total_insts = 0
      # data-parallel region
      if region_type == 1:
        nodes = trace_df['tid'].unique()
        strands = {}
        for node in nodes:
          strands[node] = trace_df[trace_df['tid'] == node]['pc'].values.tolist()
        (unique, total) = maximal_sharing( strands )
        unique_insts = unique_insts + unique
        total_insts  = total_insts + total
      # task-parallel region
      else:
        # create a networkx directed graph
        tg = nx.DiGraph()
        # add the edeges based on the task-graph
        tg.add_edges_from(graph_df[['parent','child']].values)

        # get the asap schedule
        schedule = asap_schedule( tg, nx.topological_sort(tg).next() )

        # analyze the trace based on the asap schedule
        for level,nodes in schedule.iteritems():
          traces = trace_df[trace_df['tid'].isin(nodes)]
          strands = {}
          for node in nodes:
            strands[node] = traces[traces['tid'] == node]['pc'].values.tolist()
          (unique, total) = maximal_sharing( strands )
          unique_insts = unique_insts + unique
          total_insts  = total_insts + total

      out.write("Parallel region %(region)s:\n"  % {'region':region})
      out.write("  unique    insts: %(insts)d\n" % {'insts' :unique_insts})
      out.write("  total     insts: %(insts)d\n" % {'insts' :total_insts})
      out.write("  redundant insts: %(insts)d\n" % {'insts' :(total_insts-unique_insts)})
      out.write("  savings: %(savings).2f%%\n" % {'savings':((total_insts-unique_insts)/float(total_insts))*100})
