#=========================================================================
# machine.py
#=========================================================================

from pydgin.storage import RegisterFile

#-------------------------------------------------------------------------
# State
#-------------------------------------------------------------------------
class State( object ):
  # TODO: add virtualizables

  def __init__( self, memory, debug, reset_addr=0x400 ):
    self.pc       = reset_addr

    # TODO: don't know what this is:
    self.xlen     = 64

    self.rf       = RegisterFile()
    self.mem      = memory

    self    .debug = debug
    self.rf .debug = debug
    self.mem.debug = debug

    # coprocessor registers
    self.status          = 0
    self.stats_en        = 0
    self.num_insts       = 0
    self.stat_num_insts  = 0

    # we need a dedicated running flag bacase status could be 0 on a
    # syscall_exit
    self.running       = True

    # indicate if this is running a self-checking test
    self.testbin  = False

    # executable name
    self.exe_name = ""

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

  def fetch_pc( self ):
    return self.pc
