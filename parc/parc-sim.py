#=========================================================================
# parc-sim.py
#=========================================================================

import sys

# need to add parent directory to get access to pydgin package
# TODO: cleaner way to do this?
sys.path.append('..')

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory, MMUMemory
from pydgin.misc    import load_program
from bootstrap      import syscall_init, test_init, memory_size
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

    # MMU project: use MMUMemory
    # HACKY: we don't have the state yet... pass a null pointer

    mem = MMUMemory( None, mem )

    entrypoint, breakpoint = load_program( exe_file, mem  )

    # Insert bootstrapping code into memory and initialize processor state

    if testbin: self.state = test_init   ( mem, self.debug )
    else:       self.state = syscall_init( mem, breakpoint, run_argv,
                                           run_envp, self.debug )

    # MMU project: actually pass the state to the mmu memory
    mem.state = self.state

    self.state.testbin  = testbin
    self.state.exe_name = exe_name

  #---------------------------------------------------------------------
  # run
  #---------------------------------------------------------------------
  # Override sim's run to print stat_num_insts on exit

  def run( self ):
    Sim.run( self )
    print "Instructions Executed in Stat Region =", self.state.stat_num_insts

    # MMU project: print load/store counters
    print "Num mem reads =",  self.state.num_reads
    print "Num mem ireads =", self.state.num_ireads
    print "Num mem writes =", self.state.num_writes

    # MMU project: if page table enabled, print the stats
    if self.state.enable_page_table:
      print "Page table hits (data)=",   self.state.dpage_table.hits
      print "Page table misses (data) =", self.state.dpage_table.misses
      print "Page table hits (Inst)=",   self.state.ipage_table.hits
      print "Page table misses (Inst) =", self.state.ipage_table.misses

# this initializes similator and allows translation and python
# interpretation

init_sim( ParcSim() )

