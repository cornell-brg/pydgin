#=======================================================================
# storage.py
#=======================================================================

from pydgin.jit               import elidable, unroll_safe, hint
from pydgin.cache             import AbstractCache, NullCache
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

#-------------------------------------------------------------------------
# _AbstractMemory
#-------------------------------------------------------------------------
class _AbstractMemory( object ):
  def __init__( self ):
    self.icache = NullCache()
    self.dcache = NullCache()

  def read( self, start_addr, num_bytes ):
    raise NotImplementedError()

  def iread( self, start_addr, num_bytes ):
    raise NotImplementedError()

  def write( self, start_addr, num_bytes, value ):
    raise NotImplementedError()

  # set caches
  def set_caches( self, icache, dcache ):
    self.icache = icache
    self.dcache = dcache

  # allocates pages for the address range if not already initialized
  def init_pages( self, vaddr_begin, vaddr_end ):
    pass

#-------------------------------------------------------------------------
# _WordMemory
#-------------------------------------------------------------------------
# Memory that uses ints instead of chars
class _WordMemory( _AbstractMemory ):
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
    return widen( self.data[ start_addr >> 2 ] ), start_addr

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
class _ByteMemory( _AbstractMemory ):
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
    return value, start_addr

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
# _PhysicalByteMemory
#-----------------------------------------------------------------------
# This is similar to normal byte memory, but the backing storage is passed
# as a raw C character array
class _PhysicalByteMemory( _AbstractMemory ):
  def __init__( self, pmem, size=2**10, page_table={}, page_shamt=12 ):
    self.pmem  = pmem
    self.size  = size
    self.debug = Debug()

    self.page_shamt = page_shamt
    self.set_page_table( page_table )

  def set_page_table( self, page_table ):
    self.page_table = page_table
    self.diff_page_table = {}
    self.page_size  = 1 << self.page_shamt
    self.page_mask  = self.page_size - 1
    self.next_paddr = len( self.page_table ) * self.page_size
    print "page shamt %d size %x mask %x next %x" % ( self.page_shamt,
                                              self.page_size,
                                              self.page_mask,
                                              self.next_paddr )

  def bounds_check( self, addr ):
    # check if the accessed data is larger than the memory size
    if addr > self.size:
      print "WARNING: accessing larger address than memory size. " + \
            "addr=%s size=%s" % ( pad_hex( addr ), pad_hex( self.size ) )
    if addr == 0:
      print "WARNING: writing null pointer!"
      raise Exception()

  # allocate a new page
  def allocate_page( self, vaddr_idx ):
    self.page_table[ vaddr_idx ] = self.next_paddr
    self.diff_page_table[ vaddr_idx ] = self.next_paddr
    self.next_paddr += self.page_size
    #print "allocate page vaddr_idx=%d paddr=%x" % (vaddr_idx,
    #                               self.page_table[ vaddr_idx ] )
    return self.page_table[ vaddr_idx ]

  # allocates pages for the address range if not already initialized
  def init_pages( self, vaddr_begin, vaddr_end ):
    vaddr_begin_idx = vaddr_begin >> self.page_shamt
    vaddr_end_idx   = vaddr_end   >> self.page_shamt

    for vaddr_idx in range( vaddr_begin_idx, vaddr_end_idx+1 ):
      if vaddr_idx not in self.page_table:
        self.allocate_page( vaddr_idx )

  # lookup in the page table and find the physical address
  @elidable
  def page_table_lookup( self, addr ):
    # first get the virtual address index
    vaddr_idx = addr >> self.page_shamt

    if vaddr_idx in self.page_table:
      paddr = ( addr & self.page_mask ) | self.page_table[ vaddr_idx ]

    else:
      paddr = ( addr & self.page_mask ) | self.allocate_page( vaddr_idx )

    #print "page_table_lookup %x paddr %x vaddr_idx %x base_paddr %x" \
    #      % (addr, paddr, vaddr_idx, self.page_table[ vaddr_idx ] )
    return paddr

  @unroll_safe
  def read( self, start_addr, num_bytes ):
    start_addr = self.page_table_lookup( start_addr )
    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr )
    value = 0
    if self.debug.enabled( "mem" ):
      print ':: RD.MEM[%s] = ' % pad_hex( start_addr ),
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.pmem[ start_addr + i ] )
    if self.debug.enabled( "mem" ):
      print '%s' % pad_hex( value ),
    return value

  # this is instruction read, which is otherwise identical to read. The
  # only difference is the elidable annotation, which we assume the
  # instructions are not modified (no side effects, assumes the addresses
  # correspond to the same instructions)
  @elidable
  def iread( self, start_addr, num_bytes ):
    start_addr = self.page_table_lookup( start_addr )
    value = 0
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.pmem[ start_addr + i ] )
    return value, start_addr

  @unroll_safe
  def write( self, start_addr, num_bytes, value ):
    start_addr = self.page_table_lookup( start_addr )
    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr )
    if self.debug.enabled( "mem" ):
      print ':: WR.MEM[%s] = %s' % ( pad_hex( start_addr ),
                                     pad_hex( value ) ),
    for i in range( num_bytes ):
      self.pmem[ start_addr + i ] = chr(value & 0xFF)
      value = value >> 8

#-----------------------------------------------------------------------
# _PhysicalWordMemory
#-----------------------------------------------------------------------
# This is similar to normal word memory, but the backing storage is passed
# as a raw C int array
class _PhysicalWordMemory( _AbstractMemory ):
  _immutable_fields_ = [ "page_table[*]" ]
  def __init__( self, pmem, size=2**10, page_table={}, page_shamt=12 ):
    _AbstractMemory.__init__( self )
    self.pmem  = pmem
    self.size  = size
    self.debug = Debug()

    self.page_shamt = page_shamt
    self.set_page_table( page_table )

  def set_page_table( self, page_table ):

    self.page_table_num_entries = 1
    # hacky way to get exponential (** is not rpython)
    for i in range(32 - self.page_shamt):
      self.page_table_num_entries *= 2

    print "page_table entries", self.page_table_num_entries
    self.page_table = [ -1 ] * self.page_table_num_entries

    #self.page_table = page_table
    self.diff_page_table = {}
    self.page_size  = 1 << self.page_shamt
    self.page_mask  = self.page_size - 1
    self.next_paddr = len( page_table ) * self.page_size
    print "page shamt %d size %x mask %x next %x" % ( self.page_shamt,
                                              self.page_size,
                                              self.page_mask,
                                              self.next_paddr )

  def bounds_check( self, addr ):
    # check if the accessed data is larger than the memory size
    if addr > self.size:
      print "WARNING: accessing larger address than memory size. " + \
            "addr=%s size=%s" % ( pad_hex( addr ), pad_hex( self.size ) )
    if addr == 0:
      print "WARNING: writing null pointer!"
      raise Exception()

  # allocate a new page
  def allocate_page( self, vaddr_idx ):
    self.page_table[ vaddr_idx ] = self.next_paddr
    self.diff_page_table[ vaddr_idx ] = self.next_paddr
    self.next_paddr += self.page_size
    #print "allocate page vaddr_idx=%d paddr=%x" % (vaddr_idx,
    #                               self.page_table[ vaddr_idx ] )
    return self.page_table[ vaddr_idx ]

  # allocates pages for the address range if not already initialized
  def init_pages( self, vaddr_begin, vaddr_end ):
    vaddr_begin_idx = vaddr_begin >> self.page_shamt
    vaddr_end_idx   = vaddr_end   >> self.page_shamt

    for vaddr_idx in range( vaddr_begin_idx, vaddr_end_idx+1 ):
      #if vaddr_idx not in self.page_table:
      #  self.allocate_page( vaddr_idx )
      if self.page_table[ vaddr_idx ] == -1:
        self.allocate_page( vaddr_idx )

  # lookup in the page table and find the physical address
  @elidable
  def page_table_lookup_elidable( self, addr ):
    return self.page_table_lookup( addr )
    # first get the virtual address index
    #vaddr_idx = addr >> self.page_shamt

    #if vaddr_idx in self.page_table:
    #  paddr = ( addr & self.page_mask ) | self.page_table[ vaddr_idx ]

    #else:
    #  paddr = ( addr & self.page_mask ) | self.allocate_page( vaddr_idx )

    ##print "page_table_lookup %x paddr %x vaddr_idx %x base_paddr %x" \
    ##      % (addr, paddr, vaddr_idx, self.page_table[ vaddr_idx ] )
    #return paddr

  # lookup in the page table and find the physical address
  @unroll_safe
  def page_table_lookup( self, addr ):
    # first get the virtual address index
    vaddr_idx = addr >> self.page_shamt

    base_addr = self.page_table[ vaddr_idx ]
    if base_addr != -1:
      paddr = ( addr & self.page_mask ) | base_addr
    else:
      paddr = ( addr & self.page_mask ) | self.allocate_page( vaddr_idx )

    #try:
    #  paddr = ( addr & self.page_mask ) | self.page_table[ vaddr_idx ]

    #except KeyError:
    #  paddr = ( addr & self.page_mask ) | self.allocate_page( vaddr_idx )

    #print "page_table_lookup %x paddr %x vaddr_idx %x base_paddr %x" \
    #      % (addr, paddr, vaddr_idx, self.page_table[ vaddr_idx ] )
    return paddr

  @unroll_safe
  def read( self, start_addr, num_bytes ):
    start_addr = self.page_table_lookup( start_addr )
    self.dcache.mark_transaction( AbstractCache.READ,
                                        start_addr, num_bytes )
    assert 0 < num_bytes <= 4
    word = start_addr >> 2
    byte = start_addr &  0b11

    if self.debug.enabled( "mem" ):
      print ':: RD.MEM[%s] = ' % pad_hex( start_addr ),
    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr, 'RD' )

    value = 0
    if   num_bytes == 4:  # TODO: byte should only be 0 (only aligned)
      value = widen( self.pmem[ word ] )
    elif num_bytes == 2:  # TODO: byte should only be 0, 1, 2, not 3
      mask = 0xFFFF << (byte * 8)
      value = ( widen( self.pmem[ word ] ) & mask) >> (byte * 8)
    elif num_bytes == 1:
      mask = 0xFF   << (byte * 8)
      value = ( widen( self.pmem[ word ] ) & mask) >> (byte * 8)
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
    start_addr = self.page_table_lookup_elidable( start_addr )
    assert start_addr & 0b11 == 0  # only aligned accesses allowed
    return widen( self.pmem[ start_addr >> 2 ] ), start_addr

  @unroll_safe
  def write( self, start_addr, num_bytes, value ):
    start_addr = self.page_table_lookup( start_addr )
    self.dcache.mark_transaction( AbstractCache.WRITE,
                                        start_addr, num_bytes )
    assert 0 < num_bytes <= 4
    word = start_addr >> 2
    byte = start_addr &  0b11

    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr, 'WR' )

    if   num_bytes == 4:  # TODO: byte should only be 0 (only aligned)
      pass # no masking needed
    elif num_bytes == 2:  # TODO: byte should only be 0, 1, 2, not 3
      mask  = ~(0xFFFF << (byte * 8)) & 0xFFFFFFFF
      value = ( widen( self.pmem[ word ] ) & mask ) \
              | ( (value & 0xFFFF) << (byte * 8) )
    elif num_bytes == 1:
      mask  = ~(0xFF   << (byte * 8)) & 0xFFFFFFFF
      value = ( widen( self.pmem[ word ] ) & mask ) \
              | ( (value & 0xFF  ) << (byte * 8) )
    else:
      raise Exception('Invalid num_bytes: %d!' % num_bytes)

    if self.debug.enabled( "mem" ):
      print ':: WR.MEM[%s] = %s' % ( pad_hex( start_addr ),
                                     pad_hex( value ) ),
    self.pmem[ word ] = r_uint32( value )

#-----------------------------------------------------------------------
# _SparseMemory
#-----------------------------------------------------------------------

class _SparseMemory( _AbstractMemory ):
  _immutable_fields_ = [ "BlockMemory", "block_size", "addr_mask",
                         "block_mask" ]

  def __init__( self, BlockMemory, block_size=2**10 ):
    _AbstractMemory.__init__( self )
    self.BlockMemory = BlockMemory
    self.block_size = block_size
    self.addr_mask  = block_size - 1
    self.block_mask = 0xffffffff ^ self.addr_mask
    self.debug = Debug()
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
    end_addr   = start_addr + num_bytes - 1

    block_addr = self.block_mask & start_addr
    block_mem = self.get_block_mem( block_addr )
    # For mixed-width ISAs, the start_addr is not necessarily
    # word-aligned, and can cross block memory boundaries. If there is
    # such a case, we have two instruction reads and then form the word
    # for it
    block_end_addr = self.block_mask & end_addr
    if block_addr == block_end_addr:
      return block_mem.iread( start_addr & self.addr_mask, num_bytes )[0], \
             start_addr
    else:
      num_bytes1 = min( self.block_size - (start_addr & self.addr_mask),
                        num_bytes )
      num_bytes2 = num_bytes - num_bytes1

      block_mem1 = block_mem
      block_mem2 = self.get_block_mem( block_end_addr )
      value1, _ = block_mem1.iread( start_addr & self.addr_mask, num_bytes1 )
      value2, _ = block_mem2.iread( 0, num_bytes2 )
      value = value1 | ( value2 << (num_bytes1*8) )
      #print "nb1", num_bytes1, "nb2", num_bytes2, \
      #      "ba1", hex(block_addr), "ba2", hex(block_end_addr), \
      #      "v1", hex(value1), "v2", hex(value2), "v", hex(value)
      return value, start_addr

  def read( self, start_addr, num_bytes ):
    self.dcache.mark_transaction( AbstractCache.READ,
                                        start_addr, num_bytes )
    if self.debug.enabled( "mem" ):
      print ':: RD.MEM[%s] = ' % pad_hex( start_addr ),
    block_addr = self.block_mask & start_addr
    block_addr = hint( block_addr, promote=True )
    block_mem = self.get_block_mem( block_addr )
    value = block_mem.read( start_addr & self.addr_mask, num_bytes )
    if self.debug.enabled( "mem" ):
      print '%s' % pad_hex( value ),
    return value

  def write( self, start_addr, num_bytes, value ):
    self.dcache.mark_transaction( AbstractCache.WRITE, start_addr, num_bytes )
    if self.debug.enabled( "mem" ):
      print ':: WR.MEM[%s] = %s' % ( pad_hex( start_addr ),
                                     pad_hex( value ) ),
    block_addr = self.block_mask & start_addr
    block_addr = hint( block_addr, promote=True )
    block_mem = self.get_block_mem( block_addr )
    block_mem.write( start_addr & self.addr_mask, num_bytes, value )




