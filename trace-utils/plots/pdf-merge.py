#=========================================================================
# pdf-merge.py
#=========================================================================
# Quick and dirty script to merge PDF files

import os
import re
import sys
import subprocess

from common import *

#-------------------------------------------------------------------------
# Utility Function
#-------------------------------------------------------------------------

def execute(cmd):
  try:
    print cmd
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    return err

#-------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------

g_path = './'

#-------------------------------------------------------------------------
# merge_pdfs
#-------------------------------------------------------------------------

def merge_pdfs( config, outfile ):
  merge_files = []
  for app in app_list:
    if not os.path.isfile( g_path + app + '-%.pdf' % config ):
      continue
    merge_files.append( g_path + app + '-%.pdf' % config )
  merge_files = ' '.join( merge_files )
  cmd = 'pdftk ' + merge_files + ' output ' + outfile
  execute( cmd )

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print "Enter the configuration and the output file!"
    exit( 1 )
  merge_pdfs( sys.argv[1], sys.argv[2] )
