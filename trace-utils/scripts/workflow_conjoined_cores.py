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

  ncores        = 4
  l0_buffer_sz  = 1
  barrier_delta = 50

  for insn_ports in [1,2]:
    for smart_sharing in range( 2 ):
      for resources in [1,2,ncores]:
        for lockstep in range( 2 ):
          for limit_lockstep in range( 2 ):
            for analysis in [0,1]:
              for adaptive_hint in range( 2 ):
                for barrier_limit in [1,1000]:

                  evaldict = get_base_evaldict()

                  # task info
                  base_str = "conjoined-cores-wsrt-%dL0-%dI-%dF-%dL-%dC-%dTS-%dLO-limit-%d-%dLL-%dAH"
                  base_str = base_str % (
                    l0_buffer_sz,
                    insn_ports,
                    ncores,
                    resources,
                    smart_sharing,
                    analysis,
                    lockstep,
                    barrier_limit,
                    limit_lockstep,
                    adaptive_hint
                  )
                  evaldict['basename']        = "sim-" + base_str
                  evaldict['resultsdir']      = "four-core-pbbs/results-" + base_str
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
                  evaldict['inst_ports']      = insn_ports
                  evaldict['data_ports']      = resources
                  evaldict['mdu_ports']       = resources
                  evaldict['fpu_ports']       = resources
                  evaldict['analysis']        = analysis
                  evaldict['lockstep']        = lockstep
                  evaldict['barrier_limit']   = barrier_limit
                  evaldict['iword_match']     = False
                  evaldict['icoalesce']       = bool( smart_sharing )
                  evaldict['limit_lockstep']  = bool( limit_lockstep )
                  evaldict['adaptive_hint']   = bool( adaptive_hint )
                  evaldict['barrier_delta']   = barrier_delta

                  # misc params
                  evaldict['cluster']         = True
                  evaldict['runtime']         = True

                  yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_conjoined_cores_spmd():

  ncores        = 4
  l0_buffer_sz  = 1
  barrier_delta = 50

  for insn_ports in [1,2]:
    for smart_sharing in range( 2 ):
      for resources in [1,2,ncores]:
        for lockstep in range( 2 ):
          for limit_lockstep in range( 2 ):
            for analysis in [0,1]:
              for adaptive_hint in range( 2 ):
                for barrier_limit in [1,1000]:

                  evaldict = get_base_evaldict()

                  # task info
                  base_str = "conjoined-cores-spmd-%dL0-%dI-%dF-%dL-%dC-%dTS-%dLO-limit-%d-%dLL-%dAH"
                  base_str = base_str % (
                    l0_buffer_sz,
                    insn_ports,
                    ncores,
                    resources,
                    smart_sharing,
                    analysis,
                    lockstep,
                    barrier_limit,
                    limit_lockstep,
                    adaptive_hint
                  )
                  evaldict['basename']        = "sim-" + base_str
                  evaldict['resultsdir']      = "four-core-pbbs/results-" + base_str
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
                  evaldict['inst_ports']      = insn_ports
                  evaldict['data_ports']      = resources
                  evaldict['mdu_ports']       = resources
                  evaldict['fpu_ports']       = resources
                  evaldict['analysis']        = analysis
                  evaldict['lockstep']        = lockstep
                  evaldict['barrier_limit']   = barrier_limit
                  evaldict['iword_match']     = False
                  evaldict['icoalesce']       = bool( smart_sharing )
                  evaldict['limit_lockstep']  = bool( limit_lockstep )
                  evaldict['adaptive_hint']   = bool( adaptive_hint )
                  evaldict['barrier_delta']   = barrier_delta

                  # misc params
                  evaldict['cluster']         = True

                  yield gen_trace_per_app( evaldict )
