#============================================================================
# workflow_serial
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

def task_pydgin_serial_sims():

  evaldict = get_base_evaldict()

  evaldict['basename']    = "sim-pydgin-serial"
  evaldict['resultsdir']  = "results-serial-small"
  evaldict['doc']         = os.path.basename(__file__).rstrip('c')

  evaldict['app_group']   = ["small"]
  evaldict['app_list']    = app_serial_list
  evaldict['serial']      = True
  evaldict['app_dict']    = app_dict
  evaldict['cluster']     = True

  yield gen_trace_per_app( evaldict )
