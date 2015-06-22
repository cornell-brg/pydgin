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
# Hacky RPython Workaround
#-------------------------------------------------------------------------
from pydgin.utils import r_uint
from pydgin.debug import Debug, pad, pad_hex

class RiscVFPRegisterFile( object ):
  def __init__( self, constant_zero=False, num_regs=32, nbits=64 ):
    self.num_regs = num_regs
    self.regs     = [ r_uint(0) ] * self.num_regs
    self.debug    = Debug()
    self.nbits    = nbits
    self.debug_nchars = nbits / 4

    if constant_zero: self._setitemimpl = self._set_item_const_zero
    else:             self._setitemimpl = self._set_item
  def __getitem__( self, idx ):
    if self.debug.enabled( "rf" ):
      print ':: RD.RF[%s] = %s' % (
                          pad( "%d" % idx, 2 ),
                          pad_hex( self.regs[idx],
                                   len=self.debug_nchars ) ),
    return self.regs[idx]

  @specialize.argtype(2)
  def __setitem__( self, idx, value ):
    value = r_uint( value )
    self._setitemimpl( idx, value )

  def _set_item( self, idx, value ):
    self.regs[idx] = value
    if self.debug.enabled( "rf" ):
      print ':: WR.RF[%s] = %s' % (
                        pad( "%d" % idx, 2 ),
                        pad_hex( self.regs[idx],
                                 len=self.debug_nchars ) ),
  def _set_item_const_zero( self, idx, value ):
    if idx != 0:
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

