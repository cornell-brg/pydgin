#! /usr/bin/env python
#============================================================================
# doit_pydgin_utils
#============================================================================

from doit.tools import create_folder

from app_paths import *
from doit_utils import *

import sys
sys.path.extend(['../tools'])

from task_regs import *
from task_trace_annotate import *
from disassemble import *
from task_graph import *
from task_trace_analysis import *

#----------------------------------------------------------------------------
# Tasks
#----------------------------------------------------------------------------

# Paths

evaldir        = '..'                            # Evaluation directory
scriptsdir     = evaldir + '/tools'              # Scripts directory
appdir         = 'links'                         # App binaries directory
appinputdir    = appdir  + '/inputs'             # App inputs directory
cpptoolsdir    = scriptsdir + '/cpptools'        # C++ tools directory
tools_builddir = evaldir + "/build-tools"        # Build dir for C++ tools

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
  target0  = evaldir + "/build-tools/task-trace-analyze"
  target1  = evaldir + "/build-tools/task-trace-annotate"
  file_dep = get_files_in_dir( cpptoolsdir )

  action = ' '.join( [
    'cd {};'.format(tools_builddir),
    'g++ -O3 -o task-trace-analyze ',
    '-I ../tools/cpptools {}/task-trace-analyze.cc -lpthread;'.format(cpptoolsdir),
    'g++ -O3 -o task-trace-annotate ',
    '-I ../tools/cpptools {}/task-trace-annotate.cc -lpthread;'.format(cpptoolsdir),
  ] )

  taskdict = {
    'basename' : 'build-tools',
    'actions'  : [ (create_folder, [tools_builddir]), action ],
    'file_dep' : file_dep,
    'targets'  : [ target0, target1 ]
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
    'task_dep' : [ 'build-tools' ],
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
# get_base_evaldict()
#----------------------------------------------------------------------------

def get_base_evaldict():

  # Default task options
  doc         = 'Basic configuration'
  basename    = 'basname'
  resultsdir  = 'results'
  evaldict    = {}

  evaldict['app_group'] = []  # Which group of apps to sim (e.g., ['scalar'])
  evaldict['app_list']  = []  # List of apps to sim
  evaldict['app_dict']  = {}  # Dict with app groups/opts to run

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
  doc        = evaldict['doc']

  # Yield a docstring subtask
  docstring_taskdict = { \
      'basename' : basename,
      'name'     : None,
      'doc'      : doc,
    }

  yield docstring_taskdict

  pydgin_binary = "../../scripts/builds/pydgin-parc-jit"
  pydgin_opts   = " --ncores 1 --pkernel ${STOW_PKGS_ROOT}/maven/boot/pkernel "

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

  app_dict  = evaldict["app_dict"]
  app_list  = evaldict["app_list"]
  app_group = evaldict["app_group"]

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

        # Define targets
        targets = [ app_dumpfile, timestamp_file ]

        #........................
        # Assemble pydgin command
        #........................

        # additional pydgin specifc options for task tracing
        extra_pydgin_opts = ""
        if os.path.isfile("links/"+app+".nm"):
          extra_pydgin_opts = " --task-runtime-md %(runtime_md)s " % { 'runtime_md' : "links/"+app+".nm"}
          extra_pydgin_opts = extra_pydgin_opts + "--outdir %(outdir)s " % { 'outdir' : app_results_dir }

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

        #...................................
        # Assemble command for regs analysis
        #...................................

        regs_cmd = (
          get_regs,
          [
            "links/"+app,
            "%(app_results_dir)s/task-trace.csv" % {'app_results_dir' : app_results_dir},
            "%(outdir)s" % {'outdir' : app_results_dir},
          ]
        )

        #......................................
        # Assemble command for task annotations
        #......................................

        disassemble_cmd = (
          disassemble,
          [
            "links/"+app,
            "%(outdir)s" % {'outdir' : app_results_dir},
          ]
        )

        annotate_cmd = ' '.join([
          "{}/task-trace-annotate".format(tools_builddir),
          " --trace {}/task-trace.csv".format(app_results_dir),
          " --calls {}/jal.csv".format(app_results_dir),
          " --runtime {}".format("links/"+app+".nm"),
          " --outdir {}".format(app_results_dir),
        ])

        #......................................
        # Assemble graph commands
        #......................................

        graph_cmd = (
          draw_graph,
          [
            "%(app_results_dir)s/task-graph.csv" % {'app_results_dir' : app_results_dir},
            "%(app_results_dir)s/task-trace.csv" % {'app_results_dir' : app_results_dir},
            "%(outdir)s" % {'outdir' : app_results_dir},
          ]
        )

        #......................................
        # Assemble trace analysis commands
        #......................................

        analyze_cmd = ' '.join([
          "{}/task-trace-analyze".format(tools_builddir),
          " --trace {}/task-trace.csv".format(app_results_dir),
          " --graph {}/task-graph.csv".format(app_results_dir),
          " --outdir {}".format(app_results_dir),
        ])

        #.......................
        # Build Task Dictionary
        #.......................

        taskdict = { \
            'basename' : basename,
            'name'     : labeled_app,
            'actions'  : [ (create_folder, [app_results_dir]), pydgin_cmd, disassemble_cmd, annotate_cmd],
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
