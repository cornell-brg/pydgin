#============================================================================
# workflow_debug
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

def task_pydgin_sims_debug():

  evaldict = get_base_evaldict()

  # task info
  evaldict['basename']        = "sim-debug"
  evaldict['resultsdir']      = "results-debug"
  evaldict['doc']             = os.path.basename(__file__).rstrip('c')

  # bmark params
  evaldict['app_group']       = ["small","mtpull"]
  evaldict['app_list']        = ['ubmark-vvadd']
  #evaldict['app_list']        = ['bilateral']
  evaldict['app_dict']        = app_dict

  # uarch params
  evaldict['barrier_limit']   = 500
  evaldict['ncores']          = 4
  evaldict['l0_buffer_sz']    = 1
  evaldict['icache_line_sz']  = 16
  evaldict['dcache_line_sz']  = 16
  evaldict['inst_ports']      = 1
  evaldict['data_ports']      = 2
  evaldict['mdu_ports']       = 2
  evaldict['fpu_ports']       = 2
  evaldict['analysis']        = 2
  evaldict['icoalesce']       = True
  evaldict['iword_match']     = False
  evaldict['lockstep']        = False
  evaldict['l0_hybrid']       = True
  #evaldict['extra_app_opts']  = ' --dataset tiny '

  # misc params
  evaldict['cluster']         = True
  evaldict['runtime']         = True

  # debug options
  #evaldict['linetrace']       = True
  evaldict['color']           = True

  yield gen_trace_per_app( evaldict )
