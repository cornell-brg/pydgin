#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile
from pydgin.utils   import r_uint

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  _virtualizable_ = ['pc', 'num_insts']
  def __init__( self, memory, debug, reset_addr=0x400 ):
    self.pc       = reset_addr

    # TODO: to allow the register file to be virtualizable (to avoid array
    # lookups in the JIT), it needs to be an array as a member of the
    # State class. Couldn't figure out how to have rf a RegisterFile
    # object and still be virtualizable.
    self.rf       = RegisterFile()
    self.mem      = memory

    self    .debug = debug
    self.rf .debug = debug
    self.mem.debug = debug

    # coprocessor registers
    self.status        = 0
    self.stats_en      = 0
    self.num_insts       = 0
    self.stat_num_insts  = 0
    self.gcd_ncycles     = 0

    # we need a dedicated running flag bacase status could be 0 on a
    # syscall_exit
    self.running       = True

    # parc special
    self.src_ptr  = 0
    self.sink_ptr = 0

    # indicate if this is running a self-checking test
    self.testbin  = False

    # executable name
    self.exe_name = ""

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

  def fetch_pc( self ):
    return self.pc
