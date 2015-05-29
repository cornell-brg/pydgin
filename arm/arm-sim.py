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

# TODO: we need this for pointer traps. can do this way better
from machine        import ArmMemory

#-------------------------------------------------------------------------
# ArmSim
#-------------------------------------------------------------------------
# ARM Simulator

class ArmSim( Sim ):

  def __init__( self ):
    Sim.__init__( self, "ARM", jit_enabled=True )

  #-----------------------------------------------------------------------
  # run
  #-----------------------------------------------------------------------
  # override run function so that we can print extra stats outputs

  def run( self ):
    Sim.run( self )
    self.state.print_stats()

  #-----------------------------------------------------------------------
  # decode
  #-----------------------------------------------------------------------
  # The simulator calls architecture-specific decode to decode the
  # instruction bits

  def decode( self, bits ):
    # TODO add decode inside instruction:
    #return decode( bits )

    # we check for the following sequence for trigger:
    # add r1, r1, #0 (e2811000)
    # add r2, r2, #0 (e2822000)
    if self.state.trig_state == 0 and bits == 0xe2811000:
      self.state.trig_state = 1
    elif self.state.trig_state == 1:
      no_hook = False
      # increment hit count hook
      if bits == 0xe2822000:
        #print "trigger! pc: %s" % hex( self.state.pc )
        self.state.jit_block_trigger()
      # guard failure hook -- no bridge
      elif bits == 0xe2833000:
        self.state.guard_fail_trigger( bridge_compiled=False )
      # guard failure hook -- w/ bridge
      elif bits == 0xe2844000:
        self.state.guard_fail_trigger( bridge_compiled=True )
      elif bits == 0xe2855000:
        self.state.load_trigger()
      elif bits == 0xe2866000:
        self.state.store_trigger()
      elif bits == 0xe2877000:
        self.state.finish_trigger()
      elif bits == 0xe2888000:
        self.state.fun_call_trigger()
      else:
        no_hook = True

      # discount the hook instructions
      if not no_hook:
        self.state.ncycles -= 2

      self.state.trig_state = 0

    inst_str, exec_fun = decode( bits )
    return Instruction( bits, inst_str ), exec_fun

  #-----------------------------------------------------------------------
  # init_state
  #-----------------------------------------------------------------------
  # This method is called to load the program and initialize architectural
  # state

  def init_state( self, exe_file, run_argv, run_envp ):

    # Load the program into a memory object

    # XXX: using arm memory so that we can have pointer traps
    #mem = Memory( size=memory_size, byte_storage=False )
    mem = ArmMemory( None, memory_size )

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

