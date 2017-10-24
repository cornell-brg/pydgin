#! /usr/bin/env python
#============================================================================
# dodo
#============================================================================
# Template dodo file with reporter that outputs task actions as strings.
#
# Author : Shreesha Srinath
# Date   : September 16th, 2017

from doit.task  import clean_targets
from doit.tools import check_timestamp_unchanged
from doit.tools import create_folder

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# Config
#----------------------------------------------------------------------------

DOIT_CONFIG = {
  'reporter' : MyReporter,
}

#----------------------------------------------------------------------------
# Tasks
#----------------------------------------------------------------------------

def task_pydgin_sims():

  evaldict = get_base_evaldict()

  evaldict['basename']    = "sim-pydgin"
  evaldict['resultsdir']  = "results"
  evaldict['doc']         = os.path.basename(__file__).rstrip('c')

  evaldict['app_group']   = ["small","mtpull"]
  evaldict['app_list']    = app_list
  evaldict['app_dict']    = app_dict

  yield gen_trace_per_app( evaldict )

def task_pydgin_ksack():

  evaldict = get_base_evaldict()

  evaldict['basename']    = "sim-pydgin-ksack"
  evaldict['resultsdir']  = "results-ksack"
  evaldict['doc']         = os.path.basename(__file__).rstrip('c')

  evaldict['app_group']   = ["small","mtpull"]
  evaldict['app_list']    = ['cilk-knapsack-parc-mtpull']
  evaldict['app_dict']    = app_dict

  yield gen_trace_per_app( evaldict )
