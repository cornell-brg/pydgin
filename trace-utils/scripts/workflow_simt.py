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

  for l0_buffer_sz in [1]:
    for frontend in [1,2]:
      for resources in [2,4]:
        for analysis in range( 3 ):
          for barrier_limit in [1,500,1000]:

            evaldict = get_base_evaldict()

            # task info
            evaldict['basename']        = "sim-simt-wsrt-%d-%d-%d-%d-limit-%d" % ( l0_buffer_sz, frontend, resources, analysis, barrier_limit )
            evaldict['resultsdir']      = "results-simt-wsrt-%d-%d-%d-%d-limit-%d" % ( l0_buffer_sz, frontend, resources, analysis, barrier_limit )
            evaldict['doc']             = os.path.basename(__file__).rstrip('c')

            # bmark params
            evaldict['app_group']       = ["small","mtpull"]
            evaldict['app_list']        = app_list
            evaldict['app_dict']        = app_dict

            # uarch params
            evaldict['barrier_limit']   = barrier_limit
            evaldict['ncores']          = 4
            evaldict['l0_buffer_sz']    = l0_buffer_sz
            evaldict['icache_line_sz']  = 16
            evaldict['dcache_line_sz']  = 16
            evaldict['inst_ports']      = frontend
            evaldict['data_ports']      = resources
            evaldict['mdu_ports']       = resources
            evaldict['fpu_ports']       = resources
            evaldict['iword_match']     = True
            evaldict['analysis']        = analysis
            evaldict['lockstep']        = True
            evaldict['simt']            = True

            # misc params
            evaldict['cluster']         = True
            evaldict['runtime']         = True

            yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_simt_spmd():

  for l0_buffer_sz in range( 2 ):
    for frontend in [1,2]:
      for resources in [2,4]:
        for analysis in range( 3 ):
          for barrier_limit in [1,500,1000]:

            evaldict = get_base_evaldict()

            # task info
            evaldict['basename']        = "sim-simt-spmd-%d-%d-%d-%d-limit-%d" % ( l0_buffer_sz, frontend, resources, analysis, barrier_limit )
            evaldict['resultsdir']      = "results-simt-spmd-%d-%d-%d-%d-limit-%d" % ( l0_buffer_sz, frontend, resources, analysis, barrier_limit )
            evaldict['doc']             = os.path.basename(__file__).rstrip('c')

            # bmark params
            evaldict['app_group']       = ["small","mt"]
            evaldict['app_list']        = app_list_spmd
            evaldict['app_dict']        = app_dict

            # uarch params
            evaldict['barrier_limit']   = barrier_limit
            evaldict['ncores']          = 4
            evaldict['l0_buffer_sz']    = l0_buffer_sz
            evaldict['icache_line_sz']  = 16
            evaldict['dcache_line_sz']  = 16
            evaldict['inst_ports']      = frontend
            evaldict['data_ports']      = resources
            evaldict['mdu_ports']       = resources
            evaldict['fpu_ports']       = resources
            evaldict['iword_match']     = True
            evaldict['analysis']        = analysis
            evaldict['lockstep']        = True
            evaldict['simt']            = True

            # misc params
            evaldict['cluster']         = True

            yield gen_trace_per_app( evaldict )
