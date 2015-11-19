#=========================================================================
# parc-sim.py
#=========================================================================

import sys

# need to add parent directory to get access to pydgin package
# TODO: cleaner way to do this?
sys.path.append('..')

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory
from pydgin.misc    import load_program
from pydgin         import elf

from bootstrap      import syscall_init, test_init, memory_size, \
                           pkernel_init
from instruction    import Instruction
from isa            import decode, reg_map

#-------------------------------------------------------------------------
# ParcSim
#-------------------------------------------------------------------------
# PARC Simulator

class ParcSim( Sim ):

  def __init__( self ):
    Sim.__init__( self, "PARC", jit_enabled=True )

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
  # init_state
  #-----------------------------------------------------------------------
  # This method is called to load the program and initialize architectural
  # state

  def init_state( self, exe_file, exe_name, run_argv, run_envp, testbin ):

    # Load the program into a memory object

    mem = Memory( size=memory_size, byte_storage=False )
    entrypoint, breakpoint = load_program( exe_file, mem  )

    # if there is also a pkernel specified, load it as well

    pkernel_enabled = False
    reset_addr = 0x1000
    if self.pkernel_bin is not None:
      try:
        pkernel_bin = self.pkernel_bin
        assert pkernel_bin is not None
        pkernel = open( pkernel_bin, 'rb' )
        load_program( pkernel, mem )
        # we also pick the pkernel reset vector if specified
        # TODO: get this from the elf
        reset_addr = 0xc000000
        pkernel_enabled = True
      except IOError:
        print "Could not open pkernel %s\nFalling back to no-pkernel mode" \
              % self.pkernel_bin

    # Insert bootstrapping code into memory and initialize processor state

    # TODO: testbin is hardcoded false right now
    testbin = False

    #if testbin: self.state = test_init   ( mem, debug )
    if pkernel_enabled:
      # TODO: get args_start_addr from elf
      self.states = pkernel_init( mem, breakpoint, run_argv,
                                  run_envp, self.debug,
                                  args_start_addr=0xd000320,
                                  ncores=self.ncores,
                                  reset_addr=reset_addr )
    else:
      self.states = syscall_init( mem, breakpoint, run_argv,
                                  run_envp, self.debug,
                                  ncores=self.ncores,
                                  reset_addr=reset_addr )

    for state in self.states:
      state.testbin  = testbin
      state.exe_name = exe_name

  #---------------------------------------------------------------------
  # run
  #---------------------------------------------------------------------
  # Override sim's run to print stat_num_insts on exit

  def run( self ):
    Sim.run( self )
    for i, state in enumerate( self.states ):
      print "Core %d Instructions Executed in Stat Region = %d" % \
            ( i, state.stat_num_insts )
      # we also calculate the stat instructions
      for j in xrange( 16 ):
        # first check if the stat was enabled
        if state.stat_inst_en[ j ]:
          # calculate the final value
          state.stat_inst_num_insts[ j ] += state.num_insts - \
                                          state.stat_inst_begin[j]

        # print the stat if it's greater than 0
        if state.stat_inst_num_insts[ j ] > 0:
          print "  Stat %d = %d" % ( j, state.stat_inst_num_insts[ j ] )
      # print XPC stats
      print "  Number of pcalls =", state.num_pcalls

# this initializes similator and allows translation and python
# interpretation

init_sim( ParcSim() )

