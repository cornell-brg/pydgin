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
from   rpython.rlib.jit import JitDriver, hint

#-----------------------------------------------------------------------
# jit
#-----------------------------------------------------------------------

# for debug printing in PYPYLOG
def get_location( pc ):
  # TODO: add the disassembly of the instruction here as well
  return "pc: %x" % pc

jitdriver = JitDriver( greens =['pc'],
                       reds   =['num_inst','state'],
                       virtualizables = ['state'],
                       get_printable_location=get_location,
                     )

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-----------------------------------------------------------------------
# bootstrap code
#-----------------------------------------------------------------------
# TODO: HACKY! We are rewriting the binary here, should really fix the
#       compiler instead!

bootstrap_addr = 0x400
bootstrap_code = [
  #0x07, 0x00, 0x1d, 0x3c,   # lui r29, 0x0007
  #0xfc, 0xff, 0x1d, 0x34,   # ori r29, r0, 0xfffc
  #0x00, 0x04, 0x00, 0x08,   # j   0x1000
  0x3c1d0007,
  0x341dfffc,
  0x08000400,
]

rewrite_addr      = 0x1008
rewrite_code      = [
  #0x08, 0x04, 0x00, 0x08,   # j   0x1020
  0x08000408,
]

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run( mem ):
  s  = State( Memory(mem), None, reset_addr=0x400 )
  num_inst = 0

  while s.status == 0:

    jitdriver.jit_merge_point(
      pc       = s.pc,
      num_inst = num_inst,
      state    = s,
    )

    # constant fold the pc
    pc = hint( s.pc, promote=True )
    old = pc

    #print'{:06x}'.format( s.pc ),
    # we use trace elidable iread instead of just read
    inst = s.mem.iread( pc, 4 )
    #print '{:08x}'.format( inst ), decode(inst), num_inst
    decode( inst )( s, inst )
    num_inst += 1

    if s.pc < old:
      jitdriver.can_enter_jit(
        pc       = s.pc,
        num_inst = num_inst,
        state    = s,
      )

  print 'DONE! Status =', s.status
  print 'Instructions Executed =', num_inst

#-----------------------------------------------------------------------
# load_program
#-----------------------------------------------------------------------
def load_program( fp ):
  mem_image = elf.elf_reader( fp )

  sections = mem_image.get_sections()
  mem      = [0]*(2**20)

  for section in sections:
    start_addr = section.addr >> 2
    #for i, data in enumerate( section.data ):
    #  mem[start_addr+i] = data
    data       = section.data
    for idx in range( len(section.data) >> 2 ):
      i = idx << 2
      value = (( ord(data[i]  )
            |  ( ord(data[i+1]) <<  8)
            |  ( ord(data[i+2]) << 16)
            |  ( ord(data[i+3]) << 24)))
      mem[start_addr+idx] = value

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
    mem[ (bootstrap_addr >> 2) + i ] = data

  # Rewrite jump address
  for i, data in enumerate( rewrite_code ):
    mem[ (rewrite_addr >> 2) + i ] = data

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
