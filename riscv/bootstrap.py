#=======================================================================
# bootstrap.py
#=======================================================================

from machine import State

#-----------------------------------------------------------------------
# test_init
#-----------------------------------------------------------------------
# initialize simulator state for simple programs, no syscalls
def test_init( mem, debug ):

  # inject bootstrap code into the memory

  for i, data in enumerate( bootstrap_code ):
    mem.write( bootstrap_addr + i, 1, data )
  for i, data in enumerate( rewrite_code ):
    mem.write( rewrite_addr + i, 1, data )

  # instantiate architectural state with memory and reset address

  state = State( mem, debug, reset_addr=0x2000 )

  return state

