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

  # size is the total size of the cache in bytes,
  # line_size is the cache line size in bytes
  def __init__( self, size, line_size, name, debug ):
    self.size = size
    self.line_size = line_size

    # naive implementation: use a simple tag array implemented as an array
    self.num_lines = self.size / self.line_size
    self.tag_array = [ r_uint32( 0 ) ] * self.num_lines

    # calculate line_shamt: the shift amount to find the line base address
    self.line_shamt = 0
    ls = self.line_size
    while ls & 1 == 0:
      ls = ls >> 1
      self.line_shamt += 1

    self.line_idx_mask = self.num_lines - 1

    self.debug = debug
    self.name  = name
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
      hit = ( widen( self.tag_array[ line_idx ] ) == addr_sh )
      print "%s %s %s addr = %x, line_idx = %x" \
            % ( self.name,
                "read" if type == self.READ else "write",
                "hit" if hit else "miss",
                address, line_idx )

    self.tag_array[ line_idx ] = r_uint32( addr_sh )

  def dump( self ):
    for i in range( self.num_lines ):
      print "%d %x" % ( i, widen( self.tag_array[ i ] ) )

