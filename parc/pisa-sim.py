#=======================================================================
# pisa_sim.py
#=======================================================================

import sys
sys.path.append('/Users/dmlockhart/vc/git-brg/parc/pymtl')
sys.path.append('/Users/dmlockhart/vc/hg-opensource/pypy')

import os
import elf

from   isa              import decode
from   utils            import State
from   rpython.rlib.jit import JitDriver

#-----------------------------------------------------------------------
# bootstrap code
#-----------------------------------------------------------------------

bootstrap_addr = 0x400
bootstrap_code = [
  0x3c, 0x1d, 0x00, 0x07,   # lui r29, 0x0007
  0x34, 0x1d, 0xff, 0xfc,   # ori r29, r0, 0xfff
  0x08, 0x00, 0x04, 0x00,   # j   0x1000
]

#-----------------------------------------------------------------------
# execute
#-----------------------------------------------------------------------
def execute( mem ):
  s  = State( mem, None, reset_addr=0x400 )

  import struct
  for i in range( 10 ):
    string = ''.join(mem[s.pc:s.pc+4])
    bin_   = struct.unpack('>I', string)
    print s.pc, '{:08x}'.format((bin_[0]))
    print decode( bin_[0] )

#-----------------------------------------------------------------------
# load_program
#-----------------------------------------------------------------------
def load_program( fp ):
  mem_image = elf.elf_reader( fp )

  sections = mem_image.get_sections()
  mem      = [' ']*(2**20)

  for section in sections:
    start_addr = section.addr
    print section.name, start_addr
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
  for i, data in enumerate( bootstrap_code ):
    mem[ bootstrap_addr + i ] = chr( data )
  execute( mem )

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
