#=======================================================================
# pisa-sim.py
#=======================================================================

import sys

# TODO: figure out a better way to set PYTHONENV
sys.path.append('..')
sys.path.append('/work/bits0/dml257/hg-pypy/pypy')

import os
import elf

from isa   import decode, reg_map
from utils import State, Memory, WordMemory, Debug, \
                  pad, pad_hex

from rpython.rlib.jit import JitDriver, hint

# the help message to display on --help

help_message = """
Pydgin ISA Simulator
usage: %s <args> <sim_exe> <sim_args>

<sim_exe>  the executable to be simulated
<sim_args> arguments to be passed to the simulated executable
<args>     the following optional arguments are supported:

  --help          show this message and exit
  --test          run in testing mode (for running asm tests)
  --debug <flags> enable debug flags in a comma-separated form (e.g.
                  "--debug syscalls,insts"). the following flags are
                  supported:
       insts              cycle-by-cycle instructions
       rf                 register file accesses
       mem                memory accesses
       regdump            register dump
       syscalls           syscall information

"""

#-----------------------------------------------------------------------
# jit
#-----------------------------------------------------------------------

# for debug printing in PYPYLOG
def get_location( pc ):
  # TODO: add the disassembly of the instruction here as well
  return "pc: %x" % pc

jitdriver = JitDriver( greens =['pc'],
                       reds   =['state'],
                       get_printable_location=get_location,
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
memory_size = 2**29
page_size   = 8192

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------

def run( state ):
  s = state

  while s.running:

    jitdriver.jit_merge_point(
      pc       = s.pc,
      state    = s,
    )

    # constant fold the pc
    pc = hint( s.pc, promote=True )
    old = pc

    # We constant fold the s.mem object. This is important because
    # otherwise the trace elidable iread doesn't work (assumes s.mem might
    # have changed)
    mem = hint( s.mem, promote=True )

    if s.debug.enabled( "insts" ):
      print pad( "%x" % s.pc, 6, " ", False ),

    # the print statement in memcheck conflicts with @elidable in iread.
    # So we use normal read if memcheck is enabled which includes the
    # memory checks

    if s.debug.enabled( "memcheck" ):
      inst = mem.read( pc, 4 )
    else:
      # we use trace elidable iread instead of just read
      inst = mem.iread( pc, 4 )

    inst_str, exec_fun = decode( inst )

    if s.debug.enabled( "insts" ):
      print "%s %s %s" % (
              pad_hex( inst ),
              pad( inst_str, 8 ),
              pad( "%d" % s.ncycles, 8 ), ),

    exec_fun( s, inst )

    s.ncycles += 1  # TODO: should this be done inside instruction definition?
    if s.stats_en: s.stat_ncycles += 1

    if s.debug.enabled( "insts" ):
      print
    if s.debug.enabled( "regdump" ):
      s.rf.print_regs()

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
#def load_program( fp, mem ):
def load_program( fp ):
  mem_image = elf.elf_reader( fp )

  sections = mem_image.get_sections()
  # currently word-addressed memory is enabled, uncomment the other to
  # enable byte-addressed memory
  mem      = WordMemory( size=memory_size )
  #mem      = Memory( size=memory_size )

  for section in sections:
    start_addr = section.addr
    for i, data in enumerate( section.data ):
      mem.write( start_addr+i, 1, ord( data ) )

  bss        = sections[-1]
  breakpoint = bss.addr + len( bss.data )
  return mem, breakpoint

#-----------------------------------------------------------------------
# test_init
#-----------------------------------------------------------------------
# initialize simulator state for simple programs, no syscalls
def test_init( mem, debug ):

  # inject bootstrap code into the memory

  for i, data in enumerate( bootstrap_code ):
    mem.write( bootstrap_addr + i, 1, data )
  for i, data in enumerate( rewrite_code ):
    mem.write( rewrite_addr + i, 1, data )

  # instantiate architectural state with memory and reset address

  state = State( mem, None, debug, reset_addr=0x0400 )

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

  #print 'stack min', hex( stack_ptr )
  #print 'stack size', stack_base - stack_ptr

  #print 'argv', stack_nbytes[-2]
  #print 'envp', stack_nbytes[-3]
  #print 'auxv', stack_nbytes[-4]
  #print 'argd', stack_nbytes[-6]
  #print 'envd', stack_nbytes[-7]

  # utility functions

  # TODO: we can do more efficient versions of these using Memory object
  # (writing 4 bytes at once etc.)

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

  # initialize processor state
  state = State( mem, None, debug, reset_addr=0x1000 )

  # TODO: where should this go?
  state.breakpoint = breakpoint

  #print '---'
  #print 'argc = %d (%x)' % ( argc,         stack_off[-1] )
  #for i, ptr in enumerate(argv_ptrs):
  #  print 'argv[%d] = %x (%x)' % ( i, argv_ptrs[i], stack_off[-2]+4*i ),
  #  print len( argv[i] ), argv[i]
  #print 'argd = %s (%x)' % ( argv[0],      stack_off[-6] )
  #print '---'
  #print 'argv-base', hex(stack_off[-2])
  #print 'envp-base', hex(stack_off[-3])
  #print 'auxv-base', hex(stack_off[-4])
  #print 'argd-base', hex(stack_off[-6])
  #print 'envd-base', hex(stack_off[-7])

  # initialize processor registers
  state.rf[ reg_map['a0'] ] = argc         # argument 0 reg = argc
  state.rf[ reg_map['a1'] ] = stack_off[6] # argument 1 reg = argv ptr addr
  state.rf[ reg_map['sp'] ] = stack_ptr    # stack pointer reg

  return state

#-----------------------------------------------------------------------
# entry_point
#-----------------------------------------------------------------------

def entry_point( argv ):

  filename_idx = 0
  debug_flags = []
  testbin = False

  # we're using a mini state machine to parse the args, and these are two
  # states we have

  ARGS        = 0
  DEBUG_FLAGS = 1
  token_type = ARGS

  # go through the args one by one and parse accordingly

  for i in xrange( 1, len( argv ) ):
    token = argv[i]

    if token_type == ARGS:

      if token == "--help":
        print help_message % argv[0]
        return 0

      elif token == "--test":
        testbin = True

      elif token == "--debug":
        token_type = DEBUG_FLAGS
        # warn the user if debugs are not enabled for this translation
        if not Debug.global_enabled:
          print "WARNING: debugs are not enabled for this translation. " + \
                "To allow debugs, translate with --debug option."

      elif token[:2] == "--":
        # unknown option
        print "Unknown argument %s" % token
        return 1

      else:
        # this marks the start of the program name
        filename_idx = i
        break

    elif token_type == DEBUG_FLAGS:
      debug_flags = token.split( "," )
      token_type = ARGS

  if filename_idx == 0:
    print "You must supply a filename"
    return 1

  filename = argv[ filename_idx ]

  # args after program are args to the simulated program

  run_argv = argv[ filename_idx : ]

  # Load the program into a memory object

  mem, breakpoint = load_program( open( filename, 'rb' ) )

  # create a Debug object which contains the debug flags

  debug = Debug()
  debug.set_flags( debug_flags )

  # Insert bootstrapping code into memory and initialize processor state

  if testbin: state = test_init   ( mem, debug )
  else:       state = syscall_init( mem, breakpoint, run_argv, debug )

  # Execute the program

  run( state )

  return 0

#-----------------------------------------------------------------------
# target
#-----------------------------------------------------------------------
# Enables RPython translation of our interpreter.
def target( driver, args ):

  # if --debug flag is provided in translation, we enable debug printing

  if "--debug" in args:
    print "Enabling debugging"
    Debug.global_enabled = True
  else:
    print "Disabling debugging"

  # form a name
  exe_name = "pydgin-parc"
  if driver.config.translation.jit:
    exe_name += "-jit"
  else:
    exe_name += "-nojit"

  if Debug.global_enabled:
    exe_name += "-debug"

  print "Translated binary name:", exe_name
  driver.exe_name = exe_name

  return entry_point, None

#-----------------------------------------------------------------------
# main
#-----------------------------------------------------------------------
# Enables CPython simulation of our interpreter.
if __name__ == "__main__":
  # enable debug flags in interpreted mode
  Debug.global_enabled = True
  entry_point( sys.argv )
