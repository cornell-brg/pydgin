#============================================================================
# workflow_spmd_similarity
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *


def task_spmd_similarity():

  for barrier_limit in [1,250]:

    evaldict = get_base_evaldict()

    # task info
    evaldict['basename']        = "sim-spmd-similarity-limit-%d" % barrier_limit
    evaldict['resultsdir']      = "results-spmd-similarity-limit-%d" % barrier_limit
    evaldict['doc']             = os.path.basename(__file__).rstrip('c')

    # bmark params
    evaldict['app_group']       = ["small","mt"]
    evaldict['app_list']        = app_list_spmd
    evaldict['app_dict']        = app_dict

    # uarch params
    evaldict['barrier_limit']   = barrier_limit
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

    yield gen_trace_per_app( evaldict )
