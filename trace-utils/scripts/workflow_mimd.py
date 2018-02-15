#============================================================================
# workflow_mimd
#============================================================================
# Workflow for the MIMD baseline with an L0 buffer and coalescing enabled

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# WSRT
#----------------------------------------------------------------------------

def task_mimd_wsrt():

  ncores        = 4
  l0_buffer_sz  = 1
  barrier_delta = 50

  for barrier_limit in [1,1000]:
    for adaptive_hint in range( 2 ):

      evaldict = get_base_evaldict()

      # task info
      evaldict['basename']        = "sim-mimd-wsrt-limit-%d-%dAH" % ( barrier_limit, adaptive_hint )
      evaldict['resultsdir']      = "four-core-pbbs/results-mimd-wsrt-limit-%d-%dAH" % ( barrier_limit, adaptive_hint )
      evaldict['doc']             = os.path.basename(__file__).rstrip('c')

      # bmark params
      evaldict['app_group']       = ["small","mtpull"]
      evaldict['app_list']        = app_list
      evaldict['app_dict']        = app_dict

      # uarch params
      evaldict['barrier_limit']   = barrier_limit
      evaldict['ncores']          = ncores
      evaldict['l0_buffer_sz']    = l0_buffer_sz
      evaldict['icache_line_sz']  = ncores*4
      evaldict['dcache_line_sz']  = ncores*4
      evaldict['inst_ports']      = ncores
      evaldict['data_ports']      = ncores
      evaldict['mdu_ports']       = ncores
      evaldict['fpu_ports']       = ncores
      evaldict['iword_match']     = False
      evaldict['adaptive_hint']   = bool( adaptive_hint )
      evaldict['barrier_delta']   = barrier_delta

      # misc params
      evaldict['cluster']         = True
      evaldict['runtime']         = True

      yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_mimd_spmd():

  ncores        = 4
  l0_buffer_sz  = 1
  barrier_delta = 50

  for barrier_limit in [1,1000]:
    for adaptive_hint in range( 2 ):

      evaldict = get_base_evaldict()

      # task info
      evaldict['basename']        = "sim-mimd-spmd-limit-%d-%dAH" % ( barrier_limit, adaptive_hint )
      evaldict['resultsdir']      = "four-core-pbbs/results-mimd-spmd-limit-%d-%dAH" % ( barrier_limit, adaptive_hint )
      evaldict['doc']             = os.path.basename(__file__).rstrip('c')

      # bmark params
      evaldict['app_group']       = ["small","mt"]
      evaldict['app_list']        = app_list_spmd
      evaldict['app_dict']        = app_dict

      # uarch params
      evaldict['barrier_limit']   = barrier_limit
      evaldict['ncores']          = ncores
      evaldict['l0_buffer_sz']    = l0_buffer_sz
      evaldict['icache_line_sz']  = ncores*4
      evaldict['dcache_line_sz']  = ncores*4
      evaldict['inst_ports']      = ncores
      evaldict['data_ports']      = ncores
      evaldict['mdu_ports']       = ncores
      evaldict['fpu_ports']       = ncores
      evaldict['iword_match']     = False
      evaldict['adaptive_hint']   = bool( adaptive_hint )
      evaldict['barrier_delta']   = barrier_delta

      # misc params
      evaldict['cluster']         = True

      yield gen_trace_per_app( evaldict )
