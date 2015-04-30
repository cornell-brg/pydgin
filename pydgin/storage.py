#=======================================================================
# storage.py
#=======================================================================

from pydgin.jit               import elidable, unroll_safe
from debug                    import Debug, pad, pad_hex
from rpython.rlib.rarithmetic import r_uint32, widen

#-----------------------------------------------------------------------
# RegisterFile
#-----------------------------------------------------------------------
class RegisterFile( object ):
  def __init__( self, constant_zero=True, num_regs=32 ):
    self.num_regs = num_regs
    self.regs     = [0] * self.num_regs
    self.debug    = Debug()

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
  # per_row specifies the number of registers to display per row
  def print_regs( self, per_row=6 ):
    for c in xrange( 0, self.num_regs, per_row ):
      str = ""
      for r in xrange( c, min( self.num_regs, c+per_row ) ):
        str += "%s:%s " % ( pad( "%d" % r, 2 ),
                            pad_hex( self.regs[r] ) )
      print str

#-----------------------------------------------------------------------
# Memory
#-----------------------------------------------------------------------
def Memory( data=None, size=2**10, byte_storage=False ):
  if byte_storage:
    return _ByteMemory( data, size )
  else:
    return _WordMemory( data, size )

#-------------------------------------------------------------------------
# _WordMemory
#-------------------------------------------------------------------------
# Memory that uses ints instead of chars
class _WordMemory( object ):
  def __init__( self, data=None, size=2**10 ):
    self.data  = data if data else [ r_uint32(0) ] * (size >> 2)
    self.size  = (len( self.data ) << 2)
    self.debug = Debug()

    # TODO: pass data_section to memory for bounds checking
    self.data_section = 0x00000000

  def bounds_check( self, addr, x ):
    # check if the accessed data is larger than the memory size
    if addr > self.size:
      print ("WARNING: %s accessing larger address than memory size. "
             "addr=%s size=%s") % ( x, pad_hex( addr ), pad_hex( self.size ) )
      raise Exception()
    if addr == 0:
      print "WARNING: accessing null pointer!"
      raise Exception()

    # Special write checks
    if x == 'WR' and addr < self.data_section:
      print ("WARNING: %s writing address below .data section!!!. "
             "addr=%s size=%s") % ( x, pad_hex( addr ), pad_hex( self.data_section ) )
      raise Exception()


  @unroll_safe
  def read( self, start_addr, num_bytes ):
    assert 0 < num_bytes <= 4
    word = start_addr >> 2
    byte = start_addr &  0b11

    if self.debug.enabled( "mem" ):
      print ':: RD.MEM[%s] = ' % pad_hex( start_addr ),
    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr, 'RD' )

    value = 0
    if   num_bytes == 4:  # TODO: byte should only be 0 (only aligned)
      value = widen( self.data[ word ] )
    elif num_bytes == 2:  # TODO: byte should only be 0, 1, 2, not 3
      mask = 0xFFFF << (byte * 8)
      value = ( widen( self.data[ word ] ) & mask) >> (byte * 8)
    elif num_bytes == 1:
      mask = 0xFF   << (byte * 8)
      value = ( widen( self.data[ word ] ) & mask) >> (byte * 8)
    else:
      raise Exception('Invalid num_bytes: %d!' % num_bytes)

    if self.debug.enabled( "mem" ):
      print '%s' % pad_hex( value ),

    return value

  # this is instruction read, which is otherwise identical to read. The
  # only difference is the elidable annotation, which we assume the
  # instructions are not modified (no side effects, assumes the addresses
  # correspond to the same instructions)
  @elidable
  def iread( self, start_addr, num_bytes ):
    assert start_addr & 0b11 == 0  # only aligned accesses allowed
    return widen( self.data[ start_addr >> 2 ] )

  @unroll_safe
  def write( self, start_addr, num_bytes, value ):
    assert 0 < num_bytes <= 4
    word = start_addr >> 2
    byte = start_addr &  0b11

    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr, 'WR' )

    if   num_bytes == 4:  # TODO: byte should only be 0 (only aligned)
      pass # no masking needed
    elif num_bytes == 2:  # TODO: byte should only be 0, 1, 2, not 3
      mask  = ~(0xFFFF << (byte * 8)) & 0xFFFFFFFF
      value = ( widen( self.data[ word ] ) & mask ) \
              | ( (value & 0xFFFF) << (byte * 8) )
    elif num_bytes == 1:
      mask  = ~(0xFF   << (byte * 8)) & 0xFFFFFFFF
      value = ( widen( self.data[ word ] ) & mask ) \
              | ( (value & 0xFF  ) << (byte * 8) )
    else:
      raise Exception('Invalid num_bytes: %d!' % num_bytes)

    if self.debug.enabled( "mem" ):
      print ':: WR.MEM[%s] = %s' % ( pad_hex( start_addr ),
                                     pad_hex( value ) ),
    self.data[ word ] = r_uint32( value )

#-----------------------------------------------------------------------
# _ByteMemory
#-----------------------------------------------------------------------
class _ByteMemory( object ):
  def __init__( self, data=None, size=2**10 ):
    self.data  = data if data else [' '] * size
    self.size  = len( self.data )
    self.debug = Debug()

  def bounds_check( self, addr ):
    # check if the accessed data is larger than the memory size
    if addr > self.size:
      print "WARNING: accessing larger address than memory size. " + \
            "addr=%s size=%s" % ( pad_hex( addr ), pad_hex( self.size ) )
    if addr == 0:
      print "WARNING: writing null pointer!"
      raise Exception()

  @unroll_safe
  def read( self, start_addr, num_bytes ):
    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr )
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
  def iread( self, start_addr, num_bytes ):
    value = 0
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.data[ start_addr + i ] )
    return value

  @unroll_safe
  def write( self, start_addr, num_bytes, value ):
    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr )
    if self.debug.enabled( "mem" ):
      print ':: WR.MEM[%s] = %s' % ( pad_hex( start_addr ),
                                     pad_hex( value ) ),
    for i in range( num_bytes ):
      self.data[ start_addr + i ] = chr(value & 0xFF)
      value = value >> 8


