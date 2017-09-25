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

  #timestep = max( asap_labels.values() )
  #for timestep in xrange(1,timestep+1):
  #  print "Cycle: [",
  #  for node,cycle in asap_labels.iteritems():
  #    if cycle == timestep:
  #      print node,
  #  print "]"

  return asap_labels

#-------------------------------------------------------------------------
# trace_analyze()
#-------------------------------------------------------------------------

def trace_analyze(trace,graph):
  trace_df = pd.read_csv(trace)
  graph_df = pd.read_csv(graph)

  # create a networkx directed graph
  tg = nx.DiGraph()
  # add the edeges based on the task-graph
  tg.add_edges_from(graph_df[['parent','child']].values)

  # get the asap schedule
  asap_labels = asap_schedule( tg,  nx.topological_sort(tg).next() )
