#=======================================================================
# bootstrap.py
#=======================================================================

from machine import State

#-----------------------------------------------------------------------
# syscall_init
#-----------------------------------------------------------------------
# initialize simulator state for syscall emulation
def syscall_init( mem, debug ):

  # instantiate architectural state with memory and reset address

  state = State( mem, debug, reset_addr=0x2000 )

  return state

#-----------------------------------------------------------------------
# test_init
#-----------------------------------------------------------------------
# initialize simulator state for simple programs, no syscalls
def test_init( mem, debug ):

  # instantiate architectural state with memory and reset address

  state = State( mem, debug, reset_addr=0x200 )

  return state

