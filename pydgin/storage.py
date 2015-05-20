#=======================================================================
# storage.py
#=======================================================================

from pydgin.jit               import elidable, unroll_safe, hint
from debug                    import Debug, pad, pad_hex
try:
  from rpython.rlib.rarithmetic import r_uint32, widen
except ImportError:
  # if rpython not in path, we can use normal ints to store data
  r_uint32 = int
  def widen( value ):
    return value

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
  # use sparse storage if not translated
  try:
    from rpython.rlib.objectmodel import we_are_translated
    sparse_storage = not we_are_translated()
  except ImportError:
    sparse_storage = True

  if sparse_storage:
    print "NOTE: Using sparse storage"
    if byte_storage:
      return _SparseMemory( _ByteMemory )
    else:
      return _SparseMemory( _WordMemory )
  else:
    if byte_storage:
      return _ByteMemory( data, size )
    else:
      return _WordMemory( data, size )

#-----------------------------------------------------------------------
# Page
#-----------------------------------------------------------------------
# Represent a page of memory for the purpose of tracking code that
# modifies the instruction segment. Does nothing interesting except
# includes the quasi-immutable version.
class Page( object ):
  _immutable_fields_ = [ 'version?' ]

  def __init__( self ):
    self.version = 0

  def increment_version( self ):
    self.version += 1

  def is_data( self ):
    return not (self.version & 1)

  def is_inst( self ):
    return self.version & 1


#-------------------------------------------------------------------------
# _WordMemory
#-------------------------------------------------------------------------
# Memory that uses ints instead of chars
class _WordMemory( object ):
  _immutable_fields_ = [ 'page_shamt', 'num_pages' ]
  def __init__( self, data=None, size=2**10 ):
    self.data  = data if data else [ r_uint32(0) ] * (size >> 2)
    self.size  = (len( self.data ) << 2)
    self.debug = Debug()

    # TODO: pass data_section to memory for bounds checking
    self.data_section = 0x00000000

    # XXX: no idea if this is a good value
    self.page_shamt = 8
    self.num_pages = ( 0xffffffff >> self.page_shamt ) + 1
    # Initializing all of the pages at initialization seems to be a big
    # bottleneck. Instead, initializing a none array, and constructing
    # Page objects as necessary
    self.pages = [ None for i in xrange( self.num_pages ) ]

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

  # returns the page for this address
  @elidable
  def get_page( self, addr ):
    page_idx = addr >> self.page_shamt
    page = self.pages[ page_idx ]
    # initialize page if not initialized
    if page is None:
      new_page = Page()
      self.pages[ page_idx ] = new_page
      return new_page
    return page

  # same as above, but not elidable to ensure it doesn't turn into a
  # function call in the jit header
  def get_page_noelide( self, addr ):
    page_idx = addr >> self.page_shamt
    page = self.pages[ page_idx ]
    # initialize page if not initialized
    if page is None:
      new_page = Page()
      self.pages[ page_idx ] = new_page
      return new_page
    return page

  # utility function to increment the version of the page corresponding to
  # this address
  def increment_page( self, addr ):
    self.get_page( addr ).increment_version()

  # this is instruction read, which is otherwise identical to read. The
  # only difference is the elidable annotation, which we assume the
  # instructions are not modified (no side effects, assumes the addresses
  # correspond to the same instructions)
  # note that modified iread a little, and this is not elidable anymore.
  # instead, it calls elidale _iread_impl
  def iread( self, start_addr, num_bytes ):
    return self._iread_impl( start_addr, num_bytes,
                             self.get_page( start_addr ).version )

  # this is the actual elidable implementation that also includes the
  # version. by marking the version quasi-immutable, we can invalidate the
  # compiled jit when the version changes
  @elidable
  def _iread_impl( self, start_addr, num_bytes, _version ):
    # the least significant bit of version indicates instruction page
    if _version & 1 == 0:
      self.increment_page( start_addr )
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

    # check if the page version is odd (indicates instruction page),
    # change version
    page = self.get_page_noelide( start_addr )
    if page.is_inst():
      print "marking inst page a data page"
      page.increment_version()
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

#-----------------------------------------------------------------------
# _SparseMemory
#-----------------------------------------------------------------------

class _SparseMemory( object ):
  _immutable_fields_ = [ "BlockMemory", "block_size", "addr_mask",
                         "block_mask" ]

  def __init__( self, BlockMemory, block_size=2**10 ):
    self.BlockMemory = BlockMemory
    self.block_size = block_size
    self.addr_mask  = block_size - 1
    self.block_mask = 0xffffffff ^ self.addr_mask
    print "sparse memory size %x addr mask %x block mask %x" \
          % ( self.block_size, self.addr_mask, self.block_mask )
    #blocks     = []
    self.block_dict = {}

  def add_block( self, block_addr ):
    #print "adding block: %x" % block_addr
    self.block_dict[ block_addr ] = self.BlockMemory( size=self.block_size )

  @elidable
  def get_block_mem( self, block_addr ):
    #block_idx  = block_dict[ 
    if block_addr not in self.block_dict:
      self.add_block( block_addr )
    block_mem = self.block_dict[ block_addr ]
    return block_mem

  @elidable
  def iread( self, start_addr, num_bytes ):
    start_addr = hint( start_addr, promote=True )
    num_bytes  = hint( num_bytes,  promote=True )

    block_addr = self.block_mask & start_addr
    block_mem = self.get_block_mem( block_addr )
    return block_mem.iread( start_addr & self.addr_mask, num_bytes )

  def read( self, start_addr, num_bytes ):
    block_addr = self.block_mask & start_addr
    block_addr = hint( block_addr, promote=True )
    block_mem = self.get_block_mem( block_addr )
    return block_mem.read( start_addr & self.addr_mask, num_bytes )

  def write( self, start_addr, num_bytes, value ):
    block_addr = self.block_mask & start_addr
    block_addr = hint( block_addr, promote=True )
    block_mem = self.get_block_mem( block_addr )
    block_mem.write( start_addr & self.addr_mask, num_bytes, value )




