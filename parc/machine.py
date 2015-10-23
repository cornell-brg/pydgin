#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine
from pydgin.storage import RegisterFile

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( Machine ):
  #_virtualizable_ = ['pc', 'num_insts']
  def __init__( self, memory, debug, reset_addr=0x400, core_id=0, ncores=1 ):
    Machine.__init__(self, memory, RegisterFile(), debug, reset_addr=reset_addr )

    # parc special
    self.src_ptr  = 0
    self.sink_ptr = 0

    # indicate if this is running a self-checking test
    self.testbin  = False

    # executable name
    self.exe_name = ""

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

    # multicore stuff
    self.core_id = core_id
    self.ncores  = ncores

    # indicates if pkernel is enabled
    self.pkernel = False
    # indicates exception handling address for pkernel only
    self.except_addr = 0
    # epc is the address to return back to that eret uses
    self.epc = 0

    # stat registers
    self.stat_inst_en      = [ False ] * 16
    self.stat_inst_begin   = [ 0 ]     * 16
    self.stat_inst_num_insts = [ 0 ]     * 16

  def fetch_pc( self ):
    return self.pc
