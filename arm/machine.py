# trace elidable for instruction reads
from rpython.rlib.jit         import elidable, unroll_safe
from rpython.rlib.rstruct     import ieee
from rpython.rlib.rarithmetic import intmask

#-----------------------------------------------------------------------
# RegisterFile
#-----------------------------------------------------------------------
class RegisterFile( object ):
  def __init__( self, debug=False ):
    self.regs  = [0] * 32
    self.debug = debug
  def __getitem__( self, idx ):
    if self.debug: print ':: RD.RF[%2d] = %8x' % (idx, self.regs[idx]),
    return self.regs[idx]
  def __setitem__( self, idx, value ):
    if idx != 0:
      self.regs[idx] = value
      if self.debug: print ':: WR.RF[%2d] = %8x' % (idx, value),

#-----------------------------------------------------------------------
# Memory
#-----------------------------------------------------------------------
class Memory( object ):
  def __init__( self, data=None, debug=False ):
    if not data:
      self.data = [' ']*2**10
    else:
      self.data = data
    self.debug = debug

  @unroll_safe
  def read( self, start_addr, num_bytes ):
    value = 0
    if self.debug: print ':: RD.MEM[%x] = ' % (start_addr),
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.data[ start_addr + i ] )
    if self.debug: print '%x' % (value),
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
    if self.debug: print ':: WR.MEM[%x] = %x' % (start_addr, value),
    for i in range( num_bytes ):
      self.data[ start_addr + i ] = chr(value & 0xFF)
      value = value >> 8

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  _virtualizable_ = [ 'rf.regs[*]' ]
  def __init__( self, memory, symtable, reset_addr=0x400, debug=False ):
    self.pc       = reset_addr
    self.rf       = RegisterFile()
    self.mem      = memory

    self.rf .debug = debug
    self.mem.debug = debug

    # coprocessor registers
    self.N = 0
    self.Z = 0
    self.C = 0
    self.V = 0

    # other registers
    self.status        = 0
    self.ncycles       = 0

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

