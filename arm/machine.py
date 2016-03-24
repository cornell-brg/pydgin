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
  _immutable_fields_ = [ 'count_fun_calls', 'jit_mem_analysis' ]
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

    # pyxcel related:
    self.trig_state = 0
    self.event_file = None
    self.print_event = False
    self.event_ctrs = {}

    # function call analysis
    self.count_fun_calls = False

    # events to find out which phase pypy is currently in
    self.last_event = "begin"
    self.last_event_stack = None
    # only the events that have entries in here will be kept track
    self.event_num_insts = { "begin"            : 0,
                             "fun_call"         : 0,
                             "jit_block"        : 0,
                             "blackhole_start"  : 0,
                             "tracing_start"    : 0,
                             "tracing_start_gf" : 0, }
    self.num_insts_at_last_event = 0

    # jit mem analysis
    self.jit_mem_analysis = False
    self.check_jit_mem = False
    self.jit_mem_prev_stores = {}
    self.jit_mem_stores = {}
    self.jit_mem_num_conflicts = 0
    self.jit_mem_num_accesses = 0
    self.jit_mem_conflict_rates = []

    # mmap boundary
    from bootstrap import memory_size
    self.mmap_boundary = memory_size - 0x10000000 - 1

  def fetch_pc( self ):
    return self.pc

  def cpsr( self ):
    return ( self.N << 31 ) | \
           ( self.Z << 30 ) | \
           ( self.C << 29 ) | \
           ( self.V << 28 ) | \
           ( self.mode    )

  def record_load( self, addr ):
    # only if we're supposed to do mem analysis
    if self.jit_mem_analysis:
      if self.check_jit_mem:
        #print "record load"
        # for now just count the number of conflicts
        if addr in self.jit_mem_prev_stores:
          self.jit_mem_num_conflicts += 1
        self.jit_mem_num_accesses += 1

  def record_store( self, addr ):
    # only if we're supposed to do mem analysis
    if self.jit_mem_analysis:
      if self.check_jit_mem:
        #print "record store"
        if addr not in self.jit_mem_stores:
          self.jit_mem_stores[ addr ] = 1
        else:
          self.jit_mem_stores[ addr ] += 1


  # print pc only if non-zero
  def trigger_event( self, descr, pc=0, end_descr=None ):

    # start a new event
    if descr is not None and descr in self.event_num_insts:
      # because the last event wasn't properly ended store it
      self.last_event_stack = self.last_event

      if self.last_event is not None:
        # end the last event
        self.event_num_insts[ self.last_event ] += \
                (self.ncycles - self.num_insts_at_last_event)

      self.last_event = descr
      self.num_insts_at_last_event = self.ncycles

      # specific to jit blocks: add up the mem conflicts
      if descr == "jit_block":
        # check jit mem is true only if we had that enabled
        if self.jit_mem_analysis:
          # add the conflict rate only if there were stores from prev
          # iteration
          if self.check_jit_mem and len( self.jit_mem_prev_stores ) > 0 \
                and self.jit_mem_num_accesses > 0:
            self.jit_mem_conflict_rates.append(
                    float( self.jit_mem_num_conflicts ) /
                    float( self.jit_mem_num_accesses ) )

          self.check_jit_mem = True
          self.jit_mem_prev_stores = self.jit_mem_stores
          self.jit_mem_stores = {}
          self.jit_mem_num_conflicts = 0
          self.jit_mem_num_accesses = 0

      # certain events cancel the jit mem analysis
      if descr == "blackhole_start" or descr == "tracing_start" or \
          descr == "tracing_start_gf":
        if self.jit_mem_analysis:
          # add the conflict rate only if there were stores from prev
          # iteration
          if self.check_jit_mem and len( self.jit_mem_prev_stores ) > 0 \
                and self.jit_mem_num_accesses > 0:
            self.jit_mem_conflict_rates.append(
                    float( self.jit_mem_num_conflicts ) /
                    float( self.jit_mem_num_accesses ) )

          self.check_jit_mem = False
          self.jit_mem_prev_stores = {}
          self.jit_mem_stores = {}
          self.jit_mem_num_conflicts = 0
          self.jit_mem_num_accesses = 0


    # end an event
    elif end_descr is not None and end_descr in self.event_num_insts:
      # it's bad if we're trying to end an event that wasn't the last
      # event
      #if self.last_event != end_descr:
      #  print "end_descr=%s doesn't match last_event=%s pc=%x" % \
      #      (end_descr, self.last_event, self.pc)

      if self.last_event is not None:
        # end the last event
        self.event_num_insts[ self.last_event ] += \
                (self.ncycles - self.num_insts_at_last_event)

      # we pop the stack
      self.last_event = self.last_event_stack
      self.last_event_stack = None
      self.num_insts_at_last_event = self.ncycles

      # certain events cancel the jit mem analysis
      if end_descr == "jit_block":
        if self.jit_mem_analysis:
          # add the conflict rate only if there were stores from prev
          # iteration
          if self.check_jit_mem and len( self.jit_mem_prev_stores ) > 0 \
                and self.jit_mem_num_accesses > 0:
            self.jit_mem_conflict_rates.append(
                    float( self.jit_mem_num_conflicts ) /
                    float( self.jit_mem_num_accesses ) )

          # reset counters
          self.check_jit_mem = False
          self.jit_mem_prev_stores = {}
          self.jit_mem_stores = {}
          self.jit_mem_num_conflicts = 0
          self.jit_mem_num_accesses = 0


    if descr not in self.event_ctrs:
      self.event_ctrs[ descr ] = 1
      iter = 1
    else:
      iter = self.event_ctrs[ descr ] + 1
      self.event_ctrs[ descr ] = iter

    # if pc provided, append to descr
    if pc != 0:
      descr = "%s_%x" % ( descr, pc )
    if self.print_event:
      print descr, self.ncycles
    if self.event_file:
      # write events to a csv file
      self.event_file.write( "%s,%d,%d\n"
                          % (descr, self.ncycles, iter) )

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
      # pyxcel temp
      if self.state.count_fun_calls:
        if value == self.state.fun_call_return_pc:
          self.state.fun_call_return_pc = 0
          self.state.trigger_event( "fun_call_end", end_descr="fun_call" )

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
