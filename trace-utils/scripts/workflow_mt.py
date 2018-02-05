#============================================================================
# workflow_mt
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# WSRT
#----------------------------------------------------------------------------

def task_mt_wsrt():

  ncores        = 8
  l0_buffer_sz  = 1
  barrier_delta = 50

  for analysis in [0,1]:
    for adaptive_hint in range( 2 ):
      for barrier_limit in [1,1000]:

        evaldict = get_base_evaldict()

        # task info
        base_str = "mt-wsrt-%dTS-limit-%d-%dAH"
        base_str = base_str % (
          analysis,
          barrier_limit,
          adaptive_hint
        )
        evaldict['basename']        = "sim-" + base_str
        evaldict['resultsdir']      = "mt-wsrt/results-" + base_str
        evaldict['doc']             = os.path.basename(__file__).rstrip('c')

        # bmark params
        evaldict['app_group']       = ["small","mtpull"]
        evaldict['app_list']        = app_list
        evaldict['app_dict']        = app_dict

        # uarch params
        evaldict['ncores']          = ncores
        evaldict['icache_line_sz']  = ncores*4
        evaldict['dcache_line_sz']  = ncores*4
        evaldict['l0_buffer_sz']    = l0_buffer_sz
        evaldict['inst_ports']      = 1
        evaldict['data_ports']      = 1
        evaldict['mdu_ports']       = 1
        evaldict['fpu_ports']       = 1
        evaldict['analysis']        = analysis
        evaldict['barrier_limit']   = barrier_limit
        evaldict['adaptive_hint']   = bool( adaptive_hint )
        evaldict['barrier_delta']   = barrier_delta
        evaldict['mt']              = True

        # misc params
        evaldict['cluster']         = True
        evaldict['runtime']         = True

        yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_mt_spmd():

  ncores        = 8
  l0_buffer_sz  = 1
  barrier_delta = 50

  for analysis in [0,1]:
    for adaptive_hint in range( 2 ):
      for barrier_limit in [1,1000]:

        evaldict = get_base_evaldict()

        # task info
        base_str = "mt-spmd-%dTS-limit-%d-%dAH"
        base_str = base_str % (
          analysis,
          barrier_limit,
          adaptive_hint
        )
        evaldict['basename']        = "sim-" + base_str
        evaldict['resultsdir']      = "mt-spmd/results-" + base_str
        evaldict['doc']             = os.path.basename(__file__).rstrip('c')

        # bmark params
        evaldict['app_group']       = ["small","mt"]
        evaldict['app_list']        = app_list_spmd
        evaldict['app_dict']        = app_dict

        # uarch params
        evaldict['ncores']          = ncores
        evaldict['icache_line_sz']  = ncores*4
        evaldict['dcache_line_sz']  = ncores*4
        evaldict['l0_buffer_sz']    = l0_buffer_sz
        evaldict['inst_ports']      = 1
        evaldict['data_ports']      = 1
        evaldict['mdu_ports']       = 1
        evaldict['fpu_ports']       = 1
        evaldict['analysis']        = analysis
        evaldict['barrier_limit']   = barrier_limit
        evaldict['adaptive_hint']   = bool( adaptive_hint )
        evaldict['barrier_delta']   = barrier_delta
        evaldict['mt']              = True

        # misc params
        evaldict['cluster']         = True

        yield gen_trace_per_app( evaldict )
