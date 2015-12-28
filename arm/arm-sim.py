#=========================================================================
# arm-sim.py
#=========================================================================

import sys

# need to add parent directory to get access to pydgin package
# TODO: cleaner way to do this?
sys.path.append('..')

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory
from pydgin.misc    import load_program, FatalError
from bootstrap      import syscall_init, memory_size
from instruction    import Instruction
from isa            import decode

#-------------------------------------------------------------------------
# ArmSim
#-------------------------------------------------------------------------
# ARM Simulator

class ArmSim( Sim ):

  def __init__( self ):
    Sim.__init__( self, "ARM", jit_enabled=True )

  #-----------------------------------------------------------------------
  # decode
  #-----------------------------------------------------------------------
  # The simulator calls architecture-specific decode to decode the
  # instruction bits

  def decode( self, bits ):
    # TODO add decode inside instruction:
    #return decode( bits )
    inst_str, exec_fun = decode( bits )
    return Instruction( bits, inst_str ), exec_fun

  #-----------------------------------------------------------------------
  # pre_execute
  #-----------------------------------------------------------------------
  # Override pre execute to print the CPSRs on debug

  def pre_execute( self ):
    if self.debug.enabled( "rf" ):
      print ':: RD.CPSR = %s%s%s%s' % (
        'N' if self.state.N else '-',
        'Z' if self.state.Z else '-',
        'C' if self.state.C else '-',
        'V' if self.state.V else '-'
      ),

  #-----------------------------------------------------------------------
  # init_state
  #-----------------------------------------------------------------------
  # This method is called to load the program and initialize architectural
  # state

  def init_state( self, exe_file, exe_name, run_argv, run_envp, testbin ):

    # Load the program into a memory object

    mem = Memory( size=memory_size, byte_storage=False )
    entrypoint, breakpoint = load_program(
        #open( filename, 'rb' ),
        exe_file,
        mem,
        # TODO: GEM5 uses this alignment, remove?
        alignment = 1<<12
    )

    self.state = syscall_init( mem, entrypoint, breakpoint,
                               run_argv, run_envp, self.debug )


# this initializes similator and allows translation and python
# interpretation

init_sim( ArmSim() )

