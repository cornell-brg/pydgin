#=========================================================================
# riscv-sim.py
#=========================================================================

import sys

# need to add parent directory to get access to pydgin package
# TODO: cleaner way to do this?
sys.path.append('..')

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory
from pydgin.misc    import load_program
from bootstrap      import test_init, syscall_init
from instruction    import Instruction
from isa            import decode

#-------------------------------------------------------------------------
# RiscVSim
#-------------------------------------------------------------------------
class RiscVSim( Sim ):

  def __init__( self ):
    Sim.__init__( self, 'RiscV', jit_enabled=True )

  #-----------------------------------------------------------------------
  # decode
  #-----------------------------------------------------------------------
  # The simulator calls architecture-specific decode to decode the
  # instruction bits

  def decode( self, bits ):
    inst_str, exec_fun = decode( bits )
    return Instruction( bits, inst_str ), exec_fun

  #-----------------------------------------------------------------------
  # init_state
  #-----------------------------------------------------------------------
  # This method is called to load the program and initialize architectural
  # state

  def init_state( self, exe_file, exe_name, run_argv, run_envp, testbin ):

    # TODO: setting mem size here
    memory_size = 2**29

    # Load the program into a memory object

    mem = Memory( size=memory_size, byte_storage=False )
    entrypoint, breakpoint = load_program( exe_file, mem  )

    # Insert bootstrapping code into memory and initialize processor state

    #if testbin: self.state = test_init   ( mem, self.debug )
    #else:       self.state = syscall_init( mem, breakpoint, run_argv,
    #                                       run_envp, self.debug )
    if testbin:
      self.state = test_init( mem, self.debug )
    else:
      self.state = syscall_init( mem, self.debug )

    self.state.testbin  = testbin
    self.state.exe_name = exe_name

  #---------------------------------------------------------------------
  # run
  #---------------------------------------------------------------------
  # Override sim's run to print stat_num_insts on exit

  def run( self ):
    Sim.run( self )

# this initializes similator and allows translation and python
# interpretation

init_sim( RiscVSim() )

