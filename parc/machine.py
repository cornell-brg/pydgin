#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine
from pydgin.storage import RegisterFile

#-----------------------------------------------------------------------
# StrandStackEntry
#-----------------------------------------------------------------------

class StrandStackEntry( object ):
  def __init__( self ):
    self.strand_list = []

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

    # Explicit parallel call registers. We keep track of the current work
    # index, the requested number of calls and the start address of the
    # function to call.
    self.xpc_en             = False
    self.xpc_start_idx      = 0
    self.xpc_end_idx        = 0
    self.xpc_idx            = 0
    self.xpc_start_addr     = 0x00000000
    self.xpc_return_addr    = 0x00000000
    self.xpc_saved_ra       = 0x00000000
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

    # multicore stuff
    self.core_id = core_id
    self.ncores  = ncores

    # indicates if pkernel is enabled
    self.pkernel = False
    # indicates exception handling address for pkernel only
    self.except_addr = 0
    # epc is the address to return back to that eret uses
    self.epc = 0

    # core type and stats core type for xpc
    self.core_type = 0
    self.stats_core_type = 0

    # accel rf mode for xpc
    self.accel_rf = False

    # xpc stats
    self.num_pcalls = 0

    # stat registers
    self.stat_inst_en      = [ False ] * 16
    self.stat_inst_begin   = [ 0 ]     * 16
    self.stat_inst_num_insts = [ 0 ]     * 16

    # shreesha: task tracing
    # 0 = child, 1 = continuation
    self.strand_type = 0
    # global strand count
    self.g_strand_count = 0
    # current strand
    self.curr_strand = 0
    # strand queue to track the execution order
    self.strand_queue = []
    # strand stack
    # each entry of the stack corresponds to the strands that
    # are the children of a spawn point for a given level in the dag
    self.strand_stack = []
    # corresponds to the strand that yielded
    self.prev_strand_stack = []

    # flag to indicate if we are in a parallel section
    self.parallel_mode = False

    # flag to indicate runtime mode
    self.runtime_mode = False
    # runtime ras
    self.runtime_ras = []

    # flag to indicate task mode
    self.task_mode = False
    # task ras
    self.task_ras = []

    # strand graph
    self.strand_graph = []
    # strand trace
    self.strand_trace = []
    # strand joins
    self.strand_joins = []

    # task runtime addr,name dict
    self.runtime_dict = {}

    # parallel region
    self.parallel_section_counter = 0

    # stats region
    # NOTE: At the moment, we allow for 16 named stats regions
    #
    # Stat regions of interest:
    #   13 : local enqueue
    #   12 : local dequeue
    #   10 : task execution
    self.stats_on     = [0]*16   # instructions count when stats was turned on
    self.stats_insts  = [0]*16   # total number of dynamic instructions per-stats region
    self.stats_counts = [0]*16   # total number of times each stats region was executed

    self.serial_insts = 0  # instructions count in serial sections
    self.runtime_insts = 0 # instructions count in runtime sections

  def fetch_pc( self ):
    return self.pc
