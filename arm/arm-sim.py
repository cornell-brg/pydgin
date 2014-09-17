#=======================================================================
# arm-sim.py
#=======================================================================

import sys
import os

# TODO: figure out a better way to set PYTHONENV
sys.path.append('..')
sys.path.append('/work/bits0/dml257/hg-pypy/pypy')

from pydgin.misc import load_program
from bootstrap   import syscall_init, memory_size
from isa         import decode

from rpython.rlib.jit import JitDriver

#-----------------------------------------------------------------------
# jit
#-----------------------------------------------------------------------

jitdriver = JitDriver( greens =['pc'],
                       reds   =['state'],
                       virtualizables = ['state']
                     )

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run( state, debug ):
  s = state

  while s.status == 0:

    jitdriver.jit_merge_point(
      pc       = s.pc,
      state    = s,
    )

    old = s.pc

    #if debug: print'{:6x}'.format( s.pc ),
    # we use trace elidable iread instead of just read
    inst = s.mem.iread( s.pc, 4 )
    #if debug: print '{:08x} {:8s} {:8d}'.format(inst, decode(inst).func_name[8:], s.ncycles),
    decode( inst )( s, inst )
    s.rf[15] = s.pc+8 # TODO: should this be done inside instruction definition?
    s.ncycles += 1    # TODO: should this be done inside instruction definition?
    if debug: print

    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[ 0: 6] )
    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[ 6:12] )
    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[12:18] )
    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[18:24] )
    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[24:30] )
    #print '0x{:08x} 0x{:08x} '.format( *s.rf[30:32] )

    if s.pc < old:
      jitdriver.can_enter_jit(
        pc       = s.pc,
        state    = s,
      )

  print 'DONE! Status =', s.status
  print 'Instructions Executed =', s.ncycles

#-----------------------------------------------------------------------
# entry_point
#-----------------------------------------------------------------------
def entry_point( argv ):
  try:
    filename = argv[1]
  except IndexError:
    print "You must supply a filename"
    return 1

  # Load the program into a memory object

  mem = [chr(0x88)] * memory_size
  mem, entrypoint, breakpoint = load_program(
      open( filename, 'rb' ), mem,
      # TODO: GEM5 uses this alignment, remove?
      alignment = 1<<12
  )

  debug = False

  # Insert bootstrapping code into memory and initialize processor state

  state = syscall_init( mem, entrypoint, breakpoint, argv, debug )
  state.rf .debug = False
  state.mem.debug = debug

  # Execute the program

  run( state, debug )

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
