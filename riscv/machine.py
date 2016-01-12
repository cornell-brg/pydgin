#=========================================================================
# machine.py
#=========================================================================

from pydgin.storage import RegisterFile
from pydgin.utils import specialize, r_ulonglong
from utils import trim_64
from isa import ENABLE_FP
from csr import Csr, PRV_M, PRV_H, PRV_S, PRV_U

#-------------------------------------------------------------------------
# State
#-------------------------------------------------------------------------
class State( object ):
  _virtualizable_ = ['pc', 'num_insts']
  # defines immutable fields that can't change during execution
  _immutable_fields_ = ['xlen', 'flen', 'extensions']

  def __init__( self, memory, debug, reset_addr=0x400,
                xlen=64,
                flen=64,
                extensions="imafd" ):
    self.pc         = reset_addr

    self.xlen       = xlen   # defines the bitwidth of int registers
    self.flen       = flen   # defines the bitwidth of fp  registers
    # TODO: convert to lower
    self.extensions = extensions

    self.rf       = RiscVRegisterFile( nbits=self.xlen )
    self.csr      = Csr( self )
    # TODO: a bit hacky...
    if self.extension_enabled( "f" ):
      self.fp       = RiscVFPRegisterFile()
      self.fp.debug = debug
      self.fcsr     = r_ulonglong( 0 )    # Bits( 32 )
    self.mem      = memory

    if self.extension_enabled( "a" ):
      self.load_reservation = 0 # Bits( 64 )

    self    .debug = debug
    self.rf .debug = debug
    self.mem.debug = debug

    # other state
    self.prv      = PRV_M
    self.mepc     = 0
    self.mbadaddr = 0
    self.mtimecmp = 0
    self.mscratch = 0
    self.mcause   = 0
    self.minstret = 0
    self.mie      = 0
    self.mip      = 0
    self.sepc     = 0
    self.sbadaddr = 0
    self.sscratch = 0
    self.stvec    = 0
    self.sptbr    = 0
    self.scause   = 0
    self.sutime_delta    = 0
    self.suinstret_delta = 0
    self.tohost   = 0
    self.fromhost = 0

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

  def extension_enabled( self, ext ):
    return ext in self.extensions


#-----------------------------------------------------------------------
# RiscVRegisterFile
#-----------------------------------------------------------------------
# TODO: we should use generic register file if possible

class RiscVRegisterFile( RegisterFile ):
  def __init__( self, nbits ):
    RegisterFile.__init__( self,
      constant_zero=True,
      num_regs=32,
      nbits=nbits
    )

  @specialize.argtype(2)
  def __setitem__( self, idx, value ):
    return RegisterFile.__setitem__( self, idx, trim_64( value ) )

#class RiscVFPRegisterFile( RegisterFile ):
#  def __init__( self ):
#    RegisterFile.__init__( self,
#      constant_zero=False,
#      num_regs=32,
#      nbits=64
#    )
#
#  @specialize.argtype(2)
#  def __setitem__( self, idx, value ):
#    return RegisterFile.__setitem__( self, idx, value )

#-------------------------------------------------------------------------
# RiscVFPRegisterFile
#-------------------------------------------------------------------------
# TODO: Hacky RPython Workaround

from pydgin.utils import r_uint
from pydgin.debug import Debug, pad, pad_hex

class RiscVFPRegisterFile( object ):
  def __init__( self, num_regs=32, nbits=64 ):
    self.num_regs = num_regs
    self.regs     = [ r_uint(0) ] * self.num_regs
    self.debug    = Debug()
    self.nbits    = nbits
    self.debug_nchars = nbits / 4

  def __getitem__( self, idx ):
    if self.debug.enabled( "rf" ):
      print ':: RD.RF[%s] = %s' % (
                          pad( "%d" % idx, 2 ),
                          pad_hex( self.regs[idx],
                                   len=self.debug_nchars ) ),
    return self.regs[idx]

  @specialize.argtype(2)
  def __setitem__( self, idx, value ):
    value = trim_64(value)
    self.regs[idx] = value
    if self.debug.enabled( "rf" ):
      print ':: WR.RF[%s] = %s' % (
                        pad( "%d" % idx, 2 ),
                        pad_hex( self.regs[idx],
                                 len=self.debug_nchars ) ),

  #-----------------------------------------------------------------------
  # print_regs
  #-----------------------------------------------------------------------
  # prints all registers (register dump)
  # per_row specifies the number of registers to display per row
  def print_regs( self, per_row=6 ):
    for c in xrange( 0, self.num_regs, per_row ):
      str = ""
      for r in xrange( c, min( self.num_regs, c+per_row ) ):
        str += "%s:%s " % ( pad( "%d" % r, 2 ),
                            pad_hex( self.regs[r] ) )
      print str

