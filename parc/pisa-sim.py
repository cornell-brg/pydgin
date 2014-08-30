#=======================================================================
# pisa_sim.py
#=======================================================================

import sys
#sys.path.append('/Users/dmlockhart/vc/git-brg/parc/pymtl')
#sys.path.append('/Users/dmlockhart/vc/hg-opensource/pypy')
sys.path.append('/work/bits0/dml257/pymtl')
sys.path.append('/work/bits0/dml257/hg-pypy/pypy')

import os
import elf

from   isa              import decode, reg_map
from   utils            import State, Memory
from   rpython.rlib.jit import JitDriver

#-----------------------------------------------------------------------
# jit
#-----------------------------------------------------------------------

jitdriver = JitDriver( greens =['pc'],
                       reds   =['state'],
                       virtualizables = ['state']
                     )

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-----------------------------------------------------------------------
# bootstrap code
#-----------------------------------------------------------------------
# TODO: HACKY! We are rewriting the binary here, should really fix the
#       compiler instead!

bootstrap_addr = 0x400
bootstrap_code = [
  0x07, 0x00, 0x1d, 0x3c,   # lui r29, 0x0007
  0xfc, 0xff, 0x1d, 0x34,   # ori r29, r0, 0xfff
  0x00, 0x04, 0x00, 0x08,   # j   0x1000
]

rewrite_addr      = 0x1008
rewrite_code      = [
  0x08, 0x04, 0x00, 0x08,   # j   0x1020
]

# Currently these constants are set to match gem5
memory_size = 2**27
page_size   = 8192

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run( state, debug ):
  s = state

  while s.status == 0:

    jitdriver.jit_merge_point(
      pc       = s.pc,
      state    = s,
    )

    old = s.pc

    if debug: print'{:6x}'.format( s.pc ),
    # we use trace elidable iread instead of just read
    inst = s.mem.iread( s.pc, 4 )
    if debug: print '{:08x} {:8s} {:8d}'.format(inst, decode(inst).func_name[8:], s.ncycles),
    decode( inst )( s, inst )
    s.ncycles += 1  # TODO: should this be done inside instruction definition?
    if s.stats_en: s.stat_ncycles += 1
    if debug: print

    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[ 0: 6] )
    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[ 6:12] )
    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[12:18] )
    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[18:24] )
    #print '0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} 0x{:08x} '.format( *s.rf[24:30] )
    #print '0x{:08x} 0x{:08x} '.format( *s.rf[30:32] )

    if s.pc < old:
      jitdriver.can_enter_jit(
        pc       = s.pc,
        state    = s,
      )

  print 'DONE! Status =', s.status
  print 'Instructions Executed =', s.ncycles

#-----------------------------------------------------------------------
# load_program
#-----------------------------------------------------------------------
def load_program( fp ):
  mem_image = elf.elf_reader( fp )

  sections = mem_image.get_sections()
  mem      = [' ']*memory_size

  for section in sections:
    start_addr = section.addr
    for i, data in enumerate( section.data ):
      mem[start_addr+i] = data

  bss        = sections[-1]
  breakpoint = bss.addr + len( bss.data )
  return mem, breakpoint

#-----------------------------------------------------------------------
# test_init
#-----------------------------------------------------------------------
# initialize simulator state for simple programs, no syscalls
def test_init( mem ):

  # inject bootstrap code into the memory

  for i, data in enumerate( bootstrap_code ):
    mem[ bootstrap_addr + i ] = chr( data )
  for i, data in enumerate( rewrite_code ):
    mem[ rewrite_addr + i ] = chr( data )

  # instantiate architectural state with memory and reset address

  state = State( Memory(mem), None, reset_addr=0x0400 )

  return state

# MIPS stack starts at top of kuseg (0x7FFF.FFFF) and grows down
#stack_base = 0x7FFFFFFF
stack_base = memory_size-1   # TODO: set this correctly!

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
def syscall_init( mem, breakpoint, argv, debug ):

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
  argv = argv[1:]
  argc = len( argv )

  def sum_( x ):
    val = 0
    for i in x:
      val += i
    return val

  # calculate sizes of sections
  # TODO: parameterize auxv/envp/argv calc for variable int size?
  stack_nbytes  = [ 4,                              # end mark nbytes
                    sum_([len(x)+1 for x in envp]), # envp_str nbytes
                    sum_([len(x)+1 for x in argv]), # argv_str nbytes
                    0,                              # padding  nbytes
                    8*(len(auxv) + 1),              # auxv     nbytes
                    4*(len(envp) + 1),              # envp     nbytes
                    4*(len(argv) + 1),              # argv     nbytes
                    4 ]                             # argc     nbytes

  # calculate padding to align boundary
  # TODO: gem5 doesn't do this step, temporarily remove it. There should
  #       really be padding to align argv to a 16 byte boundary!!!
  #stack_nbytes[3] = 16 - (sum_(stack_nbytes[:3]) % 16)

  def round_down( val ):
    return val & ~(page_size - 1)

  # calculate stack pointer based on size of storage needed for args
  # TODO: round to nearest page size?
  stack_ptr = round_down( stack_base - sum_( stack_nbytes ) )
  offset    = stack_ptr + sum_( stack_nbytes )
  stack_off = []
  for nbytes in stack_nbytes:
    offset -= nbytes
    stack_off.append( offset )
  assert offset == stack_ptr

  if debug:
    print 'stack min', hex( stack_ptr )
    print 'stack size', stack_base - stack_ptr

    print 'argv', stack_nbytes[-2]
    print 'envp', stack_nbytes[-3]
    print 'auxv', stack_nbytes[-4]
    print 'argd', stack_nbytes[-6]
    print 'envd', stack_nbytes[-7]

  # utility functions

  def str_to_mem( mem, val, addr ):
    for i, char in enumerate(val+'\0'):
      mem[ addr + i ] = char
    return addr + len(val) + 1

  def int_to_mem( mem, val, addr ):
    # TODO properly handle endianess
    for i in range( 4 ):
      mem[addr+i] = chr((val >> 8*i) & 0xFF)
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

  # initialize processor state
  state = State( Memory(mem), None, reset_addr=0x1000 )

  # TODO: where should this go?
  state.breakpoint = breakpoint

  if debug:
    print '---'
    print 'argc = %d (%x)' % ( argc,         stack_off[-1] )
    for i, ptr in enumerate(argv_ptrs):
      print 'argv[%2d] = %x (%x)' % ( i, argv_ptrs[i], stack_off[-2]+4*i ),
      print len( argv[i] ), argv[i]
    print 'argd = %s (%x)' % ( argv[0],      stack_off[-6] )
    print '---'
    print 'argv-base', hex(stack_off[-2])
    print 'envp-base', hex(stack_off[-3])
    print 'auxv-base', hex(stack_off[-4])
    print 'argd-base', hex(stack_off[-6])
    print 'envd-base', hex(stack_off[-7])

  # initialize processor registers
  state.rf[ reg_map['a0'] ] = argc         # argument 0 reg = argc
  state.rf[ reg_map['a1'] ] = stack_off[6] # argument 1 reg = argv ptr addr
  state.rf[ reg_map['sp'] ] = stack_ptr    # stack pointer reg

  return state

#-----------------------------------------------------------------------
# entry_point
#-----------------------------------------------------------------------
def entry_point( argv ):
  try:
    filename = argv[1]
    testbin  = len(argv) == 3 and argv[2] == '--test'
  except IndexError:
    print "You must supply a filename"
    return 1

  # Load the program into a memory object

  mem, breakpoint = load_program( open( filename, 'rb' ) )

  debug = False

  # Insert bootstrapping code into memory and initialize processor state

  if testbin: state = test_init   ( mem )
  else:       state = syscall_init( mem, breakpoint, argv, debug )
  state.rf .debug = False
  state.mem.debug = debug

  # Execute the program

  run( state, debug )

  return 0

#-----------------------------------------------------------------------
# target
#-----------------------------------------------------------------------
# Enables RPython translation of our interpreter.
def target( *args ):
  return entry_point, None

#-----------------------------------------------------------------------
# main
#-----------------------------------------------------------------------
# Enables CPython simulation of our interpreter.
if __name__ == "__main__":
  entry_point( sys.argv )
