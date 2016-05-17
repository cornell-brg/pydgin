#=========================================================================
# arm-sim.py
#=========================================================================

import sys

# need to add parent directory to get access to pydgin package
# TODO: cleaner way to do this?
sys.path.append('..')

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory, MMUMemory
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

    # MMU project: use MMUMemory
    # HACKY: we don't have the state yet... pass a null pointer

    mem = MMUMemory( None, mem )

    entrypoint, breakpoint = load_program(
        #open( filename, 'rb' ),
        exe_file,
        mem,
        # TODO: GEM5 uses this alignment, remove?
        alignment = 1<<12
    )

    self.state = syscall_init( mem, entrypoint, breakpoint,
                               run_argv, run_envp, self.debug )

    # MMU project: actually pass the state to the mmu memory
    mem.state = self.state

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

init_sim( ArmSim() )

