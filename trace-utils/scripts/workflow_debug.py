#============================================================================
# workflow_debug
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

def task_pydgin_sims_debug():

  ncores       = 4
  l0_buffer_sz = 1
  ports        = 4
  llfus        = 4
  lockstep     = 1
  analysis     = 1

  # get an evaluation dictionary
  evaldict = get_base_evaldict()

  # task info
  evaldict['basename']    = "sim-pydgin-debug"
  evaldict['resultsdir']  = "results-debug"
  evaldict['doc']         = os.path.basename(__file__).rstrip('c')

  # kernels to run with options
  evaldict['app_group']   = ["tiny","mtpull"]
  #evaldict['app_list']    = ['cilk-matmul-parc-mtpull']
  #evaldict['app_list']    = ['pbbs-bfs-ndBFS-parc-mtpull']
  evaldict['app_list']    = ['ubmark-vvadd']
  evaldict['app_dict']    = app_dict

  # pydgin options
  evaldict['ncores']         = ncores           # number of cores to simulate
  evaldict['inst_ports']     = ports            # instruction port bw
  evaldict['l0_buffer_sz']   = l0_buffer_sz     # l0 buffer size
  evaldict['icache_line_sz'] = 16               # icache line size
  evaldict['data_ports']     = ports            # data port bw
  evaldict['mdu_ports']      = llfus            # mdu port bw
  evaldict['fpu_ports']      = llfus            # fpu port bw
  evaldict['analysis']       = analysis         # type of reconvergence scheme
  evaldict['lockstep']       = bool( lockstep ) # enable lockstep execution
  evaldict['cluster']        = True             # enable running the job on cluster
  evaldict['runtime']        = True             # provide runtime metadata
  evaldict['extra_app_opts'] = "--verify"

  # debug options
  evaldict['linetrace']   = True
  evaldict['color']       = True

  yield gen_trace_per_app( evaldict )


