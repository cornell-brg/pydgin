#=========================================================================
# pipe_model.py
#=========================================================================

from pydgin.debug import pad, pad_hex

class Execution( object ):

  def __init__( self, pc=0, inst=None ):

    self.pc   = pc
    self.inst = inst

    self.read_regs = []
    # assume we have a single write port
    self.write_reg = -1

    self.is_branch = False

    self.squashed = False


class StallingProcPipelineModel( object ):

  def __init__( self, state ):

    # pipeline stages -- these are either execution objects or none

    self.F = None
    self.D = None
    self.X = None
    self.M = None
    self.W = None

    self.fetch_pc = state.fetch_pc()
    self.last_pc  = state.fetch_pc()

    self.state    = state

    self.num_cycles = 0


  def next_inst( self, inst ):

    pc = self.state.fetch_pc()

    if pc != self.last_pc + 4:
      # redirect the control flow
      self.fetch_pc = pc

      # squash F and D
      self.F.squashed = True
      self.D.squashed = True

    self.last_pc = pc

    # for each instruction, we cycle until we see the inst in x
    self.xtick()

    while self.X is None or pc != self.X.pc or self.X.squashed:
      self.xtick()

  def xtick( self ):

    if self.state.debug.enabled( "trace" ):
      self.print_trace()

    # the general behavior is a shifting behavior
    self.W = self.M
    self.M = self.X
    self.X = self.D
    self.D = self.F

    self.F = Execution( pc=self.fetch_pc )

    #if self.state.debug.enabled( "trace" ):
    #  self.print_trace()

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
    if stage is None:
      return pad( "", nchars )
    elif stage.squashed:
      return pad( "--", nchars )
    else:
      return pad( pad_hex( stage.pc, 6 ), nchars )
