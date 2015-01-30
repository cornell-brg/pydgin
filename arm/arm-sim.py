#=======================================================================
# arm-sim.py
#=======================================================================

import sys
# TODO: figure out a better way to set PYTHONENV
sys.path.append('..')
sys.path.append('/work/bits0/dml257/hg-pypy/pypy')

from pydgin.storage import Memory
from pydgin.misc    import load_program, FatalError
from bootstrap      import syscall_init, memory_size
from instruction    import Instruction
from isa            import decode

from pydgin.debug     import Debug, pad, pad_hex
from rpython.rlib.jit import JitDriver, hint, set_user_param
from machine          import ReturnException

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

  --help,-h       show this message and exit
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

  --max-insts <i> run until the maximum number of instructions
  --jit <flags>   set flags to tune the JIT (see
                  rpython.rlib.jit.PARAMETER_DOCS)

"""

#-----------------------------------------------------------------------
# jit
#-----------------------------------------------------------------------

# for debug printing in PYPYLOG
def get_location( pc ):
  # TODO: add the disassembly of the instruction here as well
  return "pc: %x" % pc

jitdriver = JitDriver( greens =['pc',],
                       reds   =['max_insts','state',],
                       virtualizables  =['state',],
                       get_printable_location=get_location,
                     )

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run( state, max_insts=0 ):
  s = state

  # trigger can enter jit on recursive calls
  jitdriver.can_enter_jit(
    pc        = s.fetch_pc(),
    max_insts = max_insts,
    state     = s,
  )

  while s.status == 0:

    jitdriver.jit_merge_point(
      pc        = s.fetch_pc(),
      max_insts = max_insts,
      state     = s,
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

    # increment ncycles before so that recursion still keeps track of
    # ncycles correctly
    s.ncycles += 1    # TODO: should this be done inside instruction definition?
    if s.stats_en: s.stat_ncycles += 1

    try:
      exec_fun( s, Instruction(inst) )
    except ReturnException as ret_exception:
      if ret_exception.num_levels > 1:
        ret_exception.num_levels -= 1
        raise ret_exception
        #raise ReturnException( ret_exception.num_levels - 1 )

      return
    except FatalError as error:
      # TODO: maybe we can add a command line arg to just give a warning
      # and not terminate execution
      print "Exception in execution, aborting!"
      print "Exception message: %s" % error.msg
      break

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

    # check if we have reached the end of the maximum instructions and
    # exit if necessary
    if max_insts != 0 and s.ncycles >= max_insts:
      print "Reached the max_insts (%d), exiting." % max_insts
      break

    if s.fetch_pc() < old:
      jitdriver.can_enter_jit(
        pc        = s.fetch_pc(),
        max_insts = max_insts,
        state     = s,
      )

  print 'DONE! Status =', s.status
  print 'Instructions Executed =', s.ncycles
  # TODO: temporary -- throw a return execution to end execution
  if len( s.call_stack ) > 0:
    raise ReturnException( len( s.call_stack ) )

#-----------------------------------------------------------------------
# entry_point
#-----------------------------------------------------------------------
def entry_point( argv ):

  filename_idx = 0
  debug_flags = []
  testbin = False
  max_insts = 0

  # we're using a mini state machine to parse the args, and these are two
  # states we have

  ARGS        = 0
  DEBUG_FLAGS = 1
  MAX_INSTS   = 2
  JIT_FLAGS   = 3
  token_type = ARGS

  # go through the args one by one and parse accordingly

  for i in xrange( 1, len( argv ) ):
    token = argv[i]

    if token_type == ARGS:

      if token == "--help" or token == "-h":
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

      elif token == "--max-insts":
        token_type = MAX_INSTS

      elif token == "--jit":
        token_type = JIT_FLAGS

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
    elif token_type == MAX_INSTS:
      max_insts = int( token )
      token_type = ARGS
    elif token_type == JIT_FLAGS:
      # pass the jit flags to rpython.rlib.jit
      set_user_param( jitdriver, token )
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

  # TODO: temporary, add max_insts to state

  state.max_insts = max_insts
  state.run = run

  # Execute the program

  run( state, max_insts )

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
