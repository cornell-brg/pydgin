#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  _virtualizable_ = ['pc', 'ncycles']
  def __init__( self, memory, debug, reset_addr=0x400 ):
    self.pc       = reset_addr

    # TODO: to allow the register file to be virtualizable (to avoid array
    # lookups in the JIT), it needs to be an array as a member of the
    # State class. Couldn't figure out how to have rf a RegisterFile
    # object and still be virtualizable.
    self.rf       = RegisterFile()
    self.mem      = memory

    self    .debug = debug
    self.rf .debug = debug
    self.mem.debug = debug

    # coprocessor registers
    self.status        = 0
    self.stats_en      = 0
    self.ncycles       = 0
    self.stat_ncycles  = 0

    # we need a dedicated running flag bacase status could be 0 on a
    # syscall_exit
    self.running       = True

    # parc special
    self.src_ptr  = 0
    self.sink_ptr = 0

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

    # shreesha: PolyHS state
    self.ds_table = RegisterFile( constant_zero=False )
    self.ds_type  = RegisterFile( constant_zero=False )
    self.dt_table = RegisterFile( constant_zero=False )

    # stat registers
    self.stat_inst_en      = [ False ] * 16
    self.stat_inst_begin   = [ 0 ]     * 16
    self.stat_inst_ncycles = [ 0 ]     * 16

  def fetch_pc( self ):
    return self.pc
