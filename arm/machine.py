#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile
from pydgin.debug   import Debug, pad, pad_hex
from rpython.rlib.jit import unroll_safe, hint

class ReturnException( Exception ):

  def __init__( self, num_levels=1 ):
    self.num_levels = num_levels

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  _virtualizable_ = ['pc', 'ncycles', 'N', 'Z', 'C', 'V', 'status']
  def __init__( self, memory, debug, reset_addr=0x400, copy_from=None ):
    if copy_from is not None:

      self.pc       = copy_from.pc
      self.rf       = copy_from.rf
      self.rf.state = self
      self.mem      = copy_from.mem

      self    .debug = copy_from.debug

      # current program status register (CPSR)
      self.N    = copy_from.N      # Negative condition
      self.Z    = copy_from.Z      # Zero condition
      self.C    = copy_from.C      # Carry condition
      self.V    = copy_from.V      # Overflow condition
      #self.J    = 0b0      # Jazelle state flag
      #self.I    = 0b0      # IRQ Interrupt Mask
      #self.F    = 0b0      # FIQ Interrupt Mask
      #self.T    = 0b0      # Thumb state flag
      #self.M    = 0b00000  # Processor Mode

      # other registers
      self.status        = copy_from.status
      self.ncycles       = copy_from.ncycles
      self.status        = copy_from.status
      self.ncycles       = copy_from.ncycles
      # unused
      self.stats_en      = copy_from.stats_en
      self.stat_ncycles  = copy_from.stat_ncycles

      # syscall stuff... TODO: should this be here?
      self.breakpoint = copy_from.breakpoint

      self.run = copy_from.run
      self.max_insts = copy_from.max_insts

      self.nest_level = copy_from.nest_level + 1
      self.linked_state = copy_from
      self.link_pc = 0

    else:

      self.pc       = reset_addr
      self.rf       = ArmRegisterFile( self, num_regs=16 )
      self.mem      = memory

      self    .debug = debug
      self.rf .debug = debug
      self.mem.debug = debug

      self.rf[ 15 ]  = reset_addr

      # current program status register (CPSR)
      self.N    = 0b0      # Negative condition
      self.Z    = 0b0      # Zero condition
      self.C    = 0b0      # Carry condition
      self.V    = 0b0      # Overflow condition
      #self.J    = 0b0      # Jazelle state flag
      #self.I    = 0b0      # IRQ Interrupt Mask
      #self.F    = 0b0      # FIQ Interrupt Mask
      #self.T    = 0b0      # Thumb state flag
      #self.M    = 0b00000  # Processor Mode

      # other registers
      self.status        = 0
      self.ncycles       = 0
      ## unused
      self.stats_en      = 0
      self.stat_ncycles  = 0

      # syscall stuff... TODO: should this be here?
      self.breakpoint = 0

      self.nest_level = 0
      self.linked_state = None
      self.link_pc = 0

  def fetch_pc( self ):
    return self.pc

  def return_copy( self, other ):
    #hint( other, force_virtualizable=True )
    self.pc         = other.pc
    self.N          = other.N
    self.Z          = other.Z
    self.C          = other.C
    self.V          = other.V
    self.status     = other.status
    self.ncycles    = other.ncycles
    self.breakpoint = other.breakpoint
    self.stats_en   = other.stats_en
    self.stat_ncycles = other.stat_ncycles
    self.rf.state   = self

  def fun_call( self, old_pc, new_pc ):
    #print "fun_call %x %x %d" % ( old_pc, new_pc, self.nest_level )

    self.link_pc = old_pc
    new_state = State( None, None, copy_from=self )
    new_state.run( new_state, new_state.max_insts )

  @unroll_safe
  def fun_return( self, old_pc, new_pc ):

    search_space = 5
    state = self

    for i in xrange( 1, search_space ):
      state = state.linked_state

      if state is None:
        break

      #print "fun_return try %d %x %x" % (i, state.link_pc, new_pc)
      if state.link_pc + 4 == new_pc:
        state.return_copy( self )
        #print "fun_return %d %x %x %d" % (i, old_pc, new_pc,
        #                                  self.nest_level)
        raise ReturnException( i )
    #print "fun_noreturn %x %x %d" % (old_pc, new_pc, self.nest_level )

#-----------------------------------------------------------------------
# ArmRegisterFile
#-----------------------------------------------------------------------
class ArmRegisterFile( RegisterFile ):
  def __init__( self, state, num_regs=16 ):
    RegisterFile.__init__( self, constant_zero=False, num_regs=num_regs )
    self.state = state

  def __getitem__( self, idx ):
    # special-case for idx = 15 which is the pc
    if self.debug.enabled( "rf" ):
      if idx == 15:
        rd_str = pad_hex( self.state.pc ) + "+ 8"
      else:
        rd_str = pad_hex( self.regs[idx] )

      print ':: RD.RF[%s] = %s' % ( pad( "%d" % idx, 2 ), rd_str ),

    if idx == 15:
      return self.state.pc + 8
    else:
      return self.regs[idx]

  def __setitem__( self, idx, value ):
    if idx == 15:
      self.state.pc = value
      if self.debug.enabled( "rf" ):
        print ':: WR.RF[15] = %s' % ( pad_hex( value ) ),
    else:
      self.regs[idx] = value
      if self.debug.enabled( "rf" ):
        print ':: WR.RF[%s] = %s' % (
                          pad( "%d" % idx, 2 ),
                          pad_hex( value ) ),


