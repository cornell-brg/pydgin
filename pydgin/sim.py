#=======================================================================
# sim.py
#=======================================================================
# This is the common top-level simulator. ISA implementations can use
# various hooks to configure the behavior.

import os
import sys
import pickle
import csv

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
from pydgin.jit   import JitDriver, hint, set_user_param, set_param, \
                         elidable

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-------------------------------------------------------------------------
# ReconvergenceManager
#-------------------------------------------------------------------------

class ReconvergenceManager():

  def __init__( s ):
    s.top_priority = 0
    s.switch_interval = 0

  def set_state( s, active_cores ):
    s.switch_interval = active_cores
    s.top_priority = 0

  #-----------------------------------------------------------------------
  # advance_pcs
  #-----------------------------------------------------------------------

  def advance_pcs( s, sim ):

    #---------------------------------------------------------------------
    # No reconvergence
    #---------------------------------------------------------------------

    if sim.reconvergence == 0:
      pc_list = []
      for i in range( sim.active_cores ):
        if sim.states[i].parallel_mode:
          if sim.states[i].pc not in pc_list and sim.states[i].active:
            pc_list.append( sim.states[i].pc )
          if sim.states[i].active:
            sim.total_insts += 1
      sim.unique_insts += len( pc_list )

    #---------------------------------------------------------------------
    # Round-Robin + Min-PC hybrid reconvergence
    #---------------------------------------------------------------------

    elif sim.reconvergence == 1:

      min_pc = sys.maxint

      # Select the minimum-pc
      if s.switch_interval == 0:
        for i in range( sim.active_cores ):
          if sim.states[i].pc < min_pc:
            min_pc = sim.states[i].pc
        #print "Selecting MIN-PC"
        s.switch_interval = sim.active_cores + 1
      # Round-robin arbitration
      else:
        #print "Selecting by being FAIR", s.top_priority
        min_pc = sim.states[s.top_priority].pc
        s.top_priority = 0 if s.top_priority == sim.active_cores-1 else s.top_priority+1

      #pc_list = []
      #for i in range( sim.active_cores ):
      #  pc_list.append( sim.states[i].pc )
      #print "[",
      #for x in pc_list:
      #  print hex(x), ",",
      #print "] min_pc: ", hex(min_pc)

      for i in range( sim.active_cores ):
        # advance pcs that match the min-pc and make sure to not activate
        # cores that have reached the barrier
        if sim.states[i].pc == min_pc and not sim.states[i].stop:
          sim.states[i].active = True
          sim.total_insts += 1
        else:
          sim.states[i].active = False

      sim.unique_insts += 1
      s.switch_interval -= 1

#-------------------------------------------------------------------------
# Sim
#-------------------------------------------------------------------------
# Abstract simulator class

class Sim( object ):

  def __init__( self, arch_name, jit_enabled=False ):

    self.arch_name   = arch_name

    self.jit_enabled = jit_enabled

    if jit_enabled:
      self.jitdriver = JitDriver( greens =['pc', 'core_id'],
                                  reds   = ['tick_ctr', 'max_insts', 'state', 'sim',],
                                  #virtualizables  =['state',],
                                  get_printable_location=self.get_location,
                                )

      # Set the default trace limit here. Different ISAs can override this
      # value if necessary
      self.default_trace_limit = 400000

    self.max_insts = 0

    self.ncores = 1
    self.core_switch_ival = 1
    self.pkernel_bin = None

    # shreesha: adding extra stuff here
    self.barrier_count = 0
    self.active_cores = 0
    self.linetrace = False
    self.analysis = False
    self.reconvergence = 0
    self.unique_insts = 0
    self.total_insts = 0
    self.total_steps = 0
    self.reconvergence_manager = ReconvergenceManager()

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

  def init_state( self, exe_file, exe_name, run_argv, testbin ):
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
    --ncores <i>    Number of cores to simulate
    --core-switch-ival <i>
                    Switch cores at this interval
    --pkernel <f>   Load pkernel binary
    --jit <flags>   Set flags to tune the JIT (see
                    rpython.rlib.jit.PARAMETER_DOCS)
    --linetrace     Turn on linetrace for parallel mode
    --analysis      Use the options below
        0 No reconvergence
        1 Min-pc, opportunistic
    --runtime-md    Runtime metadata used in analysis
  """

  #-----------------------------------------------------------------------
  # get_location
  #-----------------------------------------------------------------------
  # for debug printing in PYPYLOG

  @staticmethod
  def get_location( pc, core_id ):
    # TODO: add the disassembly of the instruction here as well
    return "pc: %x core_id: %x" % ( pc, core_id )

  @elidable
  def next_core_id( self, core_id ):
    return ( core_id + 1 ) % self.ncores

  #-----------------------------------------------------------------------
  # run
  #-----------------------------------------------------------------------
  def run( self ):
    self = hint( self, promote=True )

    #s = self.state

    max_insts = self.max_insts
    jitdriver = self.jitdriver

    core_id = 0
    tick_ctr = 0

    # use proc 0 to determine if should be running
    while self.states[0].running:

      # NOTE: Fix this assertion to be more useful
      active = False
      for i in xrange( self.ncores ):
        if not self.states[i].stop:
          active |= self.states[i].active
        else:
          active |= True
      if not active:
        print "Something wrong no cores are active!"
        raise AssertionError

      for core_id in xrange( self.ncores ):
        s = self.states[ core_id ]

        if s.active:
          pc = s.fetch_pc()
          mem = s.mem

          if s.debug.enabled( "insts" ):
            print pad( "%x" % pc, 8, " ", False ),

          # fetch
          inst_bits = mem.iread( pc, 4 )

          try:
            inst, exec_fun = self.decode( inst_bits )

            if s.debug.enabled( "insts" ):
              print "c%s %s %s %s" % (
                      core_id,
                      pad_hex( inst_bits ),
                      pad( inst.str, 12 ),
                      pad( "%d" % s.num_insts, 8 ), ),

            exec_fun( s, inst )

          except FatalError as error:
            print "Exception in execution (pc: 0x%s), aborting!" % pad_hex( pc )
            print "Exception message: %s" % error.msg
            break

          s.num_insts += 1
          if s.stats_en: s.stat_num_insts += 1

          # shreesha: collect instrs in serial region if stats has been enabled
          if s.stats_en and ( not s.parallel_mode ): s.serial_insts += 1
          if s.parallel_mode and s.runtime_mode: s.runtime_insts += 1

          if s.debug.enabled( "insts" ):
            print
          if s.debug.enabled( "regdump" ):
            s.rf.print_regs( per_row=4 )

          # check if we have reached the end of the maximum instructions and
          # exit if necessary
          if max_insts != 0 and s.num_insts >= max_insts:
            print "Reached the max_insts (%d), exiting." % max_insts
            break

      # count steps in stats region
      if self.states[0].stats_en: self.total_steps += 1

      # shreesha: reconvergence
      self.reconvergence_manager.advance_pcs( self )

      # check if the count of the barrier is equal to the number of active
      # cores, reset the hardware barrier
      if self.barrier_count == self.active_cores:
        for i in xrange( self.active_cores ):
          if not self.states[i].active:
            self.states[i].active = True

      # shreesha: linetrace
      if self.linetrace:
        parallel_mode = False
        for i in range( self.active_cores ):
          parallel_mode |= self.states[i].parallel_mode

        if parallel_mode:
          for i in range( self.ncores ):
            #print pad( "%x %d |" % ( self.states[i].pc, self.states[i].active ), 8, " ", False ),
            if self.states[i].active and self.states[i].parallel_mode:
              print pad( "%x |" % self.states[i].pc, 8, " ", False ),
            else:
              print pad( " |" % self.states[i].pc, 8, " ", False ),
          print

    print '\nDONE! Status =', self.states[0].status
    print 'Total Ticks Simulated = %d' % tick_ctr
    print 'Unique Insts in parallel regions = %d' % self.unique_insts
    print 'Total Insts in parallel regions = %d' % self.total_insts
    print 'Total steps in stats region = %d' % self.total_steps
    redundant_insts = ( self.total_insts - self.unique_insts )
    print 'Redundant Insts in parallel regions = %d' % redundant_insts
    if self.total_insts:
      print 'Potential savings in parallel regions = %f' % ( 100*redundant_insts / float( self.total_insts ) )

    # show all stats
    for i, state in enumerate( self.states ):
      print 'Core %d Instructions Executed = %d' % ( i, state.num_insts )

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
      core_type          = 0
      stats_core_type    = 0
      accel_rf           = False
      # shreesha: runtime metadata
      runtime_md         = None

      # we're using a mini state machine to parse the args

      prev_token = ""

      # list of tokens that require an additional arg

      tokens_with_args = [ "-h", "--help",
                           "-e", "--env",
                           "-d", "--debug",
                           "--max-insts",
                           "--jit",
                           "--ncores",
                           "--core-switch-ival",
                           "--pkernel",
                           "--core-type",
                           "--stats-core-type",
                           "--linetrace",
                           "--analysis",
                           "--runtime-md",
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

          elif token == "--accel-rf":
            accel_rf = True

          elif token == "--debug" or token == "-d":
            prev_token = token
            # warn the user if debugs are not enabled for this translation
            if not Debug.global_enabled:
              print "WARNING: debugs are not enabled for this translation. " + \
                    "To allow debugs, translate with --debug option."

          elif token == "--linetrace":
            self.linetrace = True

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

          elif prev_token == "--ncores":
            self.ncores = int( token )
            self.active_cores = self.ncores
            self.reconvergence_manager.set_state( self.ncores )

          elif prev_token == "--core-switch-ival":
            self.core_switch_ival = int( token )

          elif prev_token == "--pkernel":
            self.pkernel_bin = token

          elif prev_token == "--core-type":
            core_type = int( token )

          elif prev_token == "--stats-core-type":
            stats_core_type = int( token )

          elif prev_token == "--analysis":
            self.analysis = True
            self.reconvergence = int( token )

          elif prev_token == "--runtime-md":
            runtime_md = token

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

      # set the core type and stats core type

      for i in range( self.ncores ):
        self.states[i].core_type = core_type
        self.states[i].stats_core_type = stats_core_type
        self.states[i].sim_ptr = self

      # set accel rf mode

      for i in range( self.ncores ):
        self.states[i].accel_rf = accel_rf

      # pass the state to debug for cycle-triggered debugging

      # TODO: not sure about this, just pass states[0]
      self.debug.set_state( self.states[0] )

      # Close after loading

      exe_file.close()

      # shreesha: runtime metadata
      if runtime_md:
        try:
          runtime_md_file = open( runtime_md, 'rb' )
          addr_list    = [ int(n) for n in runtime_md_file.readline().strip().split(",") ]
          name_list    = runtime_md_file.readline().strip().split(",")
          for i in range( self.ncores ):
            for x,addr in enumerate(addr_list):
              self.states[i].runtime_dict[addr] = name_list[x]
          runtime_md_file.close()
        except IOError:
          print "Could not open the runtime-md file %s " % runtime_md
          return 1

      # Execute the program

      self.run()

      return 0

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

    # NOTE: RPython has an assertion to check the type of entry_point to
    # generates a function type
    #return self.entry_point, None
    return self.get_entry_point(), None

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

