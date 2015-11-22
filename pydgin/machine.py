#=======================================================================
# machine.py
#=======================================================================

#-----------------------------------------------------------------------
# Machine
#-----------------------------------------------------------------------
class Machine( object ):
  def __init__( self, memory, register_file, debug, reset_addr=0x400 ):

    self.pc       = reset_addr
    self.rf       = register_file
    self.mem      = memory

    self    .debug = debug
    self.rf .debug = debug
    self.mem.debug = debug

    # common registers
    self.status          = 0
    self.stats_en        = 0
    self.num_insts       = 0
    self.stat_num_insts  = 0
    self.vlen            = 0

    # we need a dedicated running flag because status could be 0 on a
    # syscall_exit
    self.running       = True

  def fetch_pc( self ):
    return self.pc
