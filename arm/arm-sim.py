#=========================================================================
# arm-sim.py
#=========================================================================

import sys
# TODO: figure out a better way to set PYTHONENV
sys.path.append('..')
#sys.path.append('/work/bits0/dml257/hg-pypy/pypy')

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory
from pydgin.misc    import load_program
from bootstrap      import syscall_init, memory_size
from instruction    import Instruction
from isa            import decode

class ArmSim( Sim ):

  def __init__( self ):
    Sim.__init__( self, "ARM", jit_enabled=True )

  def decode( self, bits ):
    # TODO add decode inside instruction:
    #return decode( bits )
    inst_str, exec_fun = decode( bits )
    return Instruction( bits ), exec_fun

  def init_state( self, exe_file, run_argv ):

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
                               run_argv, self.debug )

init_sim( ArmSim() )

