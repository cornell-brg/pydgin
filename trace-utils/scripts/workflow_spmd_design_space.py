#============================================================================
# workflow_spmd_design_space.py
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# spmd design space tasks
#----------------------------------------------------------------------------
# Tasks are named using the following notation:
#
#   basename-Xc-Xl0-Xip-Xdp-Xlp-Xl-Xr
#     c  : cores
#     l0 : l0 buffer size
#     ip : imem ports
#     dp : dmem ports
#     lp : llfu ports
#     l  : lockstep execution for dmem/llfu
#     r  : reconvergence scheme
#

def task_pydgin_sims_spmd_design_space():

  ncores = 4
  for l0_buffer_sz in [1]:
    for ports in range( 1, ncores+1 ):
      for llfus in range( 1, ncores+1  ):
        for lockstep in range( 2 ):
          for analysis in range( 3 ):
            # get an evaluation dictionary
            evaldict = get_base_evaldict()

            # task info
            evaldict['basename']    = "sim-pydgin-spmd-%dc-%dl0-%dip-%ddp-%dlp-%dl-%dr" % ( ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
            evaldict['resultsdir']  = "results-small-spmd-%dc-%dl0-%dip-%ddp-%dlp-%dl-%dr" % ( ncores, l0_buffer_sz, ports, ports, llfus, lockstep, analysis )
            evaldict['doc']         = os.path.basename(__file__).rstrip('c')

            # kernels to run with options
            evaldict['app_group']   = ["small","mt"]
            evaldict['app_list']    = app_list_spmd
            evaldict['app_dict']    = app_dict

            # pydgin options
            evaldict['ncores']         = ncores           # number of cores to simulate
            evaldict['l0_buffer_sz']   = l0_buffer_sz     # l0 buffer size
            evaldict['icache_line_sz'] = 16               # icache line size
            evaldict['inst_ports']     = ports            # instruction port bw
            evaldict['data_ports']     = ports            # data port bw
            evaldict['mdu_ports']      = llfus            # mdu port bw
            evaldict['fpu_ports']      = llfus            # fpu port bw
            evaldict['analysis']       = analysis         # type of reconvergence scheme
            evaldict['lockstep']       = bool( lockstep ) # enable lockstep execution
            evaldict['cluster']        = True             # enable running the job on cluster

            yield gen_trace_per_app( evaldict )


