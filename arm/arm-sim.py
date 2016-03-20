#=========================================================================
# arm-sim.py
#=========================================================================

import sys

# need to add parent directory to get access to pydgin package
# TODO: cleaner way to do this?
sys.path.append('..')

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory
from pydgin.misc    import load_program, FatalError
from bootstrap      import syscall_init, memory_size
from instruction    import Instruction
from isa            import decode

#-------------------------------------------------------------------------
# ArmSim
#-------------------------------------------------------------------------
# ARM Simulator

class ArmSim( Sim ):

  def __init__( self ):
    Sim.__init__( self, "ARM", jit_enabled=True )


  # print pc only if non-zero
  def trigger_event( self, descr, pc=0 ):

    if descr not in self.state.event_ctrs:
      self.state.event_ctrs[ descr ] = 1
      iter = 1
    else:
      iter = self.state.event_ctrs[ descr ] + 1
      self.state.event_ctrs[ descr ] = iter

    # if pc provided, append to descr
    if pc != 0:
      descr = "%s_%x" % ( descr, pc )
    if self.state.print_event:
      print descr, self.state.ncycles
    if self.state.event_file:
      # write events to a csv file
      self.state.event_file.write( "%s,%d,%d\n"
                          % (descr, self.state.ncycles, iter) )

  #-----------------------------------------------------------------------
  # decode
  #-----------------------------------------------------------------------
  # The simulator calls architecture-specific decode to decode the
  # instruction bits

  def decode( self, bits ):
    # TODO add decode inside instruction:
    #return decode( bits )

    # This is getting a bit complicated, so here is some explanation. All
    # triggers start with "add r1, r1, #0" (e2811000). Next instruction
    # might mean different things:
    #   add r2, r2, #0 (e2822000) -- JIT region begin
    #   add r3, r3, #0 (e2833000) -- Guard fail (no bridge)
    #   add r4, r4, #0 (e2844000) -- Guard fail (w/ bridge)
    #   add r5, r5, #0 (e2855000) -- Load (disabled)
    #   add r6, r6, #0 (e2866000) -- Store (disabled)
    #   add r7, r7, #0 (e2877000) -- Finish
    #   add r8, r8, #0 (e2888000) -- Function call
    #   add r9, r9, #0 (e2899000) -- Three-inst triggers
    #   add r10,r10,#X (e28aaXXX) -- Add-sub triggers
    #
    # Three-inst triggers (next instruction after "add r9, r9, #0"):
    #   add r2, r2, #0 (e2822000) -- Blackhole region begin
    #   add r3, r3, #0 (e2833000) -- Blackhole region exit
    #   add r4, r4, #0 (e2844000) -- Blackhole region exit (w/ exception)
    #   add r5, r5, #0 (e2855000) -- GC Major collection begin
    #   add r6, r6, #0 (e2866000) -- GC Major collection end
    #   add r7, r7, #0 (e2877000) -- GC Minor collection begin
    #   add r8, r8, #0 (e2888000) -- GC Minor collection end
    #   add r9, r9, #0 (e2899000) -- Tracing begin
    #   add r10,r10,#0 (e28aa000) -- Tracing end
    #   add r11,r11,#0 (e28bb000) -- Tracing begin (GF -- what was this?)
    #   add r12,r12,#0 (e28cc000) -- Tracing end (GF -- what was this?)
    #   add r13,r13,#0 (e28dd000) -- Continue with interpreter
    #   add r14,r14,#0 (e28ee000) -- Continue with interpreter (w/ exception)
    #
    # Add-sub triggers are called as such because they add a value and
    # then they subtract the same value in the nextinstruction. For now,
    # different values added (and subtracted are application-level hooks)
    if self.state.trig_state == 0 and bits == 0xe2811000:
      self.state.trig_state = 1
    elif self.state.trig_state == 1:
      if   bits == 0xe2822000 or \
           bits == 0xe2833000 or \
           bits == 0xe2844000 or \
           bits == 0xe2855000 or \
           bits == 0xe2866000 or \
           bits == 0xe2877000 or \
           bits == 0xe2888000:

        if bits == 0xe2822000:
          self.trigger_event( "jit_block", self.state.pc )
        elif bits == 0xe2877000:
          self.trigger_event( "finish", self.state.pc )
        elif bits == 0xe2833000:
          self.trigger_event( "guard_fail_%x" % self.state.pc )
        elif bits == 0xe2844000:
          self.trigger_event( "guard_fail_bridge_%x" % self.state.pc )
        elif bits == 0xe2888000:
          self.trigger_event( "fun_call_%x" % self.state.pc )
          # if we have counting function calls enabled, record the return
          # pc and the num insts at this point
          if self.state.count_fun_calls:
            self.state.fun_call_num_insts = self.state.ncycles
            self.state.fun_call_return_pc = self.state.pc + 8
        # discount the hook instructions
        self.state.ncycles -= 2
        self.state.trig_state = 0
      elif bits == 0xe2899000:
        self.state.trig_state = 109
      # these are the addsub (application-level) hooks:
      elif ( bits & 0xfffff000 ) == 0xe28aa000:
        # get the hook id
        hook_id = bits & 0xfff
        self.trigger_event( "hook_%s" % hook_id )
        self.state.ncycles -= 2
        self.state.trig_state = 0
      else:
        self.state.trig_state = 0

    elif self.state.trig_state == 109:
      if   bits == 0xe2822000:
        self.trigger_event( "blackhole_start" )
      elif bits == 0xe2833000:
        self.trigger_event( "blackhole_stop_leave" )
      elif bits == 0xe2844000:
        self.trigger_event( "blackhole_stop_exc" )
      elif bits == 0xe2855000:
        self.trigger_event( "gc_major_start" )
      elif bits == 0xe2866000:
        self.trigger_event( "gc_major_stop" )
      elif bits == 0xe2877000:
        self.trigger_event( "gc_minor_start" )
      elif bits == 0xe2888000:
        self.trigger_event( "gc_minor_stop" )
      elif bits == 0xe2899000:
        self.trigger_event( "tracing_start" )
      elif bits == 0xe28aa000:
        self.trigger_event( "tracing_stop" )
      elif bits == 0xe28bb000:
        self.trigger_event( "tracing_start_gf" )
      elif bits == 0xe28cc000:
        self.trigger_event( "tracing_stop_gf" )
      elif bits == 0xe28dd000:
        self.trigger_event( "cont_run_portal" )
      elif bits == 0xe28ee000:
        self.trigger_event( "cont_run_exc" )

      self.state.ncycles -= 3
      self.state.trig_state = 0

    inst_str, exec_fun = decode( bits )
    return Instruction( bits, inst_str ), exec_fun

  #-----------------------------------------------------------------------
  # init_state
  #-----------------------------------------------------------------------
  # This method is called to load the program and initialize architectural
  # state

  def init_state( self, exe_file, run_argv, run_envp ):

    # Load the program into a memory object

    mem = Memory( size=memory_size, byte_storage=False )
    entrypoint, breakpoint = load_program(
        #open( filename, 'rb' ),
        exe_file,
        mem,
        # TODO: GEM5 uses this alignment, remove?
        alignment = 1<<12
    )

    self.state = syscall_init( mem, entrypoint, breakpoint,
                               run_argv, run_envp, self.debug )

    if self.event_filename != "":
      self.state.event_file = open( self.event_filename, "w" )
      # print header
      self.state.event_file.write( "event,insts,iter\n" )

  def run( self ):
    Sim.run( self )
    if self.state.event_file:
      self.state.event_file.close()

# this initializes similator and allows translation and python
# interpretation

init_sim( ArmSim() )

