#=========================================================================
# task_graph.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : September 21st, 2017
#
# Given a task-graph.csv, draws a graph in pdf using dot

import csv
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
# g_node_attributes
#-------------------------------------------------------------------------

g_node_attributes = [
  "[fillcolor=\"#f7f7f7\",style=\"filled\"]",
  "[fillcolor=\"#998ec3\",style=\"filled\"]",
]

#-------------------------------------------------------------------------
# draw_graph()
#-------------------------------------------------------------------------

def draw_graph(graph,trace,outdir,draw=False):
  task_graph_df = pd.read_csv(graph)
  task_trace_df = pd.read_csv(trace,
                              converters = {
                                'pid'   : lambda x : int( x, 16 ),
                                'tid'   : lambda x : int( x, 16 ),
                                'stype' : lambda x : int( x, 16 ),
                              }
                             )
  parallel_regions = task_trace_df['pid'].unique()
  for region in parallel_regions:
    if draw:
      with open("%(outdir)s/graph-%(region)s.dot" % {'outdir':outdir,'region':region}, "w") as dot:
        graph_df = task_graph_df[task_graph_df['pid']==region]
        edges_list = graph_df[['parent','child']].values.tolist()

        if len( edges_list ) != 0:
          # sanity checks
          tg = nx.Graph()
          tg.add_edges_from(edges_list)
          # check that it is a connected DAG
          assert( nx.is_connected(tg) )
          # check for self-loops
          assert( nx.number_of_selfloops(tg) == 0 )

        dot.write("digraph G{\n")
        for edge in edges_list:
          dot.write("  %(p)s->%(c)s;\n" % {'p':edge[0],'c':edge[1]})
        trace_df = task_trace_df[task_trace_df['pid']==region]
        nodes_df = trace_df[['tid','stype']]
        nodes_list = nodes_df.drop_duplicates(subset='tid',keep='last').values.tolist()
        for node in nodes_list:
          dot.write("  %(node)s %(attr)s\n" % {'node':node[0],'attr':g_node_attributes[node[1]]})
        dot.write("}")
      execute("cd %(outdir)s && dot -Tpdf -o graph-%(region)s.pdf graph-%(region)s.dot" % {'outdir':outdir,'region':region})
    else:
      graph_df = task_graph_df[task_graph_df['pid']==region]
      edges_list = graph_df[['parent','child']].values.tolist()

      if len( edges_list ) != 0:
        # sanity checks
        tg = nx.Graph()
        tg.add_edges_from(edges_list)
        # check that it is a connected DAG
        assert( nx.is_connected(tg) )
        # check for self-loops
        assert( nx.number_of_selfloops(tg) == 0 )


