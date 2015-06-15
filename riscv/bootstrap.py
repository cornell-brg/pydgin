#=======================================================================
# bootstrap.py
#=======================================================================

from machine import State

#-----------------------------------------------------------------------
# test_init
#-----------------------------------------------------------------------
# initialize simulator state for simple programs, no syscalls
def test_init( mem, debug ):

  # instantiate architectural state with memory and reset address

  state = State( mem, debug, reset_addr=0x2000 )

  return state

