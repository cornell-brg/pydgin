#=========================================================================
# machine.py
#=========================================================================

from pydgin.storage import RegisterFile
from pydgin.utils import specialize
from utils import trim_64
from isa import ENABLE_FP

#-------------------------------------------------------------------------
# State
#-------------------------------------------------------------------------
class State( object ):
  # TODO: add virtualizables
  _virtualizable_ = ['pc', 'num_insts']

  def __init__( self, memory, debug, reset_addr=0x400 ):
    self.pc       = reset_addr

    self.xlen     = 64   # defines the bitwidth of int registers
    self.flen     = 64   # defines the bitwidth of fp  registers

    self.rf       = RiscVRegisterFile()
    # TODO: a bit hacky...
    if ENABLE_FP:
      self.fp       = RiscVFPRegisterFile()
      self.fp.debug = debug
      self.fcsr     = 0    # Bits( 32 )
    self.csr      = 0    # Bits( XLEN )
    self.mem      = memory

    # if ENABLE_A:
    self.load_reservation = 0 # Bits( 64 )

    self    .debug = debug
    self.rf .debug = debug
    self.mem.debug = debug

    # coprocessor registers
    self.status          = 0
    self.stats_en        = 0
    self.num_insts       = 0
    self.stat_num_insts  = 0

    # we need a dedicated running flag bacase status could be 0 on a
    # syscall_exit
    self.running       = True

    # indicate if this is running a self-checking test
    self.testbin  = False

    # executable name
    self.exe_name = ""

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

  def fetch_pc( self ):
    return self.pc

class RiscVRegisterFile( RegisterFile ):
  def __init__( self ):
    RegisterFile.__init__( self,
      constant_zero=True,
      num_regs=32,
      nbits=64
    )

  @specialize.argtype(2)
  def __setitem__( self, idx, value ):
    return RegisterFile.__setitem__( self, idx, trim_64( value ) )

class RiscVFPRegisterFile( RegisterFile ):
  def __init__( self ):
    RegisterFile.__init__( self,
      constant_zero=False,
      num_regs=32,
      nbits=64
    )

  @specialize.argtype(2)
  def __setitem__( self, idx, value ):
    return RegisterFile.__setitem__( self, idx, value )
