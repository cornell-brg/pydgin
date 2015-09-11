#=========================================================================
# cache.py
#=========================================================================
# Cache models

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
  _immutable_fields_ = [ "stats_en" ]

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
        if (raw_tag & 0x80000000) != 0:
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
