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
from pydgin.jit   import JitDriver, hint, set_user_param, set_param, \
                         elidable

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-------------------------------------------------------------------------
# colors
#-------------------------------------------------------------------------
# Ref1: http://ozzmaker.com/add-colour-to-text-in-python/
# Ref2: http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html#colors

class colors():
  red    = '\033[31m'
  green  = '\033[32m'
  yellow = '\033[33m'
  blue   = '\033[34m'
  purple = '\033[35m'
  cyan   = '\033[36m'
  white  = '\033[37m'
  end    = '\033[0m'

#-------------------------------------------------------------------------
# ReconvergenceManager
#-------------------------------------------------------------------------
# NOTE: By default there is always fetch combining turned on

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
      next_pc = 0
      next_core = 0
      scheduled_list = []
      # round-robin for given port bandwidth
      for i in xrange( sim.inst_ports ):

        while True:
          s.top_priority = 0 if s.top_priority == sim.ncores-1 else s.top_priority+1
          if not ( s.top_priority in scheduled_list or sim.states[s.top_priority].stop ):
            next_pc = sim.states[s.top_priority].pc
            next_core = s.top_priority
            update_priority = True
            break

        # collect stats
        if sim.states[s.top_priority].spmd_mode:
          sim.unique_spmd += 1
          sim.unique_insts += 1
        elif sim.states[s.top_priority].wsrt_mode and sim.states[s.top_priority].task_mode:
          sim.unique_task += 1
          sim.unique_insts += 1
        elif sim.states[s.top_priority].wsrt_mode and sim.states[s.top_priority].runtime_mode:
          sim.unique_runtime += 1
          sim.unique_insts += 1
        # loop through cores
        for core in range( sim.ncores ):
          # select matching pcs
          if sim.states[core].pc == next_pc and not sim.states[core].stop:
            sim.states[core].active = True
            scheduled_list.append( core )
            # collect stats
            if sim.states[core].spmd_mode:
              sim.total_spmd     += 1
              sim.total_parallel += 1
            elif sim.states[core].wsrt_mode and sim.states[core].task_mode:
              sim.total_task     += 1
              sim.total_wsrt     += 1
              sim.total_parallel += 1
            elif sim.states[core].wsrt_mode and sim.states[core].runtime_mode:
              sim.total_runtime  += 1
              sim.total_wsrt     += 1
              sim.total_parallel += 1
          # if hit hardware barrier, consider it as scheduled to break the loop
          elif sim.states[core].stop and core not in scheduled_list:
            scheduled_list.append( core )
          # not active yet
          elif core not in scheduled_list:
            sim.states[core].active = False

        # update priority
        if len( scheduled_list ) == sim.ncores:
          break

    #---------------------------------------------------------------------
    # Round-Robin + Min-PC hybrid reconvergence
    #---------------------------------------------------------------------
    # FIXME: Add instruction port modeling

    elif sim.reconvergence == 1:

      scheduled_list = []
      for port in xrange( sim.inst_ports ):
        min_core = 0
        min_pc = sys.maxint
        update_priority = False

        # Select the minimum-pc by considering only active cores
        if s.switch_interval == 0:
          for core in range( sim.active_cores ):
            if sim.states[core].pc < min_pc and not ( sim.states[core].stop or core in scheduled_list ):
              min_pc = sim.states[core].pc
              min_core = core
          s.switch_interval = sim.ncores + 1

        # Round-robin arbitration
        else:
          while True:
            # NOTE: if selecting an already scheduled core, update priority
            s.top_priority = 0 if s.top_priority == sim.ncores-1 else s.top_priority+1
            if not ( s.top_priority in scheduled_list or sim.states[s.top_priority].stop ):
              min_pc = sim.states[s.top_priority].pc
              min_core = s.top_priority
              update_priority = True
              break

        # collect stats
        if sim.states[min_core].spmd_mode:
          sim.unique_spmd += 1
          sim.unique_insts += 1
        elif sim.states[min_core].wsrt_mode and sim.states[min_core].task_mode:
          sim.unique_task += 1
          sim.unique_insts += 1
        elif sim.states[min_core].wsrt_mode and sim.states[min_core].runtime_mode:
          sim.unique_runtime += 1
          sim.unique_insts += 1

        # loop through all the cores
        for core in range( sim.ncores ):
          # advance pcs that match the min-pc and make sure to not activate
          # cores that have reached the barrier
          if sim.states[core].pc == min_pc and not sim.states[core].stop:
            sim.states[core].active = True
            scheduled_list.append( core )
            # collect stats
            if sim.states[core].spmd_mode:
              sim.total_spmd     += 1
              sim.total_parallel += 1
            elif sim.states[core].wsrt_mode and sim.states[core].task_mode:
              sim.total_task     += 1
              sim.total_wsrt     += 1
              sim.total_parallel += 1
            elif sim.states[core].wsrt_mode and sim.states[core].runtime_mode:
              sim.total_runtime  += 1
              sim.total_wsrt     += 1
              sim.total_parallel += 1
          # if hit hardware barrier, consider it as scheduled to break the loop
          elif sim.states[core].stop and core not in scheduled_list:
            scheduled_list.append( core )
          # not yet scheduled
          elif core not in scheduled_list:
            sim.states[core].active = False

        s.switch_interval -= 1

        # update priority
        if len( scheduled_list ) == sim.ncores:
          break

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
    self.color = False
    self.reconvergence = 0
    self.unique_insts = 0
    self.reconvergence_manager = ReconvergenceManager()
    self.inst_ports = 0
    # stats
    # NOTE: Collect the stats below only when in parallel mode
    self.unique_insts   = 0 # unique insts in parallel regions
    self.unique_spmd    = 0 # unique insts in spmd region
    self.unique_task    = 0 # unique insts in wsrt tasks
    self.unique_runtime = 0 # unique insts in wsrt runtime
    self.total_spmd     = 0 # total insts in spmd region
    self.total_task     = 0 # total insts in wsrt tasks
    self.total_runtime  = 0 # total insts in wsrt runtime
    self.total_wsrt     = 0 # total insts in wsrt region
    self.total_parallel = 0 # total number of instructions in parallel regions
    # NOTE: Total number of instructions in timing loop
    self.total_steps    = 0
    self.serial_steps   = 0

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
    --color         Turn on color for linetraces
    --analysis      Use the options below
        0 No reconvergence
        1 Min-pc, opportunistic
    --runtime-md    Runtime metadata used in analysis
    --inst-ports    Number of instruction ports (bandwidth)
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

      active = False
      for i in xrange( self.ncores ):
        active |= self.states[i].active
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

      parallel_mode = self.states[0].wsrt_mode or self.states[0].spmd_mode
      if self.states[0].stats_en and not parallel_mode: self.serial_steps += 1

      # check if the count of the barrier is equal to the number of active
      # cores, reset the hardware barrier
      if self.barrier_count == self.active_cores:
        self.barrier_count = 0
        for i in xrange( self.active_cores ):
          if not self.states[i].active:
            self.states[i].active = True
            self.states[i].stop = False

      # shreesha: linetrace
      if self.linetrace:
        if self.states[0].stats_en:
          for i in range( self.ncores ):
            if self.states[i].active:
              parallel_mode = self.states[i].wsrt_mode or self.states[i].spmd_mode
              # core0 in serial section
              if self.color and not parallel_mode and i ==0 :
                print colors.white + pad( "%x |" % self.states[i].pc, 9, " ", False ) + colors.end,
              # others in bthread control function
              elif self.color and not parallel_mode:
                print colors.blue + pad( "%x |" % self.states[i].pc, 9, " ", False ) + colors.end,
              # cores in spmd region
              elif self.color and self.states[i].spmd_mode:
                print colors.purple + pad( "%x |" % self.states[i].pc, 9, " ", False ) + colors.end,
              # cores executing tasks in wsrt region
              elif self.color and self.states[i].task_mode and parallel_mode:
                print colors.green + pad( "%x |" % self.states[i].pc, 9, " ", False ) + colors.end,
              # cores executing runtime function in wsrt region
              elif self.color and self.states[i].runtime_mode and parallel_mode:
                print colors.yellow + pad( "%x |" % self.states[i].pc, 9, " ", False ) + colors.end,
              # No color requested
              else:
                print pad( "%x |" % self.states[i].pc, 9, " ", False ),
            else:
              print pad( " |", 9, " ", False ),
          print

      # shreesha: reconvergence
      self.reconvergence_manager.advance_pcs( self )

    print '\nDONE! Status =', self.states[0].status
    print 'Total ticks Simulated = %d\n' % tick_ctr

    print 'Serial steps in stats region = %d' % self.serial_steps
    print 'Total steps in stats region = %d' % self.total_steps
    parallel_region = self.total_steps - self.serial_steps
    if self.total_steps:
      print 'Percent insts in parallel region = %f\n' % ( 100*parallel_region/float( self.total_steps ) )

    print 'Total insts in parallel regions = %d' % self.total_parallel
    print 'Unique insts in parallel regions = %d' % self.unique_insts
    redundant_insts = self.total_parallel - self.unique_insts
    if self.total_parallel:
      print 'Redundancy in parallel regions = %f' % ( 100*redundant_insts/float( self.total_parallel ) )
    print

    print "Total insts in spmd region = %d " % self.total_spmd
    print 'Unique spmd insts = %d' % self.unique_spmd
    redundant_spmd = self.total_spmd - self.unique_spmd
    if self.total_spmd:
      print 'Redundancy in spmd regions = %f' % ( 100*redundant_spmd/float( self.total_spmd ) )
    print

    print "Total insts in tasks = %d " % self.total_task
    print "Total insts in runtime = %d " % self.total_runtime
    print "Total insts in wsrt region = %d " % self.total_wsrt
    print 'Unique wsrt insts = %d' % ( self.unique_runtime + self.unique_task )
    redundant_wsrt = self.total_wsrt - ( self.unique_runtime + self.unique_task )
    if self.total_wsrt:
      print 'Redundancy in wsrt regions = %f' % ( 100*redundant_wsrt/float( self.total_wsrt ) )

    if self.total_wsrt:
      print "Percent of task insts = %f" % ( 100*self.total_task /float( self.total_wsrt ) )
    print 'Unique task insts = %d' % self.unique_task
    redundant_task = self.total_task - self.unique_task
    if self.total_task:
      print 'Redundancy in task regions = %f' % ( 100*redundant_task/float( self.total_task ) )

    print 'Unique runtime insts = %d' % self.unique_runtime
    redundant_runtime = self.total_runtime - self.unique_runtime
    if self.total_runtime:
      print 'Redundancy in runtime regions = %f' % ( 100*redundant_runtime/float( self.total_runtime ) )
    print

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
                           "--color",
                           "--analysis",
                           "--runtime-md",
                           "--inst-ports",
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

          elif token == "--color":
            self.color = True

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
            self.reconvergence = int( token )

          elif prev_token == "--runtime-md":
            runtime_md = token

          elif prev_token == "--inst-ports":
            self.inst_ports = int(token)

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

      # shreesha: default number of instruction ports
      if self.inst_ports == 0:
        self.inst_ports = self.ncores

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

