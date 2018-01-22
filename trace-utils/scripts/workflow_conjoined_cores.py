#============================================================================
# workflow_conjoined_cores
#============================================================================
# Workflow for conjoined cores with two configurations:
#
# 1. Conjoined cores with 1 resource of everything and min-sp/pc selection
# 2. Conjoined cores with 2 resources of everything and min-sp/pc selection

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# WSRT
#----------------------------------------------------------------------------

def task_conjoined_cores_wsrt():

  for resources in [1,2]:
    for barrier_limit in [1,250]:

      evaldict = get_base_evaldict()

      # task info
      evaldict['basename']        = "sim-conjoined-cores-wsrt-%d-limit-%d" % ( resources, barrier_limit )
      evaldict['resultsdir']      = "results-conjoined-cores-wsrt-%d-limit-%d" % ( resources, barrier_limit )
      evaldict['doc']             = os.path.basename(__file__).rstrip('c')

      # bmark params
      evaldict['app_group']       = ["small","mtpull"]
      evaldict['app_list']        = app_list
      evaldict['app_dict']        = app_dict

      # uarch params
      evaldict['barrier_limit']   = barrier_limit
      evaldict['ncores']          = 4
      evaldict['l0_buffer_sz']    = 1
      evaldict['icache_line_sz']  = 16
      evaldict['dcache_line_sz']  = 16
      evaldict['inst_ports']      = resources
      evaldict['data_ports']      = resources
      evaldict['mdu_ports']       = resources
      evaldict['fpu_ports']       = resources
      evaldict['iword_match']     = False
      evaldict['analysis']        = 2

      # misc params
      evaldict['cluster']         = True
      evaldict['runtime']         = True

      yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_conjoined_cores_spmd():

  for resources in [1,2]:
    for barrier_limit in [1,250]:

      evaldict = get_base_evaldict()

      # task info
      evaldict['basename']        = "sim-conjoined-cores-spmd-%d-limit-%d" % ( resources, barrier_limit )
      evaldict['resultsdir']      = "results-conjoined-cores-spmd-%d-limit-%d" % ( resources, barrier_limit )
      evaldict['doc']             = os.path.basename(__file__).rstrip('c')

      # bmark params
      evaldict['app_group']       = ["small","mt"]
      evaldict['app_list']        = app_list_spmd
      evaldict['app_dict']        = app_dict

      # uarch params
      evaldict['barrier_limit']   = barrier_limit
      evaldict['ncores']          = 4
      evaldict['l0_buffer_sz']    = 1
      evaldict['icache_line_sz']  = 16
      evaldict['dcache_line_sz']  = 16
      evaldict['inst_ports']      = resources
      evaldict['data_ports']      = resources
      evaldict['mdu_ports']       = resources
      evaldict['fpu_ports']       = resources
      evaldict['iword_match']     = False
      evaldict['analysis']        = 2

      # misc params
      evaldict['cluster']         = True

      yield gen_trace_per_app( evaldict )
