#============================================================================
# workflow_plot
#============================================================================

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

def task_pydgin_plot():

  plotdict = get_base_plotdict()

  # task info
  plotdict['basename']    = "plot-debug"

  # IMPORTANT: The results directoru should match the correct location!
  plotdict['resultsdir']  = "results-debug"
  plotdict['doc']         = os.path.basename(__file__).rstrip('c')

  # bmark params
  plotdict['app_group']   = ["small","mtpull"]
  #plotdict['app_list']    = ['bilateral']
  plotdict['app_list']    = ['uts']
  plotdict['app_dict']    = app_dict
  plotdict['time_slice']  = "0:30000"

  yield gen_plot_per_app( plotdict )
