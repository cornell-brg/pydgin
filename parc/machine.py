#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  _immutable_fields_ = [ 'debug?', 'rf', 'mem' ]
  _virtualizable_ = ['pc', 'ncycles']
  def __init__( self, memory, debug, reset_addr=0x400 ):
    self.pc       = reset_addr

    # TODO: to allow the register file to be virtualizable (to avoid array
    # lookups in the JIT), it needs to be an array as a member of the
    # State class. Couldn't figure out how to have rf a RegisterFile
    # object and still be virtualizable.
    self.rf        = RegisterFile( self )
    self.mem       = memory
    self.mem.state = self

    self.debug = debug

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

  def fetch_pc( self ):
    return self.pc
