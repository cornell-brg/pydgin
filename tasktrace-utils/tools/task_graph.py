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

def draw_graph(trace,outdir):
  task_graph_df = pd.read_csv(trace)
  parallel_regions = task_graph_df['pid'].unique()
  for region in parallel_regions:
    with open("%(outdir)s/graph-%(region)s.dot" % {'outdir':outdir,'region':region}, "w") as dot:
      dot.write("digraph G{\n")
      graph_df = task_graph_df[task_graph_df['pid']==region]
      edges_list = graph_df[['parent','child']].values.tolist()
      for edge in edges_list:
        dot.write("  %(p)s->%(c)s;\n" % {'p':edge[0],'c':edge[1]})
      nodes_df = graph_df[['parent','stype']]
      nodes_list = nodes_df.drop_duplicates(subset='parent',keep='last').values.tolist()
      for node in nodes_list:
        dot.write("  %(node)s %(attr)s\n" % {'node':node[0],'attr':g_node_attributes[node[1]]})
      dot.write("}")
    execute("cd %(outdir)s && dot -Tpdf -o graph-%(region)s.pdf graph-%(region)s.dot" % {'outdir':outdir,'region':region})
