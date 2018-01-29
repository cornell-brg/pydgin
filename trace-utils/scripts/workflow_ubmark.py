#============================================================================
# workflow_ubmark
#============================================================================
# Workflow for ubmark for design-space-exploration of conjoined-cores

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# WSRT
#----------------------------------------------------------------------------

def task_ubmark_conjoined_cores_wsrt():

  l0_buffer_sz = 1
  frontend     = 1

  for smart_sharing in range( 2 ):
    for resources in [2]:
      for lockstep in range( 2 ):
        for analysis in [0,1]:
          for barrier_limit in [1,1000]:

            evaldict = get_base_evaldict()

            # task info
            base_str = "ubmark-wsrt-%dL0-%dF-%dR-%dA-%dL-%dS-limit-%d"
            base_str = base_str % (
              l0_buffer_sz,
              frontend,
              resources,
              analysis,
              lockstep,
              smart_sharing,
              barrier_limit
            )
            evaldict['basename']        = "sim-" + base_str
            evaldict['resultsdir']      = "ubmark/results-" + base_str
            evaldict['doc']             = os.path.basename(__file__).rstrip('c')

            # bmark params
            evaldict['app_group']       = ["mtpull"]
            evaldict['app_list']        = ["ubmark-tpa-vvmult"]
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
            evaldict['lockstep']        = lockstep
            evaldict['barrier_limit']   = barrier_limit
            evaldict['iword_match']     = False
            evaldict['icoalesce']       = bool( smart_sharing )

            # misc params
            evaldict['cluster']         = True
            evaldict['runtime']         = True

            yield gen_trace_per_app( evaldict )
