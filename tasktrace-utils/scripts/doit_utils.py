#! /usr/bin/env python
#============================================================================
# doit_utils
#============================================================================
# Useful functions and constructs for all doit automation files.
#
# Date   : April 4, 2015
# Author : Christopher Torng
#

import os
from doit.tools import create_folder
from doit.reporter import ConsoleReporter

#----------------------------------------------------------------------------
# Set up reporter
#----------------------------------------------------------------------------

# Make reporter print task actions as they are executed / skipped

class MyReporter(ConsoleReporter):

    def execute_task(self, task):
        """called when excution starts"""
        # ignore tasks that do not define actions
        if task.actions:
            self.write('.  %s\n' % task.title())
            for action in task.actions:
              try: # CmdActions can be expanded
                self.write( '   .  %s\n' % action.expand_action() )
              except AttributeError: # PythonActions cannot
                self.write( '   .  %s\n' % str(action) )
            self.write('\n')

    def skip_uptodate(self, task):
        """skipped up-to-date task"""
        self.write("-- %s\n" % task.title())
        # ignore tasks that do not define actions
        if task.actions:
            for action in task.actions:
              try: # CmdActions can be expanded
                self.write( '   -- %s\n' % action.expand_action() )
              except AttributeError: # PythonActions cannot
                self.write( '   -- %s\n' % str(action) )
            self.write('\n')

    def skip_ignore(self, task):
        """skipped ignored task"""
        self.write("!! %s\n" % task.title())
        # ignore tasks that do not define actions
        if task.actions:
            for action in task.actions:
              try: # CmdActions can be expanded
                self.write( '   !! %s\n' % action.expand_action() )
              except AttributeError: # PythonActions cannot
                self.write( '   !! %s\n' % str(action) )
            self.write('\n')

    def add_failure(self, task, exception):
        """called when execution finishes with a failure"""
        self.failures.append({'task': task, 'exception':exception})
        msg = '\033[91m[Failed]\033[0m %s\n\n' % task.name
        self.write( msg )

    def add_success(self, task):
        """called when excution finishes successfuly"""
        msg = '\033[92m[Complete]\033[0m %s\n\n' % task.name
        self.write( msg )

    def complete_run(self):
        """called when finished running all tasks"""

        # if test fails print output from failed task
        if self.failures:
            self.write('{:~^40}\n\n'.format( ' Failures ' ))

        for result in self.failures:
            self.write("#"*40 + "\n")
            msg = '\033[91m[%s]\033[0m %s\n' % (result['exception'].get_name(),
                                                result['task'].name)
            self.write(msg)
            self.write(result['exception'].get_msg())
            self.write("\n")
            task = result['task']
            if self.show_out:
                out = "".join([a.out for a in task.actions if a.out])
                self.write("%s\n" % out)
            if self.show_err:
                err = "".join([a.err for a in task.actions if a.err])
                self.write("%s\n" % err)

        if self.runtime_errors:
            self.write('{:~^40}\n\n'.format( ' Runtime Errors ' ))
            self.write("#"*40 + "\n")
            self.write("Execution aborted.\n")
            self.write("\n".join(self.runtime_errors))
            self.write("\n")

#----------------------------------------------------------------------------
# Useful Functions
#----------------------------------------------------------------------------

def get_files_in_dir( path ):
  """Returns a list of all files in the given directory"""
  file_list = []
  for root, subfolders, files in os.walk( path ):
    for f in files:
      file_list.append( os.path.join( root, f ) )
  return file_list

def get_taskdict( task_func, basename='' ):
  """Returns the task dictionary with basename 'basename' from task"""

  task_data = task_func()

  # If task_data is a task generator, search for the basename.

  try:
    for taskdict in task_data:
      if taskdict['basename'] == basename:
        return taskdict
    assert False, \
        "Task {} does not have basename {}".format(str(task_func), basename)

  # Else, task_data is a task dictionary, so return it.

  except TypeError:
    return task_data

#----------------------------------------------------------------------------
# Useful Tasks
#----------------------------------------------------------------------------

def gen_mkdir_task( target, basename='' ):
  """Make the target dir"""

  if not basename:
    basename = 'mkdir-' + target

  taskdict = { \
    'basename' : basename,
    'actions'  : [ (create_folder, [target]) ],
    'targets'  : [ target ],
    'uptodate' : [ True ],
    'doc'      : 'Make {} directory'.format(target),
    'clean'    : [ 'rm -rf {}'.format(target) ],
    }

  yield taskdict

