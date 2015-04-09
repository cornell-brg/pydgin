#=========================================================================
# pipe_model.py
#=========================================================================

from pydgin.debug import pad, pad_hex
from isa          import get_inst_rw, get_inst_stall_cycles
from rpython.rlib.jit import unroll_safe

#-------------------------------------------------------------------------
# ExecutionToken
#-------------------------------------------------------------------------

class ExecutionToken( object ):

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
        return ExecutionToken( valid=False ), False
      else:
        return other, False
    else:
      return self, True

  def squash( self ):
    if self.valid:
      self.squashed = True
      self.valid = False
      self.stalled = False

  def get_repr( self, disasm=False ):
    repr = pad_hex( self.pc, 6 )
    if disasm:
      repr += ":" + self.inst.str
    return repr

  def get_stage_str( self, stage_idx ):
    if stage_idx < 2:
      nchars = 10
      disasm = False
    else:
      nchars = 16
      disasm = True

    if not self.valid:
      return pad( "", nchars )
    elif self.stalled:
      return pad( self.get_repr( disasm ) + " S", nchars )
    elif self.squashed:
      return pad( "--", nchars )
    else:
      return pad( self.get_repr( disasm ), nchars )

#-------------------------------------------------------------------------
# StallingProcPipelineModel
#-------------------------------------------------------------------------

class StallingProcPipelineModel( object ):

  def __init__( self, state ):

    # pipeline stages -- these are either execution objects or none

    self.F = ExecutionToken( valid=False )
    self.D = ExecutionToken( valid=False )
    self.X = ExecutionToken( valid=False )
    self.M = ExecutionToken( valid=False )
    self.W = ExecutionToken( valid=False )

    self.fetch_pc = state.fetch_pc()
    self.last_pc  = state.fetch_pc()

    self.state    = state

    self.num_cycles = 0
    self.num_squashes = 0
    self.num_llfu_stalls = 0
    self.num_raw_stalls = 0

  def is_in_flight( self, reg ):
    if self.M.valid and self.M.write_reg == reg:
      return True
    if self.W.valid and self.W.write_reg == reg:
      return True
    return False

  @unroll_safe
  def next_inst( self, inst ):

    # for each instruction, we cycle until we see the inst in x
    self.xtick()

    while not self.X.valid or self.last_pc != self.X.pc or self.X.squashed:
      self.xtick()

    # self.X contains this instruction

    self.X.inst = inst
    reg_reads, reg_writes = get_inst_rw( inst )
    stall_cycles = get_inst_stall_cycles( inst )
    self.X.write_reg = reg_writes[0] if len( reg_writes ) > 0 else -1
    self.X.stalled = True

    for i in xrange( stall_cycles ):
      self.xtick()
      self.num_llfu_stalls += 1

    for reg_read in reg_reads:
      while self.is_in_flight( reg_read ):
        self.xtick()
        self.num_raw_stalls += 1

    self.X.stalled = False

    pc = self.state.fetch_pc()

    if pc != self.last_pc + 4:
      # redirect the control flow
      self.fetch_pc = pc

      # squash F and D
      self.F.squashed = True
      self.D.squashed = True

      self.num_squashes += 2

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
    self.F, stalled = self.F.pipe_shift( ExecutionToken( pc=self.fetch_pc ), stalled )

    #if self.state.debug.enabled( "trace" ):
    #  self.print_trace()

    if not stalled:
      self.fetch_pc += 4
    self.num_cycles += 1


  def print_trace( self ):
    trace = "%d: " % self.num_cycles + \
            self.F.get_stage_str( 0 ) + "|" + \
            self.D.get_stage_str( 1 ) + "|" + \
            self.X.get_stage_str( 2 ) + "|" + \
            self.M.get_stage_str( 3 ) + "|" + \
            self.W.get_stage_str( 4 )
    print trace
