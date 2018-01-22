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

  for barrier_limit in [1,250]:

    evaldict = get_base_evaldict()

    # task info
    evaldict['basename']        = "sim-mimd-wsrt-%d" % barrier_limit
    evaldict['resultsdir']      = "results-mimd-wsrt-%d" % barrier_limit
    evaldict['doc']             = os.path.basename(__file__).rstrip('c')

    # bmark params
    evaldict['app_group']       = ["small","mtpull"]
    evaldict['app_list']        = app_list
    evaldict['app_dict']        = app_dict

    # uarch params
    evaldict['barrier_limit']   = barrier_limit
    evaldict['ncores']          = 4
    evaldict['l0_buffer_sz']    = 1
    evaldict['icache_line_sz']  = 16
    evaldict['dcache_line_sz']  = 16
    evaldict['inst_ports']      = 4
    evaldict['data_ports']      = 4
    evaldict['mdu_ports']       = 4
    evaldict['fpu_ports']       = 4
    evaldict['iword_match']     = False

    # misc params
    evaldict['cluster']         = True
    evaldict['runtime']         = True

    yield gen_trace_per_app( evaldict )

#----------------------------------------------------------------------------
# SPMD
#----------------------------------------------------------------------------

def task_mimd_spmd():

  for barrier_limit in [1,250]:

    evaldict = get_base_evaldict()

    # task info
    evaldict['basename']        = "sim-mimd-spmd-%d" % barrier_limit
    evaldict['resultsdir']      = "results-mimd-spmd-%d" % barrier_limit
    evaldict['doc']             = os.path.basename(__file__).rstrip('c')

    # bmark params
    evaldict['app_group']       = ["small","mt"]
    evaldict['app_list']        = app_list_spmd
    evaldict['app_dict']        = app_dict

    # uarch params
    evaldict['barrier_limit']   = barrier_limit
    evaldict['ncores']          = 4
    evaldict['l0_buffer_sz']    = 1
    evaldict['icache_line_sz']  = 16
    evaldict['dcache_line_sz']  = 16
    evaldict['inst_ports']      = 4
    evaldict['data_ports']      = 4
    evaldict['mdu_ports']       = 4
    evaldict['fpu_ports']       = 4
    evaldict['iword_match']     = False

    # misc params
    evaldict['cluster']         = True

    yield gen_trace_per_app( evaldict )
