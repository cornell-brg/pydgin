#=========================================================================
# simpoint.py
#=========================================================================

from pydgin.jit import elidable_promote

class BasicBlockVector:

  def __init__( self ):
    # the actual bbv which uses indexes by the bbv_map
    self.bbv = []
    # this maps pcs to bb index
    self.bbv_map = {}
    pass

  # increments the counter for the basic block
  def mark_bb( self, pc ):
    bb_idx = self.get_bb_idx( pc )
    self.bbv[ bb_idx ] += 1

  @elidable_promote()
  def get_bb_idx( self, pc ):
    if pc not in self.bbv_map:
      self.bbv_map[pc] = len( self.bbv )
      self.bbv.append( 0 )

    return self.bbv_map[pc]

  def reset( self ):
    for i in range( len( self.bbv ) ):
      self.bbv[i] = 0

  def dump( self ):
    printed_t = False
    for i in range( len( self.bbv ) ):
      ctr = self.bbv[i]
      if ctr > 0:
        if not printed_t:
          print "T:%d:%d" % ( i, ctr ),
          printed_t = True
        else:
          print ":%d:%d" % ( i, ctr ),

    print
