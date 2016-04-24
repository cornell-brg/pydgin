#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine
from pydgin.storage import RegisterFile
from pydgin.utils   import r_uint
from mmu.tlb        import PageTable

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( Machine ):
  _virtualizable_ = ['pc', 'num_insts']
  _immutable_fields_ = ['enable_page_table']
  def __init__( self, memory, debug, reset_addr=0x400):
    Machine.__init__(self, memory, RegisterFile(), debug, reset_addr=reset_addr )

    # parc special
    self.src_ptr  = 0
    self.sink_ptr = 0

    # indicate if this is running a self-checking test
    self.testbin  = False

    # executable name
    self.exe_name = ""

    # syscall stuff... TODO: should this be here?
    self.breakpoint = r_uint( 0 )

    # MMU project: add counters for loads/stores
    self.num_reads = 0
    self.num_ireads = 0
    self.num_writes = 0

    # MMU project: page table
    self.enable_page_table = False
    self.page_table = PageTable(8)

  def fetch_pc( self ):
    return self.pc
