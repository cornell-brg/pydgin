#=========================================================================
# pdf-merge-bars.py
#=========================================================================
# Quick and dirty script to merge PDF files

import os
import re
import sys
import subprocess

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

g_ncores = 4

#-------------------------------------------------------------------------
# merge_pdfs
#-------------------------------------------------------------------------

def merge_pdfs( outfile ):
  merge_files = []

  # 1. mimd-static
  for runtime in ['spmd','wsrt']:
    for group in ['custom','pbbs','cilk']:
      if runtime == 'spmd' and group == 'cilk':
        continue
      file_name = '%s-%s-CL-NI-%dF-%dL.pdf' % ( group, runtime, g_ncores, g_ncores )
      merge_files.append( file_name )

  # 2. simt-static
  for runtime in ['spmd','wsrt']:
    for group in ['custom','pbbs','cilk']:
      if runtime == 'spmd' and group == 'cilk':
        continue
      file_name = '%s-%s-CL-NI-NF-%dL.pdf' % ( group, runtime, g_ncores )
      merge_files.append( file_name )

  # 3. ccores
  for runtime in ['spmd','wsrt']:
    for group in ['custom','pbbs','cilk']:
      if runtime == 'spmd' and group == 'cilk':
        continue
      file_name = '%s-%s-CL-NI-%dF-NL.pdf' % ( group, runtime, g_ncores )
      merge_files.append( file_name )


  # 4. simt
  for runtime in ['spmd','wsrt']:
    for group in ['custom','pbbs','cilk']:
      if runtime == 'spmd' and group == 'cilk':
        continue
      file_name = '%s-%s-CL-NI-NF-NL.pdf' % ( group, runtime )
      merge_files.append( file_name )

  # 5. mt
  for runtime in ['spmd','wsrt']:
    for group in ['custom','pbbs','cilk']:
      if runtime == 'spmd' and group == 'cilk':
        continue
      file_name = '%s-%s-CL-1I-1F-1L.pdf' % ( group, runtime )
      merge_files.append( file_name )

  merge_files = ' '.join( merge_files )
  cmd = 'pdftk ' + merge_files + ' output ' + outfile
  execute( cmd )

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Enter the output file!"
    exit( 1 )
  merge_pdfs( sys.argv[1] )
