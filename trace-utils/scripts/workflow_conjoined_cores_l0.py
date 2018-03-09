#============================================================================
# workflow_conjoined_cores_l0_experiment
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# WSRT
#----------------------------------------------------------------------------

def task_conjoined_cores_l0_wsrt():

  ncores         = 4
  limit_lockstep = 0
  adaptive_hint  = 0

  for l0_buffer_sz in [0,1]:
    for coalescing in range( 2 ):
      for barrier_limit in [1,1000]:
        if coalescing == 0 and barrier_limit == 1000:
          continue
        for insn_ports in [1,2]:
          for resources in [1,2,ncores]:
            if (insn_ports != resources) and (resources < ncores):
              continue
            for lockstep in range( 2 ):
              for analysis in [0,1]:
                evaldict = get_base_evaldict()

                # task info
                base_str = "conjoined-cores-wsrt-%dL0-%dI-%dF-%dL-%dC-%dTS-%dLO-limit-%d-%dLL-%dAH"
                base_str = base_str % (
                  l0_buffer_sz,
                  insn_ports,
                  ncores,
                  resources,
                  coalescing,
                  analysis,
                  lockstep,
                  barrier_limit,
                  limit_lockstep,
                  adaptive_hint
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
                evaldict['inst_ports']      = insn_ports
                evaldict['data_ports']      = resources
                evaldict['mdu_ports']       = resources
                evaldict['fpu_ports']       = resources
                evaldict['analysis']        = analysis
                evaldict['lockstep']        = lockstep
                evaldict['barrier_limit']   = barrier_limit
                evaldict['iword_match']     = False
                evaldict['icoalesce']       = bool( coalescing )
                evaldict['limit_lockstep']  = False
                evaldict['adaptive_hint']   = False
                evaldict['barrier_delta']   = 50

                # misc params
                evaldict['cluster']         = True
                evaldict['runtime']         = True

                yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_conjoined_cores_l0_spmd():

  ncores         = 4
  limit_lockstep = 0
  adaptive_hint  = 0

  for l0_buffer_sz in [0,1]:
    for coalescing in range( 2 ):
      for barrier_limit in [1,1000]:
        if coalescing == 0 and barrier_limit == 1000:
          continue
        for insn_ports in [1,2]:
          for resources in [1,2,ncores]:
            if (insn_ports != resources) and (resources < ncores):
              continue
            for lockstep in range( 2 ):
              for analysis in [0,1]:
                evaldict = get_base_evaldict()

                # task info
                base_str = "conjoined-cores-spmd-%dL0-%dI-%dF-%dL-%dC-%dTS-%dLO-limit-%d-%dLL-%dAH"
                base_str = base_str % (
                  l0_buffer_sz,
                  insn_ports,
                  ncores,
                  resources,
                  coalescing,
                  analysis,
                  lockstep,
                  barrier_limit,
                  limit_lockstep,
                  adaptive_hint
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
                evaldict['inst_ports']      = insn_ports
                evaldict['data_ports']      = resources
                evaldict['mdu_ports']       = resources
                evaldict['fpu_ports']       = resources
                evaldict['analysis']        = analysis
                evaldict['lockstep']        = lockstep
                evaldict['barrier_limit']   = barrier_limit
                evaldict['iword_match']     = False
                evaldict['icoalesce']       = bool( coalescing )
                evaldict['limit_lockstep']  = False
                evaldict['adaptive_hint']   = False
                evaldict['barrier_delta']   = 50

                # misc params
                evaldict['cluster']         = True

                yield gen_trace_per_app( evaldict )
