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

    # we check for the following sequence for trigger:
    # add r1, r1, #0 (e2811000)
    # add r2, r2, #0 (e2822000)
    if self.state.trig_state == 0 and bits == 0xe2811000:
      self.state.trig_state = 1
    elif self.state.trig_state == 1:
      if bits == 0xe2822000 or \
         bits == 0xe2833000 or \
         bits == 0xe2844000 or \
         bits == 0xe2855000 or \
         bits == 0xe2866000 or \
         bits == 0xe2877000 or \
         bits == 0xe2888000:
        # discount the hook instructions
        self.state.ncycles -= 2
        self.state.trig_state = 0
      elif bits == 0xe2899000:
        self.state.trig_state = 109
      else:
        self.state.trig_state = 0

    elif self.state.trig_state == 109:
      if   bits == 0xe2822000:
        print "blackhole start %s" % self.state.ncycles
      elif bits == 0xe2833000:
        print "blackhole stop leave %s" % self.state.ncycles
      elif bits == 0xe2844000:
        print "blackhole stop exc %s" % self.state.ncycles
      elif bits == 0xe2855000:
        print "gc major start %s" % self.state.ncycles
      elif bits == 0xe2866000:
        print "gc major stop %s" % self.state.ncycles
      elif bits == 0xe2877000:
        print "gc minor start %s" % self.state.ncycles
      elif bits == 0xe2888000:
        print "gc minor stop %s" % self.state.ncycles
      elif bits == 0xe2899000:
        print "tracing start %s" % self.state.ncycles
      elif bits == 0xe28aa000:
        print "tracing stop %s" % self.state.ncycles
      elif bits == 0xe28bb000:
        print "tracing start gf %s" % self.state.ncycles
      elif bits == 0xe28cc000:
        print "tracing stop gf %s" % self.state.ncycles

      self.state.ncycles -= 3
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

