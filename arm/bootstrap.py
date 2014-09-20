#=======================================================================
# bootstrap.py
#=======================================================================

from machine        import State
#from pydgin.storage import Memory

# Currently these constants are set to match gem5
memory_size = 2**27
page_size   = 8192

# MIPS stack starts at top of kuseg (0x7FFF.FFFF) and grows down
#stack_base = 0x7FFFFFFF
stack_base = memory_size-1   # TODO: set this correctly!

EMULATE_GEM5 = False

#-----------------------------------------------------------------------
# syscall_init
#-----------------------------------------------------------------------
#
# MIPS Memory Map (32-bit):
#
#   0xC000.0000 - Mapped            (kseg2) -   1GB
#   0xA000.0000 - Unmapped uncached (kseg1) - 512MB
#   0x8000.0000 - Unmapped cached   (kseg0) - 512MB
#   0x0000.0000 - 32-bit user space (kuseg) -   2GB
#
def syscall_init( mem, entrypoint, breakpoint, argv, debug ):

  #---------------------------------------------------------------------
  # memory map initialization
  #---------------------------------------------------------------------

  # TODO: for multicore allocate 8MB for each process
  #proc_stack_base[pid] = stack_base - pid * 8 * 1024 * 1024

  # top of heap (breakpoint)  # TODO: handled in load program

  # memory maps: 1GB above top of heap
  # mmap_start = mmap_end = break_point + 0x40000000

  #---------------------------------------------------------------------
  # stack argument initialization
  #---------------------------------------------------------------------
  # http://articles.manugarg.com/aboutelfauxiliaryvectors.html
  #
  #                contents         size
  #
  #   0x7FFF.FFFF  [ end marker ]               4    (NULL)
  #                [ environment str data ]   >=0
  #                [ arguments   str data ]   >=0
  #                [ padding ]               0-16
  #                [ auxv[n]  data ]            8    (AT_NULL Vector)
  #                                             8*x
  #                [ auxv[0]  data ]            8
  #                [ envp[n]  pointer ]         4    (NULL)
  #                                             4*x
  #                [ envp[0]  pointer ]         4
  #                [ argv[n]  pointer ]         4    (NULL)
  #                                             4*x
  #                [ argv[0]  pointer ]         4    (program name)
  #   stack ptr->  [ argc ]                     4    (size of argv)
  #
  #                (stack grows down!!!)
  #
  #   0x7F7F.FFFF  < stack limit for pid 0 >
  #

  # auxv variables initialized by gem5, are these needed?
  #
  # - PAGESZ:    system page size
  # - PHDR:      virtual addr of program header tables
  #              (for statically linked binaries)
  # - PHENT:     size of program header entries in elf file
  # - PHNUM:     number of program headers in elf file
  # - AT_ENRTY:  program entry point
  # - UID:       user ID
  # - EUID:      effective user ID
  # - GID:       group ID
  # - EGID:      effective group ID

  # TODO: handle auxv, envp variables
  auxv = []
  envp = []
  if EMULATE_GEM5:
    argv = argv[1:]
  argc = len( argv )

  def sum_( x ):
    val = 0
    for i in x:
      val += i
    return val

  # calculate sizes of sections
  # TODO: parameterize auxv/envp/argv calc for variable int size?
  stack_nbytes  = [ 4,                              # end mark nbytes (sentry)
                    sum_([len(x)+1 for x in envp]), # envp_str nbytes
                    sum_([len(x)+1 for x in argv]), # argv_str nbytes
                    0,                              # padding  nbytes
                    8*(len(auxv) + 1),              # auxv     nbytes
                    4*(len(envp) + 1),              # envp     nbytes
                    4*(len(argv) + 1),              # argv     nbytes
                    4 ]                             # argc     nbytes

  def round_up( val ):
    alignment = 16
    return (val + alignment - 1) & ~(alignment - 1)

  # calculate padding to align boundary
  # NOTE: MIPs approach (but ignored by gem5)
  #stack_nbytes[3] = 16 - (sum_(stack_nbytes[:3]) % 16)
  # NOTE: gem5 ARM approach
  stack_nbytes[3] = round_up( sum_(stack_nbytes) ) - sum_(stack_nbytes)

  def round_down( val ):
    alignment = 16
    return val & ~(alignment - 1)

  # calculate stack pointer based on size of storage needed for args
  # TODO: round to nearest page size?
  stack_ptr = round_down( stack_base - sum_( stack_nbytes ) )

  if EMULATE_GEM5:
    # FIXME: this offset seems really wrong, but this is how gem5 does it!
    offset  = stack_base
  else:
    offset  = stack_ptr + sum_( stack_nbytes )

  stack_off = []
  for nbytes in stack_nbytes:
    offset -= nbytes
    stack_off.append( offset )
  # FIXME: this is fails for GEM5's hacky offset...
  if not EMULATE_GEM5:
    assert offset == stack_ptr

  if debug.enabled( 'bootstrap' ):
    print 'stack base', hex( stack_base )
    print 'stack min ', hex( stack_ptr )
    print 'stack size', stack_base - stack_ptr
    print
    print 'sentry ', stack_nbytes[0]
    print 'env d  ', stack_nbytes[1]
    print 'arg d  ', stack_nbytes[2]
    print 'padding', stack_nbytes[3]
    print 'auxv   ', stack_nbytes[4]
    print 'envp   ', stack_nbytes[5]
    print 'argv   ', stack_nbytes[6]
    print 'argc   ', stack_nbytes[7]

  # utility functions

  def str_to_mem( mem, val, addr ):
    for i, char in enumerate(val+'\0'):
      mem.write( addr + i, 1, ord( char ) )
    return addr + len(val) + 1

  def int_to_mem( mem, val, addr ):
    # TODO properly handle endianess
    for i in range( 4 ):
      mem.write( addr+i, 1, (val >> 8*i) & 0xFF )
    return addr + 4

  # write end marker to memory
  int_to_mem( mem, 0, stack_off[0] )

  # write environment strings to memory
  envp_ptrs = []
  offset   = stack_off[1]
  for x in envp:
    envp_ptrs.append( offset )
    offset = str_to_mem( mem, x, offset )
  assert offset == stack_off[0]

  # write argument strings to memory
  argv_ptrs = []
  offset   = stack_off[2]
  for x in argv:
    argv_ptrs.append( offset )
    offset = str_to_mem( mem, x, offset )
  assert offset == stack_off[1]

  # write auxv vectors to memory
  offset   = stack_off[4]
  for type_, value in auxv + [(0,0)]:
    offset = int_to_mem( mem, type_, offset )
    offset = int_to_mem( mem, value, offset )
  assert offset == stack_off[3]

  # write envp pointers to memory
  offset   = stack_off[5]
  for env in envp_ptrs + [0]:
    offset = int_to_mem( mem, env, offset )
  assert offset == stack_off[4]

  # write argv pointers to memory
  offset   = stack_off[6]
  for arg in argv_ptrs + [0]:
    offset = int_to_mem( mem, arg, offset )
  assert offset == stack_off[5]

  # write argc to memory
  offset = stack_off[7]
  offset = int_to_mem( mem, argc, offset )
  assert offset == stack_off[6]

  # write zeros to bottom of stack
  # TODO: why does gem5 do this?
  offset = stack_off[7] - 1
  while offset >= stack_ptr:
    mem.write( offset, 1, ord( '\0' ) )
    offset -= 1

  # initialize processor state
  state = State( mem, debug, reset_addr=0x1000 )

  if debug.enabled( 'bootstrap' ):
    print '---'
    #print 'argc = %d (%x)' % ( argc,         stack_off[-1] )
    #for i, ptr in enumerate(argv_ptrs):
    #  print 'argv[%2d] = %x (%x)' % ( i, argv_ptrs[i], stack_off[-2]+4*i ),
    #  print len( argv[i] ), argv[i]
    #print 'argd = %s (%x)' % ( argv[0],      stack_off[-6] )
    print '---'
    print 'envd-base', hex(stack_off[-7])
    print 'argd-base', hex(stack_off[-6])
    print 'auxv-base', hex(stack_off[-4])
    print 'envp-base', hex(stack_off[-3])
    print 'argv-base', hex(stack_off[-2])
    print 'argc-base', hex(stack_off[-1])
    print 'STACK_PTR', hex( stack_ptr )

  # TODO: where should this go?
  state.pc         = entrypoint
  state.breakpoint = breakpoint

  # initialize processor registers
  state.rf[  0 ] = 0            # ptr to func to run when program exits, disable
  state.rf[  1 ] = stack_off[6] # argument 1 reg = argv ptr addr
  state.rf[  2 ] = stack_off[5] # argument 2 reg = envp ptr addr
  state.rf[ 13 ] = stack_ptr    # stack pointer reg
  state.rf[ 15 ] = state.pc + 8 # pc: pointer to two instructions after the
                                # currently executing instruction!

  if debug.enabled( 'bootstrap' ):
    state.rf.print_regs( per_row=4 )
    print '='* 20, 'end bootstrap', '='*20

  return state
