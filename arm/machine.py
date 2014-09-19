#=======================================================================
# machine.py
#=======================================================================

# trace elidable for instruction reads
from rpython.rlib.jit         import elidable, unroll_safe
from rpython.rlib.rstruct     import ieee
from rpython.rlib.rarithmetic import intmask
from pydgin.debug             import Debug, pad, pad_hex

#-----------------------------------------------------------------------
# RegisterFile
#-----------------------------------------------------------------------
class RegisterFile( object ):
  def __init__( self, constant_zero=True ):
    self.regs  = [0] * 32
    self.debug = Debug()

    if constant_zero: self._setitemimpl = self._set_item_const_zero
    else:             self._setitemimpl = self._set_item
  def __getitem__( self, idx ):
    if self.debug.enabled( "rf" ):
      print ':: RD.RF[%s] = %s' % (
                          pad( "%d" % idx, 2 ),
                          pad_hex( self.regs[idx]) ),
    return self.regs[idx]
  def __setitem__( self, idx, value ):
    self._setitemimpl( idx, value )

  def _set_item( self, idx, value ):
    self.regs[idx] = value
    if self.debug.enabled( "rf" ):
      print ':: WR.RF[%s] = %s' % (
                        pad( "%d" % idx, 2 ),
                        pad_hex( self.regs[idx] ) ),
  def _set_item_const_zero( self, idx, value ):
    if idx != 0:
      self.regs[idx] = value
      if self.debug.enabled( "rf" ):
        print ':: WR.RF[%s] = %s' % (
                          pad( "%d" % idx, 2 ),
                          pad_hex( self.regs[idx] ) ),

  #-----------------------------------------------------------------------
  # print_regs
  #-----------------------------------------------------------------------
  # prints all registers (register dump)
  def print_regs( self ):
    num_regs = 16
    per_row  = 4
    for c in xrange( 0, num_regs, per_row ):
      str = ""
      for r in xrange( c, min( num_regs, c+per_row ) ):
        str += "%s:%s " % ( pad( "%d" % r, 2 ),
                            pad_hex( self.regs[r] ) )
      print str

#-----------------------------------------------------------------------
# Memory
#-----------------------------------------------------------------------
class Memory( object ):
  def __init__( self, data=None, debug=False ):
    if not data:
      self.data = [' ']*2**10
    else:
      self.data = data
    self.debug = Debug()

  @unroll_safe
  def read( self, start_addr, num_bytes ):
    value = 0
    if self.debug.enabled( "mem" ):
      print ':: RD.MEM[%s] = ' % pad_hex( start_addr ),
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.data[ start_addr + i ] )
    if self.debug.enabled( "mem" ):
      print '%s' % pad_hex( value ),
    return value

  # this is instruction read, which is otherwise identical to read. The
  # only difference is the elidable annotation, which we assume the
  # instructions are not modified (no side effects, assumes the addresses
  # correspond to the same instructions)
  @elidable
  @unroll_safe
  def iread( self, start_addr, num_bytes ):
    value = 0
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.data[ start_addr + i ] )
    return value

  @unroll_safe
  def write( self, start_addr, num_bytes, value ):
    if self.debug.enabled( "mem" ):
      print ':: WR.MEM[%s] = %s' % ( pad_hex( start_addr ),
                                     pad_hex( value ) ),
    for i in range( num_bytes ):
      self.data[ start_addr + i ] = chr(value & 0xFF)
      value = value >> 8

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  def __init__( self, memory, debug, reset_addr=0x400 ):
    self.pc       = reset_addr
    self.rf       = RegisterFile(constant_zero=False)
    self.mem      = memory

    self    .debug = debug
    self.rf .debug = debug
    self.mem.debug = debug

    # current program status register (CPSR)
    self.N    = 0b0      # Negative condition
    self.Z    = 0b0      # Zero condition
    self.C    = 0b0      # Carry condition
    self.V    = 0b0      # Overflow condition
    #self.J    = 0b0      # Jazelle state flag
    #self.I    = 0b0      # IRQ Interrupt Mask
    #self.F    = 0b0      # FIQ Interrupt Mask
    #self.T    = 0b0      # Thumb state flag
    #self.M    = 0b00000  # Processor Mode

    # other registers
    self.status        = 0
    self.ncycles       = 0
    # unused
    self.stats_en      = 0
    self.stat_ncycles  = 0

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

