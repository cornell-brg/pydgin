#=======================================================================
# pisa_sim.py
#=======================================================================

import sys
sys.path.append('/Users/dmlockhart/vc/git-brg/parc/pymtl')
sys.path.append('/Users/dmlockhart/vc/hg-opensource/pypy')

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

memory_size = 2**24

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run( state ):
  s = state

  while s.status == 0:

    jitdriver.jit_merge_point(
      pc       = s.pc,
      state    = s,
    )

    old = s.pc

    #print'{:06x}'.format( s.pc ),
    # we use trace elidable iread instead of just read
    inst = s.mem.iread( s.pc, 4 )
    #print '{:08x}'.format( inst ), decode(inst), num_inst
    decode( inst )( s, inst )
    s.ncycles += 1  # TODO: should this be done inside instruction definition?

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

  return mem

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
def syscall_init( mem, argv ):

  #---------------------------------------------------------------------
  # memory map initialization
  #---------------------------------------------------------------------

  # TODO: for multicore allocate 8MB for each process
  #proc_stack_base[pid] = stack_base - pid * 8 * 1024 * 1024

  # top of heap (breakpoint)
  #bss = mem_image.get_sections()[ -1 ]
  #assert bss.name == '.bss'
  #break_point = bss.addr + len(bss.data)

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
  stack_nbytes[3] = 16 - (sum_(stack_nbytes[:3]) % 16)

  # calculate stack pointer based on size of storage needed for args
  # TODO: round to nearest page size?
  stack_ptr = stack_base - sum_( stack_nbytes )
  offset    = stack_base
  stack_off = []
  for nbytes in stack_nbytes:
    offset -= nbytes
    stack_off.append( offset )
  assert offset == stack_ptr

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

  mem = load_program( open( filename, 'rb' ) )


  # Insert bootstrapping code into memory and initialize processor state

  if testbin: state = test_init   ( mem )
  else:       state = syscall_init( mem, argv )

  # Execute the program

  run( state )

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
