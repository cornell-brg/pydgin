#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile
from pydgin.debug   import Debug, pad, pad_hex
from rpython.rlib.jit import unroll_safe

class ReturnException( Exception ):

  def __init__( self, num_levels=1 ):
    self.num_levels = num_levels

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  #_virtualizable_ = ['pc', 'ncycles']
  def __init__( self, memory, debug, reset_addr=0x400 ):
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
    # unused
    self.stats_en      = 0
    self.stat_ncycles  = 0

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

    self.nest_level = 0
    self.call_stack = []

  def fetch_pc( self ):
    return self.pc

  def fun_call( self, old_pc, new_pc ):
    #print "fun_call %x %x %d" % ( old_pc, new_pc, self.nest_level )
    self.nest_level += 1
    self.call_stack.append( old_pc )
    self.run( self, self.max_insts )

  @unroll_safe
  def fun_return( self, old_pc, new_pc ):
    exp_pc = self.call_stack[-1] + 4
    if exp_pc == new_pc:
      self.call_stack.pop()
      self.nest_level -= 1
      #print "fun_return %x %x %d" % (old_pc, new_pc, self.nest_level )
      raise ReturnException()
    else:
      # we search for other frames this might be returning to
      search_space = 5

      for i in xrange( 1, min( len( self.call_stack ), search_space ) ):
        exp_pc = self.call_stack[ -i ] + 4
        #print "fun try %d %x %x %x" % ( i, exp_pc, old_pc, new_pc )
        if exp_pc == new_pc:
          #print "fun found return %d %x %x" % ( i, old_pc, new_pc )
          for j in xrange( i ):
            self.call_stack.pop()
          self.nest_level -= i
          raise ReturnException( i )

      #print "fun_noreturn %x %x %d" % (old_pc, new_pc, self.nest_level )
      pass

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


