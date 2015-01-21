#=======================================================================
# sim.py
#=======================================================================
# This is the common top-level simulator. ISA implementations can use
# various hooks to configure the behavior.

import sys
# TODO: figure out a better way to set PYTHONENV
#sys.path.append('..')
sys.path.append('/work/bits0/dml257/hg-pypy/pypy')

#from pydgin.storage import Memory
#from pydgin.misc    import load_program
#from bootstrap      import syscall_init, memory_size
#from instruction    import Instruction
#from isa            import decode

from pydgin.debug     import Debug, pad, pad_hex
from rpython.rlib.jit import JitDriver, hint

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-------------------------------------------------------------------------
# Sim
#-------------------------------------------------------------------------

class Sim( object ):

  #-----------------------------------------------------------------------
  # help message
  #-----------------------------------------------------------------------
  # the help message to display on --help

  help_message = """
  Pydgin %s Instruction Set Simulator
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

    --max-insts <i> run until the maximum number of instructions

  """

  #-----------------------------------------------------------------------
  # jit
  #-----------------------------------------------------------------------

  # for debug printing in PYPYLOG
  @staticmethod
  def get_location( pc ):
    # TODO: add the disassembly of the instruction here as well
    return "pc: %x" % pc

  def __init__( self, arch_name, jit_enabled=False ):

    self.arch_name   = arch_name

    self.jit_enabled = jit_enabled

    if jit_enabled:
      self.jitdriver = JitDriver( greens =['pc',],
                             reds   =['max_insts','state',],
                             virtualizables  =['state',],
                             get_printable_location=self.get_location,
                           )

    self.max_insts = 0

  #-----------------------------------------------------------------------
  # run
  #-----------------------------------------------------------------------
  def run( self ): #, state, max_insts=0 ):
    s = self.state

    max_insts = self.max_insts
    jitdriver = self.jitdriver

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
        inst_bits = mem.read( pc, 4 )
      else:
        # we use trace elidable iread instead of just read
        inst_bits = mem.iread( pc, 4 )

      #inst_str, exec_fun = decode( inst )
      inst, exec_fun = self.decode( inst_bits )

      if s.debug.enabled( "insts" ):
        print "%s %s" % ( inst, pad( "%d" % s.ncycles, 8 ), )
        #print "%s %s %s" % (
        #        pad_hex( inst ),
        #        pad( inst.str, 8 ),
        #        pad( "%d" % s.ncycles, 8 ), ),

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

  #-----------------------------------------------------------------------
  # get_entry_point
  #-----------------------------------------------------------------------
  # generates and returns the entry_point function used to start the
  # simulator

  def get_entry_point( self ):
    def entry_point( argv ):

      filename_idx = 0
      debug_flags = []
      testbin = False
      max_insts = 0

      # we're using a mini state machine to parse the args, and these are
      # three states we have

      ARGS        = 0
      DEBUG_FLAGS = 1
      MAX_INSTS   = 2
      token_type = ARGS

      # go through the args one by one and parse accordingly

      for i in xrange( 1, len( argv ) ):
        token = argv[i]

        if token_type == ARGS:

          if token == "--help":
            print self.help_message % ( self.arch_name, argv[0] )
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

      if filename_idx == 0:
        print "You must supply a filename"
        return 1

      # create a Debug object which contains the debug flags

      self.debug = Debug()
      self.debug.set_flags( debug_flags )

      filename = argv[ filename_idx ]

      # args after program are args to the simulated program

      run_argv = argv[ filename_idx : ]

      # Load the program into a memory object

      #mem = Memory( size=memory_size, byte_storage=False )
      #entrypoint, breakpoint = load_program(
      #    open( filename, 'rb' ), mem,
      #    # TODO: GEM5 uses this alignment, remove?
      #    alignment = 1<<12
      #)


      # Insert bootstrapping code into memory and initialize processor state

      #state = syscall_init( mem, entrypoint, breakpoint, run_argv, debug )

      # Open the executable for reading

      try:
        exe_file = open( filename, 'rb' )

      except IOError:
        print "Could not open file %s" % filename
        return 1

      # Call ISA-dependent init_state to load program, initialize memory
      # etc.

      self.init_state( exe_file, run_argv )

      # Close after loading

      exe_file.close()

      # Execute the program

      self.run()
      #run( state, max_insts )

      return 0

    return entry_point

  #-----------------------------------------------------------------------
  # target
  #-----------------------------------------------------------------------
  # Enables RPython translation of our interpreter.
  #def get_target( self ):
  def target( self, driver, args ):

    # if --debug flag is provided in translation, we enable debug printing

    if "--debug" in args:
      print "Enabling debugging"
      Debug.global_enabled = True
    else:
      print "Disabling debugging"

    # form a name
    exe_name = "pydgin-%s" % self.arch_name.lower()
    if driver.config.translation.jit:
      exe_name += "-jit"
    else:
      exe_name += "-nojit"

    if Debug.global_enabled:
      exe_name += "-debug"

    print "Translated binary name:", exe_name
    driver.exe_name = exe_name

    # NOTE: RPython has an assertion to check the type of entry_point to
    # be function (not a bound method). So we use get_entry_point which
    # generates a function type
    #return self.entry_point, None
    return self.get_entry_point(), None

#-------------------------------------------------------------------------
# init_sim
#-------------------------------------------------------------------------

def init_sim( sim ):

  # this is a bit hacky: we get the global variables of the caller from
  # the stack frame to determine if this is being run top level and add
  # target function required by rpython toolchain

  print "__name__:", __name__
  print "globals", globals()

  caller_globals = sys._getframe(1).f_globals
  caller_name    = caller_globals[ "__name__" ]

  print "caller __name__:", caller_name

  # add target function to top level

  caller_globals[ "target" ] = sim.target

  #-----------------------------------------------------------------------
  # main
  #-----------------------------------------------------------------------
  # Enables CPython simulation of our interpreter.
  if caller_name == "__main__":
    # enable debug flags in interpreted mode
    Debug.global_enabled = True
    sim.get_entry_point()( sys.argv )

