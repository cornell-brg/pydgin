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
  evaldict['app_group']       = ["tiny","mtpull"]
  evaldict['app_list']        = ['cilk-heat-parc-mtpull']
  evaldict['app_dict']        = app_dict

  # uarch params
  evaldict['barrier_limit']   = 250
  evaldict['ncores']          = 4
  evaldict['l0_buffer_sz']    = 0
  evaldict['icache_line_sz']  = 16
  evaldict['dcache_line_sz']  = 16
  evaldict['inst_ports']      = 4
  evaldict['data_ports']      = 4
  evaldict['mdu_ports']       = 4
  evaldict['fpu_ports']       = 4
  evaldict['analysis']        = 1

  # misc params
  evaldict['cluster']         = False
  evaldict['runtime']         = True

  # debug options
  evaldict['linetrace']       = True
  evaldict['color']           = True

  yield gen_trace_per_app( evaldict )
