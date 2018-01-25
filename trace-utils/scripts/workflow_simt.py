#============================================================================
# workflow_simt
#============================================================================
# Workflow for SIMT with four architectures:
#
# 1. SIMT with 1 frontend, no backend constraints and min-sp/pc selection
# 2. SIMT with 2 frontends, no backend constraints and min-sp/pc selection
# 3. SIMT with 1 frontend, 2 resources of everything and min-sp/pc selection
# 4. SIMT with 2 frontends, 2 resources of everything and min-sp/pc selection

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# WSRT
#----------------------------------------------------------------------------

def task_simt_wsrt():

  l0_buffer_sz = 1
  for frontend in [1]:
    for resources in [2,4]:
      for analysis in [0,1]:
        for barrier_limit in [1,1000]:

          evaldict = get_base_evaldict()

          # task info
          base_str = "simt-wsrt-%dL0-%dF-%dR-%dA-limit-%d"
          base_str = base_str % (
            l0_buffer_sz,
            frontend,
            resources,
            analysis,
            barrier_limit
          )
          evaldict['basename']        = "sim-" + base_str
          evaldict['resultsdir']      = "results-" + base_str
          evaldict['doc']             = os.path.basename(__file__).rstrip('c')

          # bmark params
          evaldict['app_group']       = ["small","mtpull"]
          evaldict['app_list']        = app_list
          evaldict['app_dict']        = app_dict

          # uarch params
          evaldict['ncores']          = 4
          evaldict['icache_line_sz']  = 16
          evaldict['dcache_line_sz']  = 16
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

          # misc params
          evaldict['cluster']         = True
          evaldict['runtime']         = True

          yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_simt_spmd():

  l0_buffer_sz = 1
  for frontend in [1]:
    for resources in [2,4]:
      for analysis in [0,1]:
        for barrier_limit in [1,1000]:

          evaldict = get_base_evaldict()

          # task info
          base_str = "simt-spmd-%dL0-%dF-%dR-%dA-limit-%d"
          base_str = base_str % (
            l0_buffer_sz,
            frontend,
            resources,
            analysis,
            barrier_limit
          )
          evaldict['basename']        = "sim-" + base_str
          evaldict['resultsdir']      = "results-" + base_str
          evaldict['doc']             = os.path.basename(__file__).rstrip('c')

          # bmark params
          evaldict['app_group']       = ["small","mt"]
          evaldict['app_list']        = app_list_spmd
          evaldict['app_dict']        = app_dict

          # uarch params
          evaldict['ncores']          = 4
          evaldict['icache_line_sz']  = 16
          evaldict['dcache_line_sz']  = 16
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

          # misc params
          evaldict['cluster']         = True

          yield gen_trace_per_app( evaldict )
