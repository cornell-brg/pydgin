#=======================================================================
# pisa_sim.py
#=======================================================================

import sys
sys.path.append('/Users/dmlockhart/vc/git-brg/parc/pymtl')
sys.path.append('/Users/dmlockhart/vc/hg-opensource/pypy')

import os
import elf

from   isa              import decode
from   utils            import State, Memory
from   rpython.rlib.jit import JitDriver

#-----------------------------------------------------------------------
# bootstrap code
#-----------------------------------------------------------------------
# TODO: HACKY! We are rewriting the binary here, should really fix the
#       compiler instead!

bootstrap_addr = 0x400
bootstrap_code = [
  0x07, 0x00, 0x1d, 0x3c,   # lui r29, 0x0007
  0xfc, 0xff, 0x1d, 0x34,   # ori r29, r0, 0xfff
  0x00, 0x04, 0x00, 0x08,   # j   0x1000
]

rewrite_addr      = 0x1008
rewrite_code      = [
  0x08, 0x04, 0x00, 0x08,   # j   0x1020
]

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run( mem ):
  s  = State( Memory(mem), None, reset_addr=0x400 )
  num_inst = 0

  while s.status == 0:

    print'{:06x}'.format( s.pc ),
    inst = s.mem.read( s.pc, 4 )
    print '{:08x}'.format( inst ), decode(inst), num_inst
    decode( inst )( s, inst )
    num_inst += 1

  print 'DONE! Status =', s.status
  print 'Instructions Executed =', num_inst

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

  # Load the program
  mem = load_program( open( filename, 'rb' ) )

  # Inject bootstrap code
  for i, data in enumerate( bootstrap_code ):
    mem[ bootstrap_addr + i ] = chr( data )

  # Rewrite jump address
  for i, data in enumerate( rewrite_code ):
    mem[ rewrite_addr + i ] = chr( data )

  # Execute program
  run( mem )

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
