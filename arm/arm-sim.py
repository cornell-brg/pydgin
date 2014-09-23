#=======================================================================
# arm-sim.py
#=======================================================================

import sys
# TODO: figure out a better way to set PYTHONENV
sys.path.append('..')
sys.path.append('/work/bits0/dml257/hg-pypy/pypy')

from pydgin.storage import Memory
from pydgin.misc    import load_program
from bootstrap      import syscall_init, memory_size
from isa            import decode

from pydgin.debug     import Debug, pad, pad_hex
from rpython.rlib.jit import JitDriver, hint

#-----------------------------------------------------------------------
# help message
#-----------------------------------------------------------------------
# the help message to display on --help

help_message = """
Pydgin PARC Instruction Set Simulator
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
       bootstrap          initial stack and register state

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
# run
#-----------------------------------------------------------------------
def run( state ):
  s = state

  while s.status == 0:

    jitdriver.jit_merge_point(
      pc       = s.fetch_pc(),
      state    = s,
    )

    # constant-fold pc and mem
    pc  = hint( s.fetch_pc(), promote=True )
    old = pc
    mem = hint( s.mem, promote=True )

    if s.debug.enabled( "insts" ):
      print pad( "%x" % pc, 6, " ", False ),

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

    s.ncycles += 1    # TODO: should this be done inside instruction definition?
    if s.stats_en: s.stat_ncycles += 1

    if s.debug.enabled( "insts" ):
      print
    if s.debug.enabled( "regdump" ):
      s.rf.print_regs( per_row=4 )
      print '%s%s%s%s' % (
        'N' if s.N else '-',
        'Z' if s.Z else '-',
        'C' if s.C else '-',
        'V' if s.V else '-'
      )

    if s.fetch_pc() < old:
      jitdriver.can_enter_jit(
        pc       = s.fetch_pc(),
        state    = s,
      )

  print 'DONE! Status =', s.status
  print 'Instructions Executed =', s.ncycles

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

  mem = Memory( size=memory_size, byte_storage=False )
  entrypoint, breakpoint = load_program(
      open( filename, 'rb' ), mem,
      # TODO: GEM5 uses this alignment, remove?
      alignment = 1<<12
  )

  # create a Debug object which contains the debug flags

  debug = Debug()
  debug.set_flags( debug_flags )

  # Insert bootstrapping code into memory and initialize processor state

  state = syscall_init( mem, entrypoint, breakpoint, run_argv, debug )

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
  exe_name = "pydgin-arm"
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
