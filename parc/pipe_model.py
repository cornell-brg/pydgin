#=========================================================================
# pipe_model.py
#=========================================================================

from pydgin.debug import pad, pad_hex
from isa          import get_inst_rw

class Execution( object ):

  def __init__( self, pc=0, inst=None, valid=True ):

    self.pc   = pc
    self.inst = inst

    #self.read_regs = []
    # assume we have a single write port
    self.write_reg = -1

    #self.is_branch = False

    self.squashed = False
    self.stalled  = False
    self.valid    = valid

  def pipe_shift( self, other, stall ):
    if not self.stalled and not stall:
      if other.stalled:
        # create a bubble
        return Execution( valid=False ), False
      else:
        return other, False
    else:
      return self, True

  def squash( self ):
    if self.valid:
      self.squashed = True
      self.valid = False
      self.stalled = False

class StallingProcPipelineModel( object ):

  def __init__( self, state ):

    # pipeline stages -- these are either execution objects or none

    self.F = Execution( valid=False )
    self.D = Execution( valid=False )
    self.X = Execution( valid=False )
    self.M = Execution( valid=False )
    self.W = Execution( valid=False )

    self.fetch_pc = state.fetch_pc()
    self.last_pc  = state.fetch_pc()

    self.state    = state

    self.num_cycles = 0

  def is_in_flight( self, reg ):
    if self.M.valid and self.M.write_reg == reg:
      return True
    if self.W.valid and self.W.write_reg == reg:
      return True
    return False

  def next_inst( self, inst ):

    # for each instruction, we cycle until we see the inst in x
    self.xtick()

    while not self.X.valid or self.last_pc != self.X.pc or self.X.squashed:
      self.xtick()

    # self.X contains this instruction

    self.X.inst = inst
    reg_reads, reg_writes = get_inst_rw( inst )
    self.X.write_reg = reg_writes[0] if len( reg_writes ) > 0 else -1
    self.X.stalled = True

    for reg_read in reg_reads:
      while self.is_in_flight( reg_read ):
        self.xtick()

    self.X.stalled = False

    pc = self.state.fetch_pc()

    if pc != self.last_pc + 4:
      # redirect the control flow
      self.fetch_pc = pc

      # squash F and D
      self.F.squashed = True
      self.D.squashed = True

    self.last_pc = pc


  def xtick( self ):

    if self.state.debug.enabled( "trace" ):
      self.print_trace()

    stalled = False

    # the general behavior is a shifting behavior
    self.W, stalled = self.W.pipe_shift( self.M, stalled )
    self.M, stalled = self.M.pipe_shift( self.X, stalled )
    self.X, stalled = self.X.pipe_shift( self.D, stalled )
    self.D, stalled = self.D.pipe_shift( self.F, stalled )
    self.F, stalled = self.F.pipe_shift( Execution( pc=self.fetch_pc ), stalled )

    #if self.state.debug.enabled( "trace" ):
    #  self.print_trace()

    if not stalled:
      self.fetch_pc += 4
    self.num_cycles += 1


  def print_trace( self ):
    trace = "%d: " % self.num_cycles + \
            self.get_stage_str( self.F ) + \
            self.get_stage_str( self.D ) + \
            self.get_stage_str( self.X ) + \
            self.get_stage_str( self.M ) + \
            self.get_stage_str( self.W )
    print trace

  def get_stage_str( self, stage ):
    nchars = 10
    if not stage.valid:
      return pad( "", nchars )
    elif stage.stalled:
      return pad( pad_hex( stage.pc, 6 ) + " S", nchars )
    elif stage.squashed:
      return pad( "--", nchars )
    else:
      return pad( pad_hex( stage.pc, 6 ), nchars )
