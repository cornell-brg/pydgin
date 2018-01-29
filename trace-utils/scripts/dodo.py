#! /usr/bin/env python
#============================================================================
# dodo
#============================================================================
# Template dodo file with reporter that outputs task actions as strings.
#
# Author : Shreesha Srinath
# Date   : September 16th, 2017

from doit.task  import clean_targets
from doit.tools import check_timestamp_unchanged
from doit.tools import create_folder

from apps import *
from doit_utils import *
from doit_pydgin_utils import *

#----------------------------------------------------------------------------
# Config
#----------------------------------------------------------------------------

DOIT_CONFIG = {
  'reporter' : MyReporter,
}

#----------------------------------------------------------------------------
# serial runs
#----------------------------------------------------------------------------

from workflow_serial import *

#----------------------------------------------------------------------------
# wsrt design space tasks
#----------------------------------------------------------------------------

#from workflow_wsrt_design_space import *

#----------------------------------------------------------------------------
# spmd design space tasks
#----------------------------------------------------------------------------

#from workflow_spmd_design_space import *

#----------------------------------------------------------------------------
# debug tasks
#----------------------------------------------------------------------------

from workflow_debug import *

#----------------------------------------------------------------------------
# plot
#----------------------------------------------------------------------------

from workflow_plot import *

#----------------------------------------------------------------------------
# wsrt similarity
#----------------------------------------------------------------------------

from workflow_wsrt_similarity import *

#----------------------------------------------------------------------------
# spmd similarity
#----------------------------------------------------------------------------

from workflow_spmd_similarity import *

#----------------------------------------------------------------------------
# MIMD
#----------------------------------------------------------------------------

from workflow_mimd import *

#----------------------------------------------------------------------------
# Conjoined cores
#----------------------------------------------------------------------------

from workflow_conjoined_cores import *

#----------------------------------------------------------------------------
# SIMT
#----------------------------------------------------------------------------

from workflow_simt import *

#----------------------------------------------------------------------------
# UBMARK
#----------------------------------------------------------------------------

from workflow_ubmark import *

def task_ubmark_pydgin_serial_sim():

  evaldict = get_base_evaldict()

  evaldict['basename']    = "sim-ubmark-serial"
  evaldict['resultsdir']  = "ubmark/results-serial"
  evaldict['doc']         = os.path.basename(__file__).rstrip('c')

  evaldict['app_group']   = ["scalar"]
  evaldict['app_list']    = ["ubmark-tpa-vvmult"]
  evaldict['serial']      = True
  evaldict['app_dict']    = app_dict
  evaldict['cluster']     = True

  yield gen_trace_per_app( evaldict )
