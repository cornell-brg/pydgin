#=======================================================================
# machine.py
#=======================================================================

from pydgin.storage import RegisterFile
from pydgin.debug   import Debug, pad, pad_hex
from pydgin.misc    import FatalError

# XXX hacky
from pydgin.storage import _WordMemory

# XXX hacky
class PtrTrap( object ):
  def __init__( self, trap_pc ):
    self.trap_pc = trap_pc
    #self.num_mem_sts = 0
    #self.num_access_same = 0
    #self.num_access_changed = 0
    self.src_ptr = 0
    self.dest_ptr = 0

    self.num_src_ptr_mem_sts = 0
    self.num_src_ptr_same = 0
    self.num_src_ptr_changed = 0
    self.num_dest_ptr_mem_sts = 0
    self.num_dest_ptr_same = 0
    self.num_dest_ptr_changed = 0

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

    # XXX: hacky
    self.mem.state = self
    self.prejump_pc = 0
    self.jit_block_hist = {}
    self.guard_fail_hist = {}
    self.guard_bridge_hist = {}
    self.fun_call_hist = {}
    # the following trap is set up by fun_call_trigger and causes the
    # function call to be added to the fun_call_hist if the call is taken
    self.fun_call_trap = False
    # go through the debug flags and the stuff that start with + are
    # considered ptr traps
    self.ptr_traps = {}
    self.ptr_traps_src_ptr_dict = {}
    self.ptr_traps_dest_ptr_dict = {}

    self.jit_region_begin = 0
    self.jit_region_end   = 0

    #self.ptr_traps_rev = {}
    # stats for ptr traps
    #self.ptr_trap_stats = {}

    #for flag in self.debug.enabled_flags:
    #  if flag.startswith( "+" ):
    #    ptr = int( flag[1:], 16 )
    #    print "adding ptr_trap for pc: %s" % hex( ptr )
    #    self.ptr_traps[ ptr ] = 0

    # pyxcel: if there is a debug file provided, we load it
    for flag in self.debug.enabled_flags:
      print flag
      if flag.startswith( "debugfile=" ):
        self.load_debug_file( flag[ len( "debugfile=" ) : ] )

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

    # mmap boundary
    from bootstrap import memory_size
    self.mmap_boundary = memory_size - 0x10000000 - 1

    self.trig_state = 0
    self.in_jit = False

  def fetch_pc( self ):
    return self.pc

  def cpsr( self ):
    return ( self.N << 31 ) | \
           ( self.Z << 30 ) | \
           ( self.C << 29 ) | \
           ( self.V << 28 ) | \
           ( self.mode    )

  # XXX: hacky
  #def check_ptr_trap_pc_hit( self, value ):
  #  if self.pc in self.ptr_traps:
  #    old_val = self.ptr_traps[ self.pc ]
  #    if value != old_val:
  #      if self.debug.enabled( "trap" ):
  #        print "ptr_trap changed pc: %s value: %s" % \
  #              ( hex( self.pc ), hex( value ) )
  #      self.ptr_traps[ self.pc ].num_access_changed += 1
  #      self.ptr_traps[ self.pc ] = value
  #      # construct a reverse dict
  #      self.ptr_traps_rev = {}
  #      for pc, ptr in self.ptr_traps.items():
  #        if ptr in self.ptr_traps_rev:
  #          self.ptr_traps_rev[ ptr ].append( pc )
  #        else:
  #          self.ptr_traps_rev[ ptr ] = [ pc ]

  #      if self.debug.enabled( "trap" ):
  #        hex_keys = []
  #        for k in self.ptr_traps_rev.keys():
  #          hex_keys.append( hex( k ) )
  #        print "keys: %s" % hex_keys
  #    else:
  #      if self.debug.enabled( "trap" ):
  #        print "ptr_trap pc: %s value: %s" % \
  #              ( hex( self.pc ), hex( value ) )
  #      self.ptr_traps[ self.pc ].num_access_same += 1
  #      #print self.ptr_traps_rev.values()

  def check_ptr_trap_mem_ld( self, addr, value ):
    if self.pc in self.ptr_traps:
      new_src_ptr  = addr
      new_dest_ptr = value
      ptr_trap     = self.ptr_traps[ self.pc ]
      old_src_ptr  = ptr_trap.src_ptr
      old_dest_ptr = ptr_trap.dest_ptr

      # src ptr

      if new_src_ptr != old_src_ptr:
        if self.debug.enabled( "trap" ):
          print "ptr_trap src_ptr changed pc: %s old: %s new: %s" % \
              ( hex( ptr_trap.trap_pc ),
                hex( old_src_ptr ), hex( new_src_ptr ) )
        ptr_trap.num_src_ptr_changed += 1
        ptr_trap.src_ptr = new_src_ptr

        # construct a reverse dict
        #self.ptr_traps_src_ptr_dict = {}
        #for pc, pt in self.ptr_traps.items():
        #  ptr = pt.src_ptr
        #  if ptr in self.ptr_traps_src_ptr_dict:
        #    self.ptr_traps_src_ptr_dict[ ptr ].append( pc )
        #  else:
        #    self.ptr_traps_src_ptr_dict[ ptr ] = [ pc ]
      else:
        ptr_trap.num_src_ptr_same += 1

      # dest ptr

      if new_dest_ptr != old_dest_ptr:
        if self.debug.enabled( "trap" ):
          print "ptr_trap dest_ptr changed pc: %s old: %s new: %s" % \
              ( hex( ptr_trap.trap_pc ),
                hex( old_dest_ptr ), hex( new_dest_ptr ) )
        ptr_trap.num_dest_ptr_changed += 1
        ptr_trap.dest_ptr = new_dest_ptr

        # construct a reverse dict
        #self.ptr_traps_dest_ptr_dict = {}
        #for pc, pt in self.ptr_traps.items():
        #  ptr = pt.dest_ptr
        #  if ptr in self.ptr_traps_dest_ptr_dict:
        #    self.ptr_traps_dest_ptr_dict[ ptr ].append( pc )
        #  else:
        #    self.ptr_traps_dest_ptr_dict[ ptr ] = [ pc ]
      else:
        ptr_trap.num_dest_ptr_same += 1


  def check_trap( self, addr, value, ptr_dict, type ):
    if addr in ptr_dict:
      trap_pcs = ptr_dict[ addr ]

      if self.debug.enabled( "trap" ):
        trap_pcs_str = []
        for pc in trap_pcs:
          trap_pcs_str.append( hex( pc ) )
        print "ptr_trap mem_st %s addr: %s value: %s st_pc: %s trap_pc: %s" % \
             ( type, hex( addr ), hex( value ), hex( self.pc ), trap_pcs_str )
      # register this event
      for trap_pc in trap_pcs:
        if type == "src_ptr":
          self.ptr_traps[ trap_pc ].num_src_ptr_mem_sts += 1
        elif type == "dest_ptr":
          self.ptr_traps[ trap_pc ].num_dest_ptr_mem_sts += 1

  # XXX: hacky
  def check_ptr_trap_mem_st( self, addr, value ):
    addr = addr & 0xfffffffc

    #self.check_trap( addr, value, self.ptr_traps_src_ptr_dict,  "src_ptr"  )
    #self.check_trap( addr, value, self.ptr_traps_dest_ptr_dict, "dest_ptr" )

  #-----------------------------------------------------------------------
  # load_debug_file
  #-----------------------------------------------------------------------
  # this is pyxcel specific: load debug file and read stuff from it

  def add_ptr_trap( self, pc ):
    if pc not in self.ptr_traps:
      self.ptr_traps[ pc ] = PtrTrap( pc )

  def is_in_jit_region( self ):
    return self.jit_region_begin != 0       and \
           self.jit_region_begin <= self.pc and \
           self.jit_region_end   >= self.pc

  def load_debug_file( self, filename ):
    file = open( filename, "r" )

    line = file.readline()
    while line != "":
      if line.startswith( "ptr_trap:" ):
        line = line.rstrip()
        ptr_trap_str = line[ len( "ptr_trap:" ) : ]
        ptr_trap_pc = int( ptr_trap_str, 16 )
        self.add_ptr_trap( ptr_trap_pc )

      elif line.startswith( "jit_region" ):
        tokens = line.rstrip().split( ":" )
        self.jit_region_begin = int( tokens[1], 16 )
        self.jit_region_end   = int( tokens[2], 16 )
        print "jit_region %x %x" % ( self.jit_region_begin,
                                     self.jit_region_end )

      line = file.readline()

    print "ptr_traps:"
    for ptr_trap in self.ptr_traps:
      print "%s, " % hex( ptr_trap ),
    print

    file.close()

  #-----------------------------------------------------------------------
  # function calls
  #-----------------------------------------------------------------------

  def check_fun_call_trap( self, taken ):
    if self.fun_call_trap and taken:
      self.fun_call_hist[ self.pc ] = self.fun_call_hist.get( self.pc, 0 ) + 1
    self.fun_call_trap = False

  #-----------------------------------------------------------------------
  # triggers for various events
  #-----------------------------------------------------------------------

  def jit_block_trigger( self ):
    # for jit blocks, we use pc - 8 of the trigger
    idx = self.pc - 8
    self.jit_block_hist[ idx ] = self.jit_block_hist.get( idx, 0 ) + 1
    if self.debug.enabled( "trigger" ):
      print "jit_block_trigger %s" % hex( idx )

    self.in_jit = True

  def guard_fail_trigger( self, bridge_compiled=False ):
    # for guard failures, we use the prejump pc
    idx = self.prejump_pc
    if bridge_compiled:
      self.guard_bridge_hist[ idx ] = self.guard_bridge_hist.get( idx, 0 ) + 1
    else:
      self.guard_fail_hist[ idx ] = self.guard_fail_hist.get( idx, 0 ) + 1
    if self.debug.enabled( "trigger" ):
      print "guard_fail_trigger bridge=%s %s" % ( bridge_compiled,
                                                  hex( idx ) )

    self.in_jit = False

  def load_trigger( self ):
    # add the loads to ptr_trap
    idx = self.pc + 4
    if self.debug.enabled( "trigger" ):
      print "load_trigger %s" % hex( idx )

    self.add_ptr_trap( idx )

    # hack to speed up simulation: once processed, rewrite this pc to r1,
    # r1 to defuse the trigger
    self.mem.write( self.pc, 4, 0xe2811000 )


  def store_trigger( self ):
    # hack: treat store triggers as load for the time being
    self.load_trigger()

  def finish_trigger( self ):
    self.in_jit = False

  def fun_call_trigger( self ):
    # instead of all function calls, we want to add the taken function
    # calls here. so we set up a trap here
    self.fun_call_trap = True

  #-----------------------------------------------------------------------
  # print_stats
  #-----------------------------------------------------------------------
  # prints the stats that were collected

  def print_stats( self ):
    print "\njit_block_triggers:"
    for addr, hit in self.jit_block_hist.items():
      print "%s: %s" % ( hex( addr ), hit )

    print "\nguard_fail_triggers:"
    for addr, hit in self.guard_fail_hist.items():
      print "%s: %s" % ( hex( addr ), hit )

    print "\nguard_bridge_triggers:"
    for addr, hit in self.guard_bridge_hist.items():
      print "%s: %s" % ( hex( addr ), hit )

    print "\nfun_call_triggers:"
    for addr, hit in self.fun_call_hist.items():
      print "%s: %s" % ( hex( addr ), hit )

    print "\nptr traps:"
    for addr, stat in self.ptr_traps.items():
      print "addr=%s src_ptr: ms=%s sm=%s ch=%s dest_ptr: ms=%s sm=%s ch=%s" \
          % ( hex( addr ),
              stat.num_src_ptr_mem_sts,
              stat.num_src_ptr_same,
              stat.num_src_ptr_changed,
              stat.num_dest_ptr_mem_sts,
              stat.num_dest_ptr_same,
              stat.num_dest_ptr_changed, )


# XXX hacky
class ArmMemory( _WordMemory ):

  def __init__( self, data, size ):
    _WordMemory.__init__( self, data, size )
    self.state = None

  def write( self, start_addr, num_bytes, value ):
    if self.state is not None:
      #self.state.check_ptr_trap_mem_st( start_addr, value )
      # hack use ld trap
      self.state.check_ptr_trap_mem_ld( start_addr, value )
    return _WordMemory.write( self, start_addr, num_bytes, value )

  def read( self, start_addr, num_bytes ):
    # note the hook is _after_ the read
    value = _WordMemory.read( self, start_addr, num_bytes )
    if self.state is not None:
      self.state.check_ptr_trap_mem_ld( start_addr, value )
    return value

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
      # pyxcel related: if this was a jump we store it
      if self.state.pc + 4 != value:
        self.state.prejump_pc = self.state.pc
      self.state.pc = value
      if self.debug.enabled( "rf" ):
        print ':: WR.RF[15] = %s' % ( pad_hex( value ) ),
    else:
      self.regs[idx] = value
      # this is for pyxcel stuff, we trap the written value in the pc
      #self.state.check_ptr_trap_pc_hit( value )
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
