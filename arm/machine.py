#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile
from pydgin.debug   import Debug, pad, pad_hex

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  _virtualizable_ = ['pc', 'ncycles']
  def __init__( self, memory, debug, reset_addr=0x400 ):
    self.pc       = reset_addr
    self.rf       = ArmRegisterFile( self, num_regs=16 )
    self.mem      = memory

    self    .debug = debug
    self.rf .debug = debug
    self.mem.debug = debug

    self.rf.__setitem__( 15, reset_addr )

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

    # processor modes:
    # 0b10000     usr
    # 0b10001     fiq
    # 0b10010     irq
    # 0b10011     svc (supervisor)
    # 0b10111     abt (abort)
    # 0b11011     und (undefined)
    # 0b11111     sys
    self.mode = 0b10000

    # other registers
    self.status        = 0
    self.ncycles       = 0
    # unused
    self.stats_en      = 0
    self.stat_ncycles  = 0

    # marks if should be running, syscall_exit sets it false
    self.running       = True

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

  def fetch_pc( self ):
    return self.pc

  def cpsr( self ):
    return ( self.N << 31 ) | \
           ( self.Z << 30 ) | \
           ( self.C << 29 ) | \
           ( self.V << 28 ) | \
           ( self.mode    )

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


  # we also print the status flags on print_regs
  def print_regs( self, per_row=6 ):
    RegisterFile.print_regs( self, per_row )
    print '%s%s%s%s' % (
      'N' if self.state.N else '-',
      'Z' if self.state.Z else '-',
      'C' if self.state.C else '-',
      'V' if self.state.V else '-'
    )
