#=========================================================================
# analyze-results.py
#=========================================================================
# Quick and dirty script to analyze data
#
# Author : Shreesha Srinath
# Date   : January 4th, 2018

import re
import math
import sys

import pandas as pd

from common import *

#-------------------------------------------------------------------------
# analyze_imix()
#-------------------------------------------------------------------------

def describe_insn_type( app, df, insn_type ):
  temp = df[df.app == app][[insn_type]].describe().T
  temp.insert(loc=0,column='app',value=app)
  temp.insert(loc=1,column='insn_type',value=insn_type)
  return temp

def analyze_imix(absolute=True):

  # concatenate all the result csv files
  df_list = []
  for res_file in insn_file_list:
    df_list.append( pd.read_csv( res_file ) )
  df = pd.concat(df_list)

  # calculate percent breakdowns
  if not absolute:
    df.loc[:,['integer','load','store','amo','mdu','fpu']] = df.loc[:,['integer','load','store','amo','mdu','fpu']].div(df.total, axis=0)
    df.loc[:,['integer','load','store','amo','mdu','fpu']] = df.loc[:,['integer','load','store','amo','mdu','fpu']].multiply(100, axis=0)

  # analyze the values for each application
  new_df = pd.DataFrame()
  for app in app_list:
    new_df = new_df.append( describe_insn_type( app, df, "integer" ) )
    new_df = new_df.append( describe_insn_type( app, df, "load" ) )
    new_df = new_df.append( describe_insn_type( app, df, "store" ) )
    new_df = new_df.append( describe_insn_type( app, df, "amo" ) )
    new_df = new_df.append( describe_insn_type( app, df, "mdu" ) )
    new_df = new_df.append( describe_insn_type( app, df, "fpu" ) )

  new_df.to_csv("test.csv", index=False)

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  analyze_imix()
