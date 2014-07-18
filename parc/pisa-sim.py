#=======================================================================
# pisa_sim.py
#=======================================================================

import sys
sys.path.append('/Users/dmlockhart/vc/git-brg/parc/pymtl')
sys.path.append('/Users/dmlockhart/vc/hg-opensource/pypy')

import os
import elf

from   rpython.rlib.jit import JitDriver

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
#def run( fp ):
#  #program, memory, symtable, src, sink  = parse( fp )
#  #mainloop( program, memory, symtable, src, sink )
#
#  with open(source_elf,'rb') as file_obj:
#    mem_image = elf.elf_reader( file_obj )

#-----------------------------------------------------------------------
# load_program
#-----------------------------------------------------------------------
def load_program( fp ):
  mem_image = elf.elf_reader( fp )

  sections = mem_image.get_sections()
  mem      = [' ']*(2**20)

  for section in sections:
    start_addr = section.addr
    for i, data in enumerate( section.data ):
      mem[start_addr+i] = data

  return mem

#-----------------------------------------------------------------------
# entry_point
#-----------------------------------------------------------------------
def entry_point( argv ):
  try:
    filename = argv[1]
  except IndexError:
    print "You must supply a filename"
    return 1

  mem = load_program( open( filename, 'rb' ) )

  return 0

#-----------------------------------------------------------------------
# target
#-----------------------------------------------------------------------
# Enables RPython translation of our interpreter.
def target( *args ):
  return entry_point, None

#-----------------------------------------------------------------------
# main
#-----------------------------------------------------------------------
# Enables CPython simulation of our interpreter.
if __name__ == "__main__":
  entry_point( sys.argv )
