#! /usr/bin/env python
#============================================================================
# doit_pydgin_utils
#============================================================================

from doit.tools import create_folder

from app_paths import *
from doit_utils import *

import sys
sys.path.extend(['../tools'])

import os

from trace_analysis import *

#----------------------------------------------------------------------------
# Tasks
#----------------------------------------------------------------------------
# NOTE: All paths are changed to be absolute paths for cluster job
# submission

curr_dir       = os.path.dirname(__file__)        # Directory from where the script is called
evaldir        = os.path.join( curr_dir, '..' )   # Evaluation directory
scriptsdir     = evaldir + '/tools'               # Scripts directory
appdir         = os.path.join( curr_dir, 'links') # App binaries directory
appinputdir    = appdir  + '/inputs'              # App inputs directory
cpptoolsdir    = scriptsdir + '/cpptools'         # C++ tools directory
tools_builddir = evaldir + "/build-tools"         # Build dir for C++ tools

#----------------------------------------------------------------------------
# get_labeled_apps()
#----------------------------------------------------------------------------
# Returns a list of labeled apps. Apps are labeled distinctly by
# their group in app_dict and by number if there are several sets of
# app_options. Only apps in app_list are returned.

def get_labeled_apps(app_dict, app_list, app_group):

  labeled_apps   = []

  for app in app_dict.keys():
    # Only sim the apps in app_list:
    if app not in app_list:
      continue
    # For each app group in app_dict[app]
    for group, app_opts_list in app_dict[app].iteritems():
      # Only sim the apps in app_group:
      if group not in app_group:
        continue
      # For each set of app options
      for i, app_opts in enumerate(app_opts_list):
        # Label specially if more than one set of app_opts
        label       = '-' + str(i) if i > 0 else ''
        labeled_app = app + '-' + group + label
        labeled_apps.append( labeled_app )

  labeled_apps = sorted(labeled_apps)

  return labeled_apps


#----------------------------------------------------------------------------
# task_build_tools():
#----------------------------------------------------------------------------

def task_build_tools():
  target   = evaldir + "/build-tools/trace-analyze"
  file_dep = get_files_in_dir( cpptoolsdir )

  action = ' '.join( [
    'cd {};'.format(tools_builddir),
    'g++ -O3 -o trace-analyze ',
    '-I ../tools/cpptools {}/trace-analyze.cc -lpthread'.format(cpptoolsdir),
  ] )

  taskdict = {
    'basename' : 'build-tools',
    'actions'  : [ (create_folder, [tools_builddir]), action ],
    'file_dep' : file_dep,
    'targets'  : [ target ]
  }

  return taskdict

#----------------------------------------------------------------------------
# task_link_apps()
#----------------------------------------------------------------------------
# Link application binaries to one directory. This uses the application
# binary paths imported from app_paths.py.

def task_link_apps():

  # Link all app binaries (i.e., files that have no extension) to one place

  action = 'mkdir -p ' + appdir + '; rm -rf ' + appdir + '/*; '
  for path in paths_to_app_binaries:
    action += '; '.join([ 'for x in $(ls -1 ' + path + ' | grep -v -e "\.")',
                          'do ln -s ' + path + '/$x ' + appdir + ' 2> /dev/null',
                          'done; ' ])

  taskdict = { \
    'basename' : 'link-apps',
    'actions'  : [ action ],
    'uptodate' : [ False ], # always re-execute
    'doc'      : os.path.basename(__file__).rstrip('c'),
    }

  return taskdict

#----------------------------------------------------------------------------
# task_runtime_md()
#----------------------------------------------------------------------------

def task_runtime_md():

  action = '../tools/parse-runtime-symbols links'

  taskdict = {
    'basename' : 'runtime-md',
    'actions'  : [ action ],
    'task_dep' : [ 'link-apps' ],
    'uptodate' : [ False ], # always re-execute
    'doc'      : os.path.basename(__file__).rstrip('c'),
  }

  return taskdict

#----------------------------------------------------------------------------
# submit_job()
#----------------------------------------------------------------------------
# helper script to submit a job on the cluster

def submit_job( cmd, name, folder ):
  import clusterjob
  jobscript = clusterjob.JobScript(
    body     = cmd,
    jobname  = name,
    backend  = 'pbs',
    queue    = 'batch',
    threads  = 1,
    ppn      = 1,
    filename = folder + "/" + name + ".pbs",
    stdout   = folder + "/" + name + "-qsub.out",
    stderr   = folder + "/" + name + "-qsub.err",
    time     = "24:00:00",
  )
  jobscript.submit()

#----------------------------------------------------------------------------
# get_base_evaldict()
#----------------------------------------------------------------------------

def get_base_evaldict():

  # Default task options
  doc         = 'Basic configuration'
  basename    = 'unnamed'
  resultsdir  = 'results'
  evaldict    = {}

  evaldict['app_group']       = []    # Which group of apps to sim (e.g., ['scalar'])
  evaldict['app_list']        = []    # List of apps to sim
  evaldict['app_dict']        = {}    # Dict with app groups/opts to run
  evaldict['runtime']         = False # Do not pass runtime-md flag
  evaldict['ncores']          = 4     # Number of cores to simulate
  evaldict['l0_buffer_sz']    = 1     # Number of l0 buffer line sizes
  evaldict['icache_line_sz']  = 0     # Icache line sz in bytes
  evaldict['dcache_line_sz']  = 0     # Dcache line sz in bytes
  evaldict['inst_ports']      = 4     # Number of ports for instruction fetch
  evaldict['data_ports']      = 4     # Number of ports for data memory
  evaldict['mdu_ports']       = 4     # Number of ports for mdu
  evaldict['fpu_ports']       = 4     # Number of ports for fpu
  evaldict['analysis']        = 0     # Reconvergence analysis type
  evaldict['lockstep']        = False # Lockstepp enable flag
  evaldict['linetrace']       = False # Linetrace enable flag
  evaldict['color']           = False # Linetrace colors enable flag
  evaldict['serial']          = False # Flag to indicate serial execution
  evaldict['cluster']         = False # Flag to indicate submission on cluster
  evaldict['extra_app_opts']  = ''    # Up to you, use this to tack on any extra app opts for all apps
  evaldict['icoalesce']       = True  # Turn of instruction coalescing
  evaldict['barrier_limit']   = 1     # Max stall cycles for barrier limit
  evaldict['iword_match']     = True  # Match only word boundaries

  # These params should definitely be overwritten in the workflow
  evaldict['basename']   = basename     # Name of the task
  evaldict['resultsdir'] = resultsdir   # Name of the results directory
  evaldict['doc']        = doc          # Docstring that is printed in 'doit list'

  return evaldict

#----------------------------------------------------------------------------
# Generating task dicts for eval
#----------------------------------------------------------------------------
# Given a app dictionary, yield simulation tasks for doit to find.
#
# Loop and yield a task for:
#
# - for each app in app_dict.keys()
#   - for each app group in app_dict[app]
#     - for each set of app options

def gen_trace_per_app( evaldict ):

  # pydgin simulation configuration params from evaldict
  basename   = evaldict['basename']
  resultsdir = evaldict['resultsdir']
  doc         = evaldict['doc']

  # Yield a docstring subtask
  docstring_taskdict = { \
      'basename' : basename,
      'name'     : None,
      'doc'      : doc,
    }

  yield docstring_taskdict

  # Create path to resultsdir inside evaldir
  resultsdir_path = evaldir + '/' + resultsdir

  #....................................................................
  # Generate subtasks for each app
  #....................................................................
  # Loop and yield a task for:
  #
  # - for each app in app_dict.keys()
  #   - for each app group in app_dict[app]
  #     - for each set of app options

  ncores          = evaldict["ncores"]
  app_dict        = evaldict["app_dict"]
  app_list        = evaldict["app_list"]
  app_group       = evaldict["app_group"]
  runtime_md_flag = evaldict["runtime"]
  inst_ports      = evaldict["inst_ports"]
  l0_buffer_sz    = evaldict["l0_buffer_sz"]
  icache_line_sz  = evaldict["icache_line_sz"]
  dcache_line_sz  = evaldict["dcache_line_sz"]
  data_ports      = evaldict["data_ports"]
  mdu_ports       = evaldict["mdu_ports"]
  fpu_ports       = evaldict["fpu_ports"]
  analysis        = evaldict["analysis"]
  lockstep        = evaldict["lockstep"]
  linetrace       = evaldict["linetrace"]
  color           = evaldict["color"]
  serial          = evaldict["serial"]
  icoalesce       = evaldict["icoalesce"]
  iword_match     = evaldict["iword_match"]
  barrier_limit   = evaldict["barrier_limit"]

  # default options for serial code
  if serial:
    ncores         = 1
    inst_ports     = 1
    data_ports     = 1
    mdu_ports      = 1
    fpu_ports      = 1
    icache_line_sz = 0
    dcache_line_sz = 0

  # NOTE: All paths are changed to be absolute paths for cluster job submission
  pydgin_binary = os.path.join( curr_dir, "../../scripts/builds/pydgin-parc-nojit-debug" )
  pydgin_opts   = " --ncores %(ncores)s --pkernel %(stow_root)s/maven/boot/pkernel " % { 'ncores' : ncores, 'stow_root' : os.environ['STOW_PKGS_ROOT'] }

  for app in app_dict.keys():
    # Only sim the apps in app_list:
    if app not in app_list:
      continue

    # Path to app binary
    app_binary   = appdir + '/' + app

    # For each app group in app_dict[app]
    for group, app_opts_list in app_dict[app].iteritems():
      # Only sim the apps in app_group:
      if group not in app_group:
        continue

      # For each set of app options
      for i, app_opts in enumerate(app_opts_list):
        # Label specially to accomodate more than one set of app_opts
        label       = '-' + str(i) if i > 0 else ''
        labeled_app = app + '-' + group + label

        #.......................
        # Make paths
        #.......................

        app_results_dir = resultsdir_path + '/' + labeled_app
        app_dumpfile    = app_results_dir + '/' + labeled_app + '.out'
        timestamp_file  = app_results_dir + '/timestamp'

        #.......................
        # App options
        #.......................

        # String substitute app options using the evaldict
        app_opts = app_opts % evaldict
        extra_app_opts = evaldict['extra_app_opts']
        app_opts += ' ' + extra_app_opts

        # Define targets
        targets = [ app_dumpfile, timestamp_file ]

        #........................
        # Assemble pydgin command
        #........................

        # additional pydgin specifc options for task tracing
        extra_pydgin_opts = ""

        if runtime_md_flag:
          extra_pydgin_opts += "--runtime-md %(runtime_md)s " % { 'runtime_md' : appdir+"/"+app+'.nm'}
        if lockstep:
          extra_pydgin_opts += "--lockstep "
        if linetrace:
          extra_pydgin_opts += "--linetrace "
        if color:
          extra_pydgin_opts += "--color "

        if not icoalesce:
          extra_pydgin_opts += "--icoalesce "

        if not iword_match:
          extra_pydgin_opts += "--iword-match "

        extra_pydgin_opts += "--barrier-limit %(barrier_limit)s " % { 'barrier_limit' : barrier_limit }
        extra_pydgin_opts += "--analysis %(analysis)s " % { 'analysis' : analysis }
        extra_pydgin_opts += "--l0-buffer-sz %(l0_buffer_sz)s " % { 'l0_buffer_sz' : l0_buffer_sz }
        extra_pydgin_opts += "--icache-line-sz %(icache_line_sz)s " % { 'icache_line_sz' : icache_line_sz }
        extra_pydgin_opts += "--dcache-line-sz %(dcache_line_sz)s " % { 'dcache_line_sz' : dcache_line_sz }
        extra_pydgin_opts += "--inst-ports %(inst_ports)s " % { 'inst_ports' : inst_ports }
        extra_pydgin_opts += "--data-ports %(data_ports)s " % { 'data_ports' : data_ports }
        extra_pydgin_opts += "--mdu-ports %(mdu_ports)s "   % { 'mdu_ports'  : mdu_ports }
        extra_pydgin_opts += "--fpu-ports %(fpu_ports)s "   % { 'fpu_ports'  : fpu_ports }

        pydgin_cmd = ' '.join([
          # pydgin binary
          pydgin_binary,

          # pydgin options
          pydgin_opts,
          extra_pydgin_opts,

          # app binary and options
          app_binary,
          app_opts,

          # app dumpfile
          '2>&1',
          '| tee',
          app_dumpfile,

        ])

        #.......................
        # assemble for cluster
        #.......................

        cluster = evaldict['cluster']
        if cluster:
          actions = [ (create_folder, [app_results_dir]), (submit_job, [pydgin_cmd, labeled_app, app_results_dir]) ]
        else:
          actions = [ (create_folder, [app_results_dir]), pydgin_cmd ]

        #.......................
        # Build Task Dictionary
        #.......................

        taskdict = { \
            'basename' : basename,
            'name'     : labeled_app,
            'actions'  : actions,
            'targets'  : targets,
            'task_dep' : [ 'runtime-md' ],
            'file_dep' : [ app_binary ],
            'uptodate' : [ True ], # Don't rebuild if targets exists
            'clean'    : [ 'rm -rf {}'.format(app_results_dir) ]
          }

        yield taskdict

  # Yield a cleaner subtask with no action, but cleaning the subtask
  # will remove the entire build_dir
  cleaner_taskdict = { \
      'basename' : basename,
      'name'     : 'clean',
      'actions'  : None,
      'targets'  : [ resultsdir_path ],
      'uptodate' : [ True ],
      'clean'    : [ 'rm -rf {}'.format(resultsdir_path) ],
      'doc'      : 'No action; clean removes {}'.format(resultsdir_path),
    }

  yield cleaner_taskdict
