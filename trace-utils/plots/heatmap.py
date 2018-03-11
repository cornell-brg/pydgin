import re
import pandas as pd
pd.set_option('display.width', 1000)

from collections import defaultdict

from common import *
from common_configs import *

def score_configs( configs ):
  score = {}
  score['-1C-']   = 0
  score['-1TS-']  = 0
  score['-1LO-']  = 0
  score['-1000-'] = 0
  # coalescing,ts,lockstep,hint
  for cfg in configs:
    for key in score.iterkeys():
      if re.search( key, cfg ):
        score[key] += 1
  num_configs = float( len( configs ) )
  for key in score.iterkeys():
    score[key] /= num_configs
  return score

def summarize_scores( *scores ):
  summary = defaultdict(float)
  for score in scores:
    for knob,value in score.iteritems():
      summary[knob] += value
  num_scores = len( scores )
  for key in summary.iterkeys():
    summary[key] /= num_scores
  return summary

if __name__ == "__main__":

  # select runtime of interest
  runtime = "spmd"

  # get the pareto optimal data frame
  df = pd.read_csv("pareto_configs.csv")

  # filter the df to contain only the required runtime
  df = df.loc[df.runtime.str.contains(runtime)]

  # get all the groups
  group_dict = populate_configs()

  # Nested-data structure that organized scores based on a group and an app
  # within a group
  scores_dict = defaultdict(dict)
  # iterate through each group
  for group in group_dict.keys():
    for app in app_list:
      try:
        # select group and app of interest
        stats = df.loc[(df.group.str.contains(group)) & (df.app == app)]
        pareto_configs = stats.config.tolist()
        scores_dict[group][app] = score_configs( pareto_configs )
      except:
        continue

  #app = 'mriq'
  #for group in group_dict.keys():
  #  print app, group
  #  pareto_configs = df.loc[(df.group.str.contains(group)) & (df.app == app)].config.tolist()
  #  for cfg in pareto_configs:
  #    print "  ", cfg
  #  print "Score:", scores_dict[group][app]

  # summarize for each group
  for group in group_dict.keys():
    scores_list = []
    for app in app_list:
      try:
        pareto_configs = df.loc[(df.group.str.contains(group)) & (df.app == app)].config.tolist()
        scores_list.append( scores_dict[group][app] )
      except:
        continue
    print "Summary for group: ", group
    print "  ", summarize_scores( *scores_list )

  ## summarize app
  #scores_list = []
  #app = ['bilateral']
  #for group in group_dict.keys():
  #  scores_list.append( scores_dict[group][app] )
  #print "mriq summary"
  #print summarize_scores( *scores_list )
