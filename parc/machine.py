#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine
from pydgin.storage import RegisterFile

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( Machine ):
  _virtualizable_ = ['pc', 'num_insts']
  def __init__( self, memory, debug, reset_addr=0x400):
    Machine.__init__(self, memory, RegisterFile(), debug, reset_addr=reset_addr )

    # parc special
    self.src_ptr  = 0
    self.sink_ptr = 0

    # Explicit parallel call registers. We keep track of the current work
    # index, the requested number of calls and the start address of the
    # function to call.
    self.xpc_en             = False
    self.xpc_start_idx      = 0
    self.xpc_end_idx        = 0
    self.xpc_idx            = 0
    self.xpc_start_addr     = 0x00000000
    self.xpc_return_addr    = 0x00000000
    self.xpc_return_trigger = 1
    self.xpc_pcall_type     = '' # Identifier for pcall variants

    # Separate accelerator regfile. Currently we only model a single-lane
    # accelerator with a vector length of 1.
    self.xpc_rf = RegisterFile()

    # We need a separate "pointer" to the current active regfile
    # depending on whether we are executing a pcall or not. We save a
    # copy of the scalar register file into a separate variable then use
    # the s.rf variable as the active regfile pointer.
    self.scalar_rf = self.rf

    # indicate if this is running a self-checking test
    self.testbin  = False

    # executable name
    self.exe_name = ""

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

    # core type and stats core type for xpc
    self.core_type = 0
    self.stats_core_type = 0

    # stat registers
    self.stat_inst_en        = [ False ] * 16
    self.stat_inst_begin     = [ 0 ]     * 16
    self.stat_inst_num_insts = [ 0 ]     * 16

  def fetch_pc( self ):
    return self.pc
