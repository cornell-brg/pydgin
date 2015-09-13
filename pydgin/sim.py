#=======================================================================
# sim.py
#=======================================================================
# This is the common top-level simulator. ISA implementations can use
# various hooks to configure the behavior.

import os
import sys

# ensure we know where the pypy source code is
# XXX: removed the dependency to PYDGIN_PYPY_SRC_DIR because rpython
# libraries are much slower than native python when running on an
# interpreter. So unless the user have added rpython source to their
# PYTHONPATH, we should use native python.
#try:
#  sys.path.append( os.environ['PYDGIN_PYPY_SRC_DIR'] )
#except KeyError as e:
#  print "NOTE: PYDGIN_PYPY_SRC_DIR not defined, using pure python " \
#        "implementation"

from pydgin.debug import Debug, pad, pad_hex
from pydgin.misc  import FatalError
from pydgin.jit   import JitDriver, hint, set_user_param, set_param
from pydgin.storage import _PhysicalByteMemory, _PhysicalWordMemory
from pydgin.cache import AbstractCache, DirectMappedCache, SetAssocCache

EXIT_SYSCALL      = 0
EXCEPTION         = 1
REACHED_MAX_INSTS = 2


def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-------------------------------------------------------------------------
# Sim
#-------------------------------------------------------------------------
# Abstract simulator class

class Sim( object ):

  def __init__( self, arch_name, jit_enabled=False ):

    self.arch_name   = arch_name

    self.jit_enabled = jit_enabled

    if jit_enabled:
      self.jitdriver = JitDriver( greens =['pc',],
                                  reds   = ['max_insts', 'state', 'sim',],
                                  virtualizables  =['state',],
                                  get_printable_location=self.get_location,
                                )

      # Set the default trace limit here. Different ISAs can override this
      # value if necessary
      self.default_trace_limit = 400000

    self.max_insts = 0

  #-----------------------------------------------------------------------
  # decode
  #-----------------------------------------------------------------------
  # This needs to be implemented in the child class

  def decode( self, bits ):
    raise NotImplementedError()

  #-----------------------------------------------------------------------
  # init_state
  #-----------------------------------------------------------------------
  # This needs to be implemented in the child class

  def init_state( self, exe_file, exe_name, run_argv, testbin, mem=None,
                  do_not_load=False ):
    raise NotImplementedError()

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

    --help,-h       Show this message and exit
    --test          Run in testing mode (for running asm tests)
    --env,-e <NAME>=<VALUE>
                    Set an environment variable to be passed to the
                    simulated program. Can use multiple --env flags to set
                    multiple environment variables.
    --debug,-d <flags>[:<start_after>]
                    Enable debug flags in a comma-separated form (e.g.
                    "--debug syscalls,insts"). If provided, debugs starts
                    after <start_after> cycles. The following flags are
                    supported:
         insts              cycle-by-cycle instructions
         rf                 register file accesses
         mem                memory accesses
         regdump            register dump
         syscalls           syscall information
         bootstrap          initial stack and register state

    --max-insts <i> Run until the maximum number of instructions
    --jit <flags>   Set flags to tune the JIT (see
                    rpython.rlib.jit.PARAMETER_DOCS)

  """

  #-----------------------------------------------------------------------
  # get_location
  #-----------------------------------------------------------------------
  # for debug printing in PYPYLOG

  @staticmethod
  def get_location( pc ):
    # TODO: add the disassembly of the instruction here as well
    return "pc: %x" % pc

  #-----------------------------------------------------------------------
  # run
  #-----------------------------------------------------------------------
  def run( self ):
    self = hint( self, promote=True )
    s = self.state

    max_insts = self.max_insts
    jitdriver = self.jitdriver

    # default exit reason: syscall
    # TODO: make this explicit in syscall handling?
    pydgin_status = EXIT_SYSCALL

    while s.running:

      jitdriver.jit_merge_point(
        pc        = s.fetch_pc(),
        max_insts = max_insts,
        state     = s,
        sim       = self,
      )

      # constant-fold pc and mem
      pc  = hint( s.fetch_pc(), promote=True )
      old = pc
      mem = hint( s.mem, promote=True )

      if s.debug.enabled( "insts" ):
        print pad( "%x" % pc, 8, " ", False ),

      # the print statement in memcheck conflicts with @elidable in iread.
      # So we use normal read if memcheck is enabled which includes the
      # memory checks

      if s.debug.enabled( "memcheck" ):
        inst_bits = mem.read( pc, 4 )
      else:
        # we use trace elidable iread instead of just read
        inst_bits, trans_addr = mem.iread( pc, 4 )
        s.mem.icache.mark_transaction( AbstractCache.READ,
                                   trans_addr, 4 )

      try:
        inst, exec_fun = self.decode( inst_bits )

        if s.debug.enabled( "insts" ):
          print "%s %s %s" % (
                  pad_hex( inst_bits ),
                  pad( inst.str, 12 ),
                  pad( "%d" % s.num_insts, 8 ), ),

        exec_fun( s, inst )
      except FatalError as error:
        print "Exception in execution (pc: 0x%s), aborting!" % pad_hex( pc )
        print "Exception message: %s" % error.msg
        pydgin_status = EXCEPTION
        break

      s.num_insts += 1    # TODO: should this be done inside instruction definition?
      if s.stats_en: s.stat_num_insts += 1

      if s.debug.enabled( "insts" ):
        print
      if s.debug.enabled( "regdump" ):
        s.rf.print_regs( per_row=4 )

      # check if we have reached the end of the maximum instructions and
      # exit if necessary
      if max_insts != 0 and s.num_insts >= max_insts and s.running:
        print "Reached the max_insts (%d), exiting." % max_insts
        pydgin_status = REACHED_MAX_INSTS
        break

      if s.fetch_pc() < old:
        jitdriver.can_enter_jit(
          pc        = s.fetch_pc(),
          max_insts = max_insts,
          state     = s,
          sim       = self,
        )

    # do a cache dump here
    print "dcache dump"
    s.mem.dcache.dump()
    print "icache dump"
    s.mem.icache.dump()
    print 'DONE! Status =', s.status
    print 'Instructions Executed =', s.num_insts
    return pydgin_status, s.status

  #-----------------------------------------------------------------------
  # get_entry_point
  #-----------------------------------------------------------------------
  # generates and returns the entry_point function used to start the
  # simulator

  def get_entry_point( self ):
    def entry_point( argv ):

      # set the trace_limit parameter of the jitdriver
      if self.jit_enabled:
        set_param( self.jitdriver, "trace_limit", self.default_trace_limit )

      filename_idx       = 0
      debug_flags        = []
      debug_starts_after = 0
      testbin            = False
      max_insts          = 0
      envp               = []

      # we're using a mini state machine to parse the args

      prev_token = ""

      # list of tokens that require an additional arg

      tokens_with_args = [ "-h", "--help",
                           "-e", "--env",
                           "-d", "--debug",
                           "--max-insts",
                           "--jit",
                         ]

      # go through the args one by one and parse accordingly

      for i in xrange( 1, len( argv ) ):
        token = argv[i]

        if prev_token == "":

          if token == "--help" or token == "-h":
            print self.help_message % ( self.arch_name, argv[0] )
            return 0

          elif token == "--test":
            testbin = True

          elif token == "--debug" or token == "-d":
            prev_token = token
            # warn the user if debugs are not enabled for this translation
            if not Debug.global_enabled:
              print "WARNING: debugs are not enabled for this translation. " + \
                    "To allow debugs, translate with --debug option."

          elif token in tokens_with_args:
            prev_token = token

          elif token[:1] == "-":
            # unknown option
            print "Unknown argument %s" % token
            return 1

          else:
            # this marks the start of the program name
            filename_idx = i
            break

        else:
          if prev_token == "--env" or prev_token == "-e":
            envp.append( token )

          elif prev_token == "--debug" or prev_token == "-d":
            # if debug start after provided (using a colon), parse it
            debug_tokens = token.split( ":" )
            if len( debug_tokens ) > 1:
              debug_starts_after = int( debug_tokens[1] )

            debug_flags = debug_tokens[0].split( "," )

          elif prev_token == "--max-insts":
            self.max_insts = int( token )

          elif prev_token == "--jit":
            # pass the jit flags to rpython.rlib.jit
            set_user_param( self.jitdriver, token )

          prev_token = ""

      if filename_idx == 0:
        print "You must supply a filename"
        return 1

      # create a Debug object which contains the debug flags

      self.debug = Debug( debug_flags, debug_starts_after )

      filename = argv[ filename_idx ]

      # args after program are args to the simulated program

      run_argv = argv[ filename_idx : ]

      # Open the executable for reading

      try:
        exe_file = open( filename, 'rb' )

      except IOError:
        print "Could not open file %s" % filename
        return 1

      # Call ISA-dependent init_state to load program, initialize memory
      # etc.

      self.init_state( exe_file, filename, run_argv, envp, testbin )

      # pass the state to debug for cycle-triggered debugging

      self.debug.set_state( self.state )

      # cache initialization

      # 16K, 4-word/cache line
      icache = DirectMappedCache( 16384, 16, "icache", self.debug )
      dcache = DirectMappedCache( 16384, 16, "dcache", self.debug )
      self.state.mem.set_caches( icache, dcache ), DirectMappedCache

      # Close after loading

      exe_file.close()

      # Execute the program

      self.run()

      return 0

    try:
      #-----------------------------------------------------------------
      # pydgin_init_elf
      #-----------------------------------------------------------------
      # this is the api to initialize pydgin using the dynamic library

      from rpython.rtyper.lltypesystem import rffi, lltype
      from rpython.rlib.entrypoint import entrypoint, RPython_StartupCode

      @entrypoint( "main",
                   [rffi.CCHARP, rffi.INT, rffi.CCHARPP, rffi.CCHARPP,
                    rffi.CCHARPP, rffi.CCHARP, rffi.INT],
                   c_name="pydgin_init_elf" )
      def pydgin_init_elf( ll_filename, ll_argc, ll_argv, ll_envp,
                           ll_debug_flags, ll_pmem, ll_do_not_load ):

        # TODO: this seems the be necessary to acquire the GIL. not sure if
        # we need it here?
        #after = rffi.aroundstate.after
        #if after: after()

        print "pydgin_init_elf"

        # convert low-level filename to string

        if ll_filename:
          filename = rffi.charp2str( ll_filename )
        else:
          print "ll_filename cannot be null"
          return rffi.cast( rffi.INT, -1 )

        # convert args

        argc = rffi.cast( lltype.Signed, ll_argc )
        run_argv = []

        if ll_argv:
          for i in range( argc ):
            run_argv.append( rffi.charp2str( ll_argv[i] ) )

        # convert environment variables

        envp = []

        if ll_envp:
          i = 0
          while ll_envp[i]:
            envp.append( rffi.charp2str( ll_envp[i] ) )
            i += 1

        # convert debug flags

        debug_flags = []

        if ll_debug_flags:
          i = 0
          while ll_debug_flags[i]:
            debug_flags.append( rffi.charp2str( ll_debug_flags[i] ) )
            i += 1


        debug_starts_after = 0
        testbin            = False

        # create a Debug object which contains the debug flags

        self.debug = Debug( debug_flags, debug_starts_after )

        # Open the executable for reading

        try:
          exe_file = open( filename, 'rb' )

        except IOError:
          print "Could not open file %s" % filename
          return rffi.cast( rffi.INT, -1 )

        # if we are provided with a physical mem, pass this to init_state
        # initialize memory

        mem = None
        if ll_pmem:
          print "using physical memory provided"

          # TODO: initialize this elsewhere
          #mem = _PhysicalByteMemory( ll_pmem, size=2**10,
          #                           page_table={} )
          pmem = rffi.cast( rffi.UINTP, ll_pmem )
          mem = _PhysicalWordMemory( pmem, size=2**10,
                                     page_table={} )

        if rffi.cast( lltype.Signed, ll_do_not_load ) != 0:
          print "Pydgin will not load the program"
          do_not_load = True
        else:
          print "Pydgin will load the program"
          do_not_load = False

        # Call ISA-dependent init_state to load program, initialize memory
        # etc.
        self.init_state( exe_file, filename, run_argv, envp, testbin,
                         mem=mem, do_not_load=do_not_load )

        # pass the state to debug for cycle-triggered debugging

        self.debug.set_state( self.state )

        # cache initialization
        # TODO: pass the parameters through the interface

        # 16K, 4-word/cache line
        #icache = DirectMappedCache( 16384, 16, "icache", self.debug,
        #                            stats_en=True, dirty_en=False )
        #dcache = DirectMappedCache( 16384, 16, "dcache", self.debug,
        #                            stats_en=True, dirty_en=True )
        #icache = DirectMappedCache( 16384, 16, "icache", self.debug,
        #                            stats_en=False, dirty_en=False )
        #dcache = DirectMappedCache( 16384, 16, "dcache", self.debug,
        #                            stats_en=False, dirty_en=False )
        #icache = SetAssocCache( 16384, 16, "icache", self.debug,
        #                            self.state, num_ways=2,
        #                            stats_en=True, dirty_en=False )
        #dcache = SetAssocCache( 16384, 16, "dcache", self.debug,
        #                            self.state, num_ways=2,
        #                            stats_en=True, dirty_en=True )
        icache = SetAssocCache( 16384, 16, "icache", self.debug,
                                    self.state, num_ways=2,
                                    stats_en=False, dirty_en=False )
        dcache = SetAssocCache( 16384, 16, "dcache", self.debug,
                                    self.state, num_ways=2,
                                    stats_en=False, dirty_en=False )
        self.state.mem.set_caches( icache, dcache ), DirectMappedCache

        # Close after loading

        exe_file.close()

        # return success
        return rffi.cast( rffi.INT, 0 )

      #-----------------------------------------------------------------
      # CReturn
      #-----------------------------------------------------------------
      # c representation of the return type
      CReturn = lltype.Struct( "PydginReturn",
                               ( "pydgin_status", rffi.INT ),
                               ( "prog_status",   rffi.INT ),
                             )

      #-----------------------------------------------------------------
      # pydgin_simulate
      #-----------------------------------------------------------------
      @entrypoint( "main", [lltype.Ptr( CReturn )], c_name="pydgin_simulate" )
      def pydgin_simulate( ll_return ):
        # remove the max instruction limit

        self.max_insts = 0

        # Execute the program

        pydgin_status, prog_status = self.run()

        # set return variables

        ll_return.pydgin_status = rffi.cast( rffi.INT, pydgin_status )
        ll_return.prog_status   = rffi.cast( rffi.INT, prog_status )

      #-----------------------------------------------------------------
      # pydgin_simulate_num_insts
      #-----------------------------------------------------------------
      @entrypoint( "main", [rffi.LONGLONG, lltype.Ptr( CReturn )],
                   c_name="pydgin_simulate_num_insts" )
      def pydgin_simulate_num_insts( ll_num_insts, ll_return ):

        # get number of instructions

        num_insts = rffi.cast( lltype.SignedLongLong, ll_num_insts )

        # add the requested number of instructions to the current number

        self.max_insts = self.state.num_insts + num_insts

        print "simulate for %s instructions" % num_insts

        # Execute the program

        pydgin_status, prog_status = self.run()

        # set return variables

        ll_return.pydgin_status = rffi.cast( rffi.INT, pydgin_status )
        ll_return.prog_status   = rffi.cast( rffi.INT, prog_status )

      #-----------------------------------------------------------------
      # CArmArchState
      #-----------------------------------------------------------------
      # c representation of arm architectural state
      CArmArchState = lltype.Struct( "PydginArmArchState",
                                    ( "rf",   rffi.CFixedArray(
                                                        rffi.UINT, 16 ) ),
                                    ( "pc",   rffi.UINT ),
                                    ( "cpsr", rffi.UINT ),
                                    ( "brk_point", rffi.UINT ),
                                   )

      #-----------------------------------------------------------------
      # pydgin_get_arch_state
      #-----------------------------------------------------------------
      @entrypoint( "main", [lltype.Ptr( CArmArchState )],
                   c_name="pydgin_get_arch_state" )
      def pydgin_get_arch_state( ll_state ):
        print "pydgin_get_arch_state"

        ll_state.pc   = rffi.cast( rffi.UINT, self.state.pc     )
        ll_state.cpsr = rffi.cast( rffi.UINT, self.state.cpsr() )
        ll_state.brk_point = rffi.cast( rffi.UINT, self.state.breakpoint )

        for i in range( 16 ):
          ll_state.rf[i] = rffi.cast( rffi.UINT, self.state.rf[i] )

        print_c_arch_state( ll_state )

      #-----------------------------------------------------------------
      # pydgin_set_arch_state
      #-----------------------------------------------------------------
      @entrypoint( "main", [lltype.Ptr( CArmArchState )],
                   c_name="pydgin_set_arch_state" )
      def pydgin_set_arch_state( ll_state ):
        print "pydgin_set_arch_state"

        print_c_arch_state( ll_state )

        self.state.pc   = rffi.cast( lltype.Signed, ll_state.pc )
        self.state.set_cpsr( rffi.cast( lltype.Signed, ll_state.cpsr ) )
        self.state.breakpoint = rffi.cast( lltype.Signed, ll_state.brk_point )

        # hack: don't set r15 because it messes up the pc
        for i in range( 15 ):
          self.state.rf[i] = rffi.cast( lltype.Signed, ll_state.rf[i] )

      #-----------------------------------------------------------------
      # pydgin_set_ptable
      #-----------------------------------------------------------------
      @entrypoint( "main", [rffi.INTP, rffi.INT],
                   c_name="pydgin_set_ptable" )
      def pydgin_set_ptable( ll_ptable, ll_ptable_nentries ):
        print "setting page table"
        # the low-level page table is encoded to be an array of
        # tuples, first the virtual memory page index then physical
        # memory base address

        # to implement differential page, table, first get the old one,
        # and append the new stuff to it
        mem = self.state.mem
        ptable = mem.page_table
        for i in range( ll_ptable_nentries ):
          v1 = rffi.cast( lltype.Signed, ll_ptable[2*i] )
          v2 = rffi.cast( lltype.Signed, ll_ptable[2*i+1] )
          print "ll_ptable[%d] = %x, %x" % (i, v1, v2)
          # TODO: temporarily disabled
          #ptable[ v1 ] = v2
        # TODO: temporarily disabled
        #mem.set_page_table( ptable )

      #-----------------------------------------------------------------
      # pydgin_get_ptable
      #-----------------------------------------------------------------
      @entrypoint( "main", [rffi.INTP],
                   c_name="pydgin_get_ptable" )
      def pydgin_get_ptable( ll_ptable ):
        print "getting page table"
        # the low-level page table is encoded to be an array of
        # tuples, first the virtual memory page index then physical
        # memory base address
        mem = self.state.mem
        i = 0
        # use the differential page table and reset one transferred
        for vaddr_idx, paddr_base in mem.diff_page_table.items():
          ll_ptable[2*i]   = rffi.cast( rffi.INT, vaddr_idx  )
          ll_ptable[2*i+1] = rffi.cast( rffi.INT, paddr_base )
          print "ll_ptable[%d] = %x, %x" % (i, vaddr_idx, paddr_base)
          i += 1

        mem.diff_page_table = {}

        return i

      #-----------------------------------------------------------------
      # print_c_arch_state
      #-----------------------------------------------------------------
      def print_c_arch_state( ll_state ):
        pc = rffi.cast( lltype.Signed, ll_state.pc )
        print "pc: %x" % pc
        cpsr = rffi.cast( lltype.Signed, ll_state.cpsr )
        print "cpsr: %x" % cpsr

        for i in range( 16 ):
          reg = rffi.cast( lltype.Signed, ll_state.rf[i] )
          print "reg%d: %x" % ( i, reg )

    except ImportError:
      pass

    return entry_point

  #-----------------------------------------------------------------------
  # target
  #-----------------------------------------------------------------------
  # Enables RPython translation of our interpreter.

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

    # allow shared compilation
    if "--shared" in args:
      print "Enabling shared library compilation"
      driver.config.translation.suggest( shared=True )

    # NOTE: RPython has an assertion to check the type of entry_point to
    # be function (not a bound method). So we use get_entry_point which
    # generates a function type
    entry_point = self.get_entry_point()
    return entry_point, None

#-------------------------------------------------------------------------
# init_sim
#-------------------------------------------------------------------------
# Simulator implementations need to call this function at the top level.
# This takes care of adding target function to top level environment and
# running the simulation in interpreted mode if directly called
# ( __name__ == "__main__" )

def init_sim( sim ):

  # this is a bit hacky: we get the global variables of the caller from
  # the stack frame to determine if this is being run top level and add
  # target function required by rpython toolchain

  caller_globals = sys._getframe(1).f_globals
  caller_name    = caller_globals[ "__name__" ]

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

