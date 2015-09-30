#=========================================================================
# cache.py
#=========================================================================
# Cache models

from pydgin.jit import unroll_safe
from pydgin.debug import pad_hex
from rpython.rtyper.lltypesystem import rffi
try:
  from rpython.rlib.rarithmetic import r_uint32, widen
except ImportError:
  r_uint32 = int
  def widen( value ):
    return value

#-------------------------------------------------------------------------
# AbstractCache
#-------------------------------------------------------------------------
# The base class for cache models
class AbstractCache( object ):

  READ  = 0
  WRITE = 1

  # generic call to mark a read/write transaction
  def mark_transaction( self, type, address, size ):
    raise NotImplementedError()

  def dump( self ):
    pass

#-------------------------------------------------------------------------
# NullCache
#-------------------------------------------------------------------------
# Cache that does nothing
class NullCache( AbstractCache ):

  def mark_transaction( self, type, address, size ):
    pass

#-------------------------------------------------------------------------
# DirectMappedCache
#-------------------------------------------------------------------------
# Direct mapped cache implementation
class DirectMappedCache( AbstractCache ):
  _immutable_fields_ = [ "stats_en", "dirty_en", "line_size",
                         "line_shamt", "line_idx_mask"]

  # size is the total size of the cache in bytes,
  # line_size is the cache line size in bytes
  def __init__( self, size, line_size, name, debug, stats_en=False,
                dirty_en=False ):
    self.size = size
    self.line_size = line_size

    # naive implementation: use a simple tag array implemented as an array
    self.num_lines = self.size / self.line_size
    self.tag_array = [ -1 ] * self.num_lines

    # calculate line_shamt: the shift amount to find the line base address
    self.line_shamt = 0
    ls = self.line_size
    while ls & 1 == 0:
      ls = ls >> 1
      self.line_shamt += 1

    self.line_idx_mask = self.num_lines - 1

    self.debug = debug
    self.name  = name
    self.dirty_en = dirty_en
    self.stats_en = stats_en
    self.num_hits   = 0
    self.num_misses = 0
    self.num_evicts = 0
    self.num_reads  = 0
    self.num_writes = 0
    if self.debug.enabled( "cache" ):
      print ( "%s init\nnum_lines = %d\nline_size = %d\n"
              "line_shamt = %d\nline_idx_mask = %x" ) \
              % ( self.name,
                  self.num_lines,
                  self.line_size,
                  self.line_shamt,
                  self.line_idx_mask )

  def mark_transaction( self, type, address, size ):
    addr_sh = address >> self.line_shamt
    line_idx = addr_sh & self.line_idx_mask

    if self.debug.enabled( "cache" ):
      # also check if we had a hit or miss
      hit = ( self.tag_array[ line_idx ] == addr_sh )
      print "%s %s %s addr = %x, line_idx = %x" \
            % ( self.name,
                "read" if type == self.READ else "write",
                "hit" if hit else "miss",
                address, line_idx )

    # shifted address only to be used for checking a hit
    addr_sh_check = addr_sh
    # if we support dirty bit, we use the 31st bit of the tag. raw tag is
    # the value before we manipulate this
    if self.dirty_en:
      raw_tag = self.tag_array[ line_idx ]
      if type == self.WRITE:
        # mark dirty bit
        addr_sh = 0x80000000 | addr_sh

      clean_tag = raw_tag & 0x7fffffff
    else:
      clean_tag = self.tag_array[ line_idx ]
      raw_tag   = clean_tag

    if self.stats_en:
      #hit = ( self.tag_array[ line_idx ] == addr_sh )
      hit = ( clean_tag == addr_sh_check )

      if hit:
        self.num_hits += 1
      else:
        self.num_misses += 1
        # check if the old line was dirty, and if so this will cause an
        # eviction
        if self.dirty_en and (raw_tag & 0x80000000) != 0:
          self.num_evicts += 1

      if type == self.READ:
        self.num_reads += 1
      else:
        self.num_writes += 1

    self.tag_array[ line_idx ] = addr_sh

  def dump( self ):
    #for i in range( self.num_lines ):
    #  print "%d %x" % ( i, self.tag_array[ i ] )

    print "Stats for", self.name
    print     ( "num_hits   = %d\n"
                "num_misses = %d\n"
                "num_evicts = %d\n"
                "num_reads  = %d\n"
                "num_writes = %d\n" ) % \
              ( self.num_hits   ,
                self.num_misses ,
                self.num_evicts ,
                self.num_reads  ,
                self.num_writes , )

#-------------------------------------------------------------------------
# SetAssocCache
#-------------------------------------------------------------------------
# Set associative cache implementation
class SetAssocCache( AbstractCache ):
  _immutable_fields_ = [ "stats_en", "dirty_en", "line_size", "num_ways",
                         "line_shamt", "line_idx_mask"]

  # size is the total size of the cache in bytes,
  # line_size is the cache line size in bytes
  def __init__( self, size, line_size, name, debug, state,
                num_ways=2, stats_en=False,
                dirty_en=False ):
    self.size = size
    self.line_size = line_size
    # XXX: for now
    assert num_ways == 2
    self.num_ways = num_ways
    # we need the state to access num_insts for pseudo-random number
    # generation
    self.state = state

    # naive implementation: use a simple tag array implemented as an array
    # divide the number of ways to get the actual number of lines
    self.num_lines = ( self.size / self.line_size ) / self.num_ways
    # initialize the tag arrays
    self.tag_array = []
    for i in range( self.num_ways ):
      self.tag_array.append( [ -1 ] * self.num_lines )

    # initialize dirty array if enabled
    if dirty_en:
      self.dirty_array = []
      for i in range( self.num_ways ):
        self.dirty_array.append( [ False ] * self.num_lines )

    # initialize mru array
    self.mru_array = [ 0 ] * self.num_lines

    # calculate line_shamt: the shift amount to find the line base address
    self.line_shamt = 0
    ls = self.line_size
    while ls & 1 == 0:
      ls = ls >> 1
      self.line_shamt += 1

    # calculate tag_shamt: similar to line_shamt, but doesn't include
    # line_idx bits
    self.tag_shamt = self.line_shamt
    nl = self.num_lines
    while nl & 1 == 0:
      nl = nl >> 1
      self.tag_shamt += 1

    print "line_shamt", self.line_shamt
    print "tag_shamt", self.tag_shamt

    self.line_idx_mask = self.num_lines - 1

    self.debug = debug
    self.name  = name
    self.dirty_en = dirty_en
    self.stats_en = stats_en
    self.num_hits   = 0
    self.num_misses = 0
    self.num_evicts = 0
    self.num_reads  = 0
    self.num_writes = 0
    # we pick the victim picking algoritm
    self.get_victim = self.get_lru_victim
    if self.debug.enabled( "cache" ):
      print ( "%s init\nnum_lines = %d\nline_size = %d\n"
              "num_ways = %d\n"
              "line_shamt = %d\nline_idx_mask = %x" ) \
              % ( self.name,
                  self.num_lines,
                  self.line_size,
                  self.num_ways,
                  self.line_shamt,
                  self.line_idx_mask )

  # determine if we have a hit, and return the way if there is a hit,
  # otherwise -1
  # note: this can be made inlinable
  def get_hit( self, addr_sh, line_idx ):
    for i in range( self.num_ways ):
      tag = self.tag_array[i][ line_idx ]

      # TODO: we might want to change this not to  break or use control
      # flow here to ensure it gets properly unrolled in the jit like
      # following:
      #hit |= (addr_sh == clean_tag)

      if addr_sh == tag:
        #hit = True
        #hit_way = i
        #break

        return i

    return -1

  def get_pseudorand_victim( self, line_idx ):
    # for miss, we need to pick a victim, use num_insts (pseudo-random
    # replacement policy)
    return self.state.num_insts & (self.num_ways - 1)

  def get_lru_victim( self, line_idx ):
    # TODO: this is a limitiation right now:
    assert self.num_ways == 2
    if self.mru_array[ line_idx ] == 0:
      return 1
    else:
      return 0

  def update_mru( self, line_idx, way ):
    # TODO: this is a limitiation right now:
    assert self.num_ways == 2
    self.mru_array[ line_idx ] = way

  @unroll_safe
  def mark_transaction( self, type, address, size ):
    addr_sh = address >> self.line_shamt
    line_idx = addr_sh & self.line_idx_mask

    # TODO: enable the debug info
    #if self.debug.enabled( "cache" ):
    #  # also check if we had a hit or miss
    #  hit = ( self.tag_array[ line_idx ] == addr_sh )
    #  print "%s %s %s addr = %x, line_idx = %x" \
    #        % ( self.name,
    #            "read" if type == self.READ else "write",
    #            "hit" if hit else "miss",
    #            address, line_idx )

    # first check if we have a hit in any of the ways

    hit_way = self.get_hit( addr_sh, line_idx )
    hit = hit_way != -1

    # stats

    if self.stats_en:
      if type == self.READ:
        self.num_reads += 1
      else:
        self.num_writes += 1

    if hit:
      if self.stats_en:
        self.num_hits += 1

      # mark element as dirty if need be
      # note: might want to experiment with checking it first

      if self.dirty_en and type == self.WRITE:
        self.dirty_array[ hit_way ][ line_idx ] = True

      self.update_mru( line_idx, hit_way )

    else:
      if self.stats_en:
        self.num_misses += 1

      victim = self.get_victim( line_idx )

      if self.stats_en and self.dirty_en:
        dirty_victim = self.dirty_array[ victim ][ line_idx ]

        if dirty_victim:
          self.num_evicts += 1

      self.tag_array[ victim ][ line_idx ] = addr_sh

      if self.dirty_en:
        self.dirty_array[ victim ][ line_idx ] = ( type == self.WRITE )

      self.update_mru( line_idx, victim )

  def print_line( self, line_idx, way ):
    # get the base addr first
    addr_sh = self.tag_array[way][line_idx]

    # first print valid and dirty info -- it's invalid if addr_sh is -1
    valid = (addr_sh != -1)
    dirty = valid and self.dirty_en and self.dirty_array[way][line_idx]

    print "%s%s" % ( "V" if valid else " ",
                     "D" if dirty else " " ),

    # print the tag
    tag = addr_sh >> (self.tag_shamt - self.line_shamt)
    print "%s -" % ( pad_hex( tag if valid else 0 ) ),

    # now, contruct the base address, get the data from main mem, and
    # display
    base_addr = addr_sh << self.line_shamt

    # disable memory's caches and memory translation so that we don't
    # pollute the cache as we read it
    self.state.mem.raw_access = True

    for addr in range( base_addr, base_addr + self.line_size, 4 ):
      print "%s" % pad_hex( self.state.mem.read( addr, 4 ) ),

    self.state.mem.raw_access = False

  def dump( self ):
    # we need to loop over every cache line in the order of most recently
    # used to least

    for l in range( self.num_lines ):
      # find the order in which to visit the ways (most recently first)
      assert self.num_ways == 2
      mru = self.mru_array[ l ]
      lru = 0 if mru else 1

      print "%d" % ( 2*l ),
      self.print_line( l, mru )
      print

      print "%d" % ( 2*l + 1 ),
      self.print_line( l, lru )
      print

  def get_ll_line_state( self, line_idx, way, ll_line_state ):
    # TODO: these are here temporarily
    VALID_FLAG = 1
    DIRTY_FLAG = 2

    # get the base addr first
    addr_sh = self.tag_array[way][line_idx]

    # first get valid and dirty info -- it's invalid if addr_sh is -1
    valid = (addr_sh != -1)
    dirty = valid and self.dirty_en and self.dirty_array[way][line_idx]

    # get the tag
    tag = addr_sh >> (self.tag_shamt - self.line_shamt)

    # now, contruct the base address, get the data from main mem
    base_addr = addr_sh << self.line_shamt

    # write these to the data structure
    ll_line_state.tag = rffi.cast( rffi.UINT, tag )
    flags = 0
    flags |= VALID_FLAG if valid else 0
    flags |= DIRTY_FLAG if dirty else 0
    ll_line_state.flags = rffi.cast( rffi.UINT, flags )

    # disable memory's caches and memory translation so that we don't
    # pollute the cache as we read it
    self.state.mem.raw_access = True

    for i in range( self.line_size/4 ):
      addr = base_addr + i*4
      ll_line_state.data[i] = rffi.cast( rffi.UINT,
                                         self.state.mem.read( addr, 4 ) )

    self.state.mem.raw_access = False

  def get_ll_state( self, ll_state ):
    for l in range( self.num_lines ):
      # find the order in which to visit the ways (most recently first)
      assert self.num_ways == 2
      mru = self.mru_array[ l ]
      lru = 0 if mru else 1

      self.get_ll_line_state( l, mru, ll_state[ 2*l   ] )
      self.get_ll_line_state( l, lru, ll_state[ 2*l+1 ] )


  def stats_dump( self ):
    #for i in range( self.num_lines ):
    #  print "%d %x" % ( i, self.tag_array[ i ] )

    print "Stats for", self.name
    print     ( "num_hits   = %d\n"
                "num_misses = %d\n"
                "num_evicts = %d\n"
                "num_reads  = %d\n"
                "num_writes = %d\n" ) % \
              ( self.num_hits   ,
                self.num_misses ,
                self.num_evicts ,
                self.num_reads  ,
                self.num_writes , )
