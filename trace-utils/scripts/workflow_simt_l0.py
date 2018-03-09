#============================================================================
# workflow_simt_l0_experiment
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# WSRT
#----------------------------------------------------------------------------

def task_simt_wsrt_l0():

  ncores         = 4
  barrier_delta  = 50
  limit_lockstep = 0
  adaptive_hint  = 0

  for l0_buffer_sz in [0,1]:
    for frontend in [1,2]:
      for resources in [1,2,ncores]:
        if (frontend != resources) and (resources < ncores):
          continue
        for analysis in [0,1]:
          for barrier_limit in [1,1000]:

              evaldict = get_base_evaldict()

              # task info
              base_str = "simt-wsrt-%dL0-%dI-%dF-%dL-%dC-%dTS-%dLO-limit-%d-%dLL-%dAH"
              base_str = base_str % (
                l0_buffer_sz,
                frontend,
                frontend,
                resources,
                1,
                analysis,
                1,
                barrier_limit,
                limit_lockstep,
                adaptive_hint,
              )
              evaldict['basename']        = "sim-l0-" + base_str
              evaldict['resultsdir']      = "l0-results/results-" + base_str
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
              evaldict['inst_ports']      = frontend
              evaldict['data_ports']      = resources
              evaldict['mdu_ports']       = resources
              evaldict['fpu_ports']       = resources
              evaldict['analysis']        = analysis
              evaldict['lockstep']        = 1
              evaldict['barrier_limit']   = barrier_limit
              evaldict['simt']            = True
              evaldict['icoalesce']       = True
              evaldict['iword_match']     = True
              evaldict['limit_lockstep']  = False
              evaldict['adaptive_hint']   = False
              evaldict['barrier_delta']   = barrier_delta

              # misc params
              evaldict['cluster']         = True
              evaldict['runtime']         = True

              yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_simt_spmd_l0():

  ncores         = 4
  barrier_delta  = 50
  limit_lockstep = 0
  adaptive_hint  = 0

  for l0_buffer_sz in [0,1]:
    for frontend in [1,2]:
      for resources in [1,2,ncores]:
        if (frontend != resources) and (resources < ncores):
          continue
        for analysis in [0,1]:
          for barrier_limit in [1,1000]:

              evaldict = get_base_evaldict()

              # task info
              base_str = "simt-spmd-%dL0-%dI-%dF-%dL-%dC-%dTS-%dLO-limit-%d-%dLL-%dAH"
              base_str = base_str % (
                l0_buffer_sz,
                frontend,
                frontend,
                resources,
                1,
                analysis,
                1,
                barrier_limit,
                limit_lockstep,
                adaptive_hint,
              )
              evaldict['basename']        = "sim-l0-" + base_str
              evaldict['resultsdir']      = "l0-results/results-" + base_str
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
              evaldict['inst_ports']      = frontend
              evaldict['data_ports']      = resources
              evaldict['mdu_ports']       = resources
              evaldict['fpu_ports']       = resources
              evaldict['analysis']        = analysis
              evaldict['lockstep']        = 1
              evaldict['barrier_limit']   = barrier_limit
              evaldict['simt']            = True
              evaldict['icoalesce']       = True
              evaldict['iword_match']     = True
              evaldict['limit_lockstep']  = False
              evaldict['adaptive_hint']   = False
              evaldict['barrier_delta']   = barrier_delta

              # misc params
              evaldict['cluster']         = True

              yield gen_trace_per_app( evaldict )
