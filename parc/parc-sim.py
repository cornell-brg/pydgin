#=========================================================================
# parc-sim.py
#=========================================================================

import sys
# TODO: figure out a better way to set PYTHONENV
sys.path.append('..')
#sys.path.append('/work/bits0/dml257/hg-pypy/pypy')

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory
# TODO: use load_program of pydgin.misc
#from pydgin.misc    import load_program
import elf

from bootstrap      import syscall_init, test_init, memory_size
from instruction    import Instruction
from isa            import decode, reg_map
from pipe_model     import StallingProcPipelineModel

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
  # post_exec
  #-----------------------------------------------------------------------

  def post_exec( self, inst ):
    # TODO: add a cmdline flag for this
    #pipe_model = None

    if self.pipe_model is not None:
      self.pipe_model.next_inst( inst )

  #-----------------------------------------------------------------------
  # sim_done
  #-----------------------------------------------------------------------

  def sim_done( self ):
    if self.pipe_model is not None:
      print "num_cycles = %d" % self.pipe_model.num_cycles
      print "num_squashes = %d" % self.pipe_model.num_squashes
      print "num_llfu_stalls = %d" % self.pipe_model.num_llfu_stalls
      print "num_raw_stalls = %d" % self.pipe_model.num_raw_stalls

  #-----------------------------------------------------------------------
  # init_state
  #-----------------------------------------------------------------------
  # This method is called to load the program and initialize architectural
  # state

  def init_state( self, exe_file, run_argv, run_envp ):

    # Load the program into a memory object

    mem, breakpoint = load_program( exe_file )

    # Insert bootstrapping code into memory and initialize processor state

    # TODO: testbin is hardcoded false right now
    testbin = False

    if testbin: self.state = test_init   ( mem, debug )
    else:       self.state = syscall_init( mem, breakpoint, run_argv,
                                           run_envp, self.debug )

    # initialize pipe model
    self.pipe_model = StallingProcPipelineModel( self.state )


#-----------------------------------------------------------------------
# load_program
#-----------------------------------------------------------------------
# TODO: refactor this as well

def load_program( fp ):
  mem_image = elf.elf_reader( fp )

  sections = mem_image.get_sections()
  mem      = Memory( size=memory_size, byte_storage=False )

  for section in sections:
    start_addr = section.addr
    for i, data in enumerate( section.data ):
      mem.write( start_addr+i, 1, ord( data ) )

  bss        = sections[-1]
  breakpoint = bss.addr + len( bss.data )
  return mem, breakpoint

# this initializes similator and allows translation and python
# interpretation

init_sim( ParcSim() )

