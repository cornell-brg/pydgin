#=========================================================================
# simpoint.py
#=========================================================================
# BBV generation

from pydgin.jit import elidable_promote

class BasicBlockInfo:
  _immutable_fields_ = [ "num_insts" ]

  def __init__( self, num_insts ):
    self.num_insts = num_insts
    self.ctr = 0

  def increment( self ):
    self.ctr += self.num_insts

  def reset( self ):
    self.ctr = 0

class BasicBlockVector:

  def __init__( self ):
    # the actual bbv which uses indexes by the bbv_map
    self.bbv = []
    # this maps pcs to bb index
    self.bbv_map = {}

    # last num instructions is only for new basic blocks
    self.last_num_insts = 0

  # increments the counter for the basic block
  def mark_bb( self, old_pc, new_pc, num_insts ):
    bb_idx = self.get_bb_idx( old_pc, new_pc )

    # code for a new bb, shouldn't happen in the jit
    if bb_idx == -1:
      bb_sig = (old_pc << 32) | new_pc
      self.bbv_map[bb_sig] = len( self.bbv )

      # calculate the number of instructions
      bb_num_insts = num_insts - self.last_num_insts

      self.bbv.append( BasicBlockInfo( bb_num_insts ) )
      bb_idx = self.bbv_map[bb_sig]

    self.bbv[ bb_idx ].increment()

    # TODO: this might be inefficient?
    self.last_num_insts = num_insts

  # get bb index
  @elidable_promote()
  def get_bb_idx( self, old_pc, new_pc ):
    # hacky: compose pcs to generate a unique signature
    bb_sig = (old_pc << 32) | new_pc
    if bb_sig not in self.bbv_map:
      # rpython complains when we append bb info to bbv here because it
      # conflicts with elidable decorator. instead, we return -1 and
      # handle this case of an unseen bb (which shouldn't happen in the
      # jit by definition) in mark_bb
      return -1

    return self.bbv_map[bb_sig]

  def reset( self ):
    for i in range( len( self.bbv ) ):
      self.bbv[i].reset()

  def dump( self ):
    printed_t = False
    for i in range( len( self.bbv ) ):
      ctr = self.bbv[i].ctr
      if ctr > 0:
        if not printed_t:
          print "T:%d:%d" % ( i+1, ctr ),
          printed_t = True
        else:
          print ":%d:%d" % ( i+1, ctr ),

    print
