#=========================================================================
# parc-sim.py
#=========================================================================

import sys
import os.path

# need to add parent directory to get access to pydgin package
# TODO: cleaner way to do this?
sys.path.append('..')

# hawajkm: to make this stat version lightweight, the stats will be dumped
#          into a file that has the executable filename in its name followed
#          by the type of the stats, e.g. {EXE_FILENAME}_output.csv
def path_leaf(path):
  pos = path.rfind('/')
  if pos < 0: pos = -1
  return path[pos+1:]

from pydgin.sim     import Sim, init_sim
from pydgin.storage import Memory
from pydgin.misc    import load_program
from pydgin         import elf

from bootstrap      import syscall_init, test_init, memory_size, \
                           pkernel_init
from instruction    import Instruction
from isa            import decode, reg_map

#=======================================================================
# Instructions Mix class: this is a dirty hack. Fix if needed.  -hawajkm
#=======================================================================
class CtrlStats():
  def __init__(self):
    self.j      = 0
    self.jr     = 0
    self.cond   = 0
    self.jal    = 0

class ArithStats():
  def __init__(self):
    self.ints = 0
    self.llfu = 0
    self.fp   = 0

class MemStats():
  def __init__(self):
    self.ld   = 0
    self.st   = 0
    self.sync = 0

class AMOStats():
  def __init__(self):
    self.arith = 0
    self.mov   = 0

class SysCallStats():
  def __init__(self):
    self.calls = 0
    self.ret   = 0

class MiscStats():
  def __init__(self):
    self.mov = 0
    self.nop = 0

class InstsStats():
  def __init__(self):
    self.count = 0
    self.ctrl  = CtrlStats()
    self.arith = ArithStats()
    self.mem   = MemStats()
    self.amo   = AMOStats()
    self.sys   = SysCallStats()
    self.misc  = MiscStats()

class MemReqStats():
  def __init__(self):
    self._type   = ""
    self.bblock  = 0
    self.pc      = 0
    self.address = 0
    self.data    = 0

class PCALLStats():
  def __init__(self):
    self.size    = 0
    self.limit   = 0
    self.target  = 0
    self.pc      = 0
    self.insts   = InstsStats()
    self.iters   = []
    self.itersA  = []
    self.div     = []
    self.mem_req = []
    self.func    = []

class PCALLStats():
  def __init__(self):
    self.size  = 0
    self.insts = InstsStats()
    self.iters = []

#-------------------------------------------------------------------------
# ParcSim
#-------------------------------------------------------------------------
# PARC Simulator

class ParcSim( Sim ):

  def __init__( self ):
    Sim.__init__( self, "PARC", jit_enabled=True )

  #-----------------------------------------------------------------------
  # decode
  #-----------------------------------------------------------------------
  # The simulator calls architecture-specific decode to decode the
  # instruction bits

  def decode( self, bits ):
    # TODO add decode inside instruction:
    #return decode( bits )
    inst_str, exec_fun = decode( bits )
    return Instruction( bits, inst_str ), exec_fun

  #-----------------------------------------------------------------------
  # init_state
  #-----------------------------------------------------------------------
  # This method is called to load the program and initialize architectural
  # state

  def init_state( self, exe_file, exe_name, run_argv, run_envp, testbin ):

    # Load the program into a memory object

    mem = Memory( size=memory_size, byte_storage=False )
    entrypoint, breakpoint = load_program( exe_file, mem  )

    # if there is also a pkernel specified, load it as well

    pkernel_enabled = False
    reset_addr = 0x1000
    if self.pkernel_bin is not None:
      try:
        pkernel_bin = self.pkernel_bin
        assert pkernel_bin is not None
        pkernel = open( pkernel_bin, 'rb' )
        load_program( pkernel, mem )
        # we also pick the pkernel reset vector if specified
        # TODO: get this from the elf
        reset_addr = 0xc000000
        pkernel_enabled = True
      except IOError:
        print "Could not open pkernel %s\nFalling back to no-pkernel mode" \
              % self.pkernel_bin

    # Insert bootstrapping code into memory and initialize processor state

    # TODO: testbin is hardcoded false right now
    testbin = False

    #if testbin: self.state = test_init   ( mem, debug )
    if pkernel_enabled:
      # TODO: get args_start_addr from elf
      self.states = pkernel_init( mem, breakpoint, run_argv,
                                  run_envp, self.debug,
                                  args_start_addr=0xd000320,
                                  ncores=self.ncores,
                                  reset_addr=reset_addr )
    else:
      self.states = syscall_init( mem, breakpoint, run_argv,
                                  run_envp, self.debug,
                                  ncores=self.ncores,
                                  reset_addr=reset_addr )

    for state in self.states:
      state.testbin  = testbin
      state.exe_name = exe_name

  #---------------------------------------------------------------------
  # run
  #---------------------------------------------------------------------
  # Override sim's run to print stat_num_insts on exit

  def run( self ):
    Sim.run( self )
    for i, state in enumerate( self.states ):
      print "Core %d Instructions Executed in Stat Region = %d" % \
            ( i, state.stat_num_insts )
      # we also calculate the stat instructions
      for j in xrange( 16 ):
        # first check if the stat was enabled
        if state.stat_inst_en[ j ]:
          # calculate the final value
          state.stat_inst_num_insts[ j ] += state.num_insts - \
                                          state.stat_inst_begin[j]

        # print the stat if it's greater than 0
        if state.stat_inst_num_insts[ j ] > 0:
          print "  Stat %d = %d" % ( j, state.stat_inst_num_insts[ j ] )
    
    # hawajkm: printing pcall stats
    #          we only assume that pcall is relevant in core 0
    print "Executed %d pcalls" % self.states[0].xpc_stats.count
    
    # Get executable name
    exe_filename = path_leaf(self.states[0].exe_name)
    
    # We initiate a summation xpc_stats
    total_xpc_stats = PCALLStats()
    
    # Handle multi-files in same folder
    # Print different pcalls with their stats and output a csv data to a file
    if not os.path.exists(exe_filename + "_output.csv"):
      csvOutput = open(exe_filename + "_output.csv", "wb")
    else:
      i = 0
      while(1):
        if not os.path.exists(exe_filename + "_output" + str(i) + ".csv"):
          csvOutput = open(exe_filename + "_output" + str(i) + ".csv", "wb")
          break
        i += 1
    # Branch data
    if not os.path.exists(exe_filename + "_divergence.csv"):
      divOutput = open(exe_filename + "_divergence.csv", "wb")
    else:
      i = 0
      while(1):
        if not os.path.exists(exe_filename + "_divergence" + str(i) +".csv"):
          divOutput = open(exe_filename + "_divergence" + str(i) + ".csv", "wb")
          break
        i += 1
    # Function Calls
    if not os.path.exists(exe_filename + "_function_calls.csv"):
      funcOutput = open(exe_filename + "_function_calls.csv", "wb")
    else:
      i = 0
      while(1):
        if not os.path.exists(exe_filename + "_function_calls" + str(i) + ".csv"):
          funcOutput = open(exe_filename + "_function_calls" + str(i) + ".csv", "wb")
          break
        i += 1
    # Number of dynamic Instructions
    if not os.path.exists(exe_filename + "_numinstructions.csv"):
      instOutput = open(exe_filename + "_numinstructions.csv", "wb")
    else:
      i = 0
      while(1):
        if not os.path.exists(exe_filename + "_numinstructions" + str(i) + ".csv"):
          instOutput = open(exe_filename + "_numinstructions" + str(i) + ".csv", "wb")
          break
        i += 1
    # Dump for divergence, but technical format
    if not os.path.exists(exe_filename + "_divergence.bin"):
      divTOutput = open(exe_filename + "_divergence.bin", "wb")
    else:
      i = 0
      while(1):
        if not os.path.exists(exe_filename + "_divergence" + str(i) + ".bin"):
          divTOutput = open(exe_filename + "_divergence" + str(i) + ".bin", "wb")
          break
        i += 1

    # Dump for divergence, but technical format
    if not os.path.exists(exe_filename + "_memory.bin"):
      memOutput = open(exe_filename + "_memory.bin", "wb")
    else:
      i = 0
      while(1):
        if not os.path.exists(exe_filename + "_memory" + str(i) + ".bin"):
          memOutput = open(exe_filename + "_memory" + str(i) + ".bin", "wb")
          break
        i += 1

    # Print the header row
    csvOutput.write("pcall_id,size,total_insts,pcall_insts,ctrl.cond,ctrl.j,ctrl.jr,ctrl.jal,arith.int,arith.llfu,arith.fp,mem.ld,mem.st,mem.sync,amo.mov,amo.arith,sys.calls,sys.eret,misc.mov,misc.nop")
    # function calls
    funcOutput.write("pcall_id,(call_pc, func_pc)")
    # ctrlOutput
    divOutput.write("pcall_id,xi,(branch_pc, target_pc)")
    divTOutput.write("%d" % (self.states[0].xpc_stats.count))
    # Number of dynamic instructions
    instOutput.write("pcall_id,number_of_instructions")
    # Memory Trace
    memOutput.write("%d" % (self.states[0].xpc_stats.count))
    for i, pcall in enumerate(self.states[0].xpc_stats.pcalls):
      
      # Add it to our final total
      total_xpc_stats.size              += pcall.size
      total_xpc_stats.insts.count       += pcall.insts.count
      total_xpc_stats.insts.ctrl.cond   += pcall.insts.ctrl.cond
      total_xpc_stats.insts.ctrl.j      += pcall.insts.ctrl.j
      total_xpc_stats.insts.ctrl.jr     += pcall.insts.ctrl.jr
      total_xpc_stats.insts.ctrl.jal    += pcall.insts.ctrl.jal
      total_xpc_stats.insts.arith.ints  += pcall.insts.arith.ints
      total_xpc_stats.insts.arith.fp    += pcall.insts.arith.fp
      total_xpc_stats.insts.arith.llfu  += pcall.insts.arith.llfu
      total_xpc_stats.insts.mem.ld      += pcall.insts.mem.ld
      total_xpc_stats.insts.mem.st      += pcall.insts.mem.st
      total_xpc_stats.insts.mem.sync    += pcall.insts.mem.sync
      total_xpc_stats.insts.amo.mov     += pcall.insts.amo.mov
      total_xpc_stats.insts.amo.arith   += pcall.insts.amo.arith
      total_xpc_stats.insts.sys.calls   += pcall.insts.sys.calls
      total_xpc_stats.insts.sys.ret     += pcall.insts.sys.ret
      total_xpc_stats.insts.misc.mov    += pcall.insts.misc.mov
      total_xpc_stats.insts.misc.nop    += pcall.insts.misc.nop
      
      # Write to file
      csvOutput.write("\n%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" %(i, pcall.pc, pcall.target, pcall.size, self.states[0].xpc_stats.insts_t[i] if i < len(self.states[0].xpc_stats.insts_t) else 0, pcall.insts.count, pcall.insts.ctrl.cond, pcall.insts.ctrl.j, pcall.insts.ctrl.jr, pcall.insts.ctrl.jal, pcall.insts.arith.ints, pcall.insts.arith.llfu, pcall.insts.arith.fp, pcall.insts.mem.ld, pcall.insts.mem.st, pcall.insts.mem.sync, pcall.insts.amo.mov, pcall.insts.amo.arith, pcall.insts.sys.calls, pcall.insts.sys.ret, pcall.insts.misc.mov, pcall.insts.misc.nop))

      # Dump the function calls by this pcall
      funcOutput.write("\n%d, [" % i)
      # Iterate through all calls
      for k, func in enumerate(pcall.func):
        if k != 0:
          funcOutput.write(", ")
        funcOutput.write("(0x%x, 0x%x)" % (func.pc, func.target))
      funcOutput.write("]")
      
      # Dump the divergence of every iteration
      # currently, I am dumping the divergence with local iteration number. If needed,
      # the divergence structure should hold the xi of the iteration as chunking could
      # screw the order of where the iterations are recorded
      # Also, keep a special copy of the analysis that is code-friendly
      divTOutput.write("\n0x%x 0x%x 0x%x" % (pcall.pc, pcall.target, len(pcall.div)))
      for d, divArray in enumerate(pcall.div):
        divOutput.write("\n%d,%d,[" % (i, d))
        divTOutput.write("\n%d" % (len(divArray)))
        for k, div in enumerate(divArray):
          if k != 0:
            divOutput.write(", ")
          divOutput.write("(0x%x, 0x%x)" % (div.pc, div.target))
          divTOutput.write(" 0x%x 0x%x" % (div.pc, div.target))
        divOutput.write("]")

      # Dump the divergence of every iteration in a format suitable for python analysis
      #divTOutput.write("\n%d" % (len(pcall.div)))
      #for d, divArray in enumerate(pcall.div):
      #  divTOutput.write("\n%d" % (len(divArray)))
      #  for k, div in enumerate(divArray):
      #    #if k != 0:
      #    #  divTOutput.write(" ")
      #    divTOutput.write(" 0x%x 0x%x" % (div.pc, div.target))

      # Dump the number of dynamic instructions per iteration
      #instOutput.write("\n%d, [" % i)
      instOutput.write("\n")
      # Iterate through all calls
      for k, nIter in enumerate(pcall.iters):
        if k != 0:
          instOutput.write(",")
        instOutput.write("%d" % nIter)
      #instOutput.write("]")

      # Dump memory trace
      memOutput.write("\n0x%x 0x%x 0x%x" % (pcall.pc, pcall.target, len(pcall.mem_req)))
      for d, memArray in enumerate(pcall.mem_req):
        memOutput.write("\n%d" % (len(memArray)))
        for req in memArray:
          memOutput.write(" %s %d 0x%x 0x%x 0x%x" % (req._type, req.bblock, req.pc, req.address, req.data))
#      print "  pcall %d:" % i
#      
#      # Get to it
#      print "    range = %d" % pcall.size  
#      print "    Instructions:"
#      print "      Count = %d" % pcall.insts.count
#      print "      Mix:"
#      print "        Branches:"
#      print "          Total          = %d" % (pcall.insts.ctrl.cond + pcall.insts.ctrl.uncond + pcall.insts.ctrl.jal)
#      print "          Conditionals   = %d" % pcall.insts.ctrl.cond
#      print "          Unconditionals = %d" % pcall.insts.ctrl.uncond
#      print "          JALs           = %d" % pcall.insts.ctrl.jal
#      print "        Arithmatics:"
#      print "          Total       = %d" % (pcall.insts.arith.ints + pcall.insts.arith.llfu)
#      print "          Integres    = %d" % pcall.insts.arith.ints
#      print "          Floatpoints = %d" % pcall.insts.arith.llfu
#      print "        Memory:"
#      print "          Totsl  = %d" % (pcall.insts.mem.ld + pcall.insts.mem.st)
#      print "          Loads  = %d" % pcall.insts.mem.ld
#      print "          Stores = %d" % pcall.insts.mem.st
#      print "        AMO:"
#      print "          Total       = %d" % (pcall.insts.amo.arith + pcall.insts.amo.mov)
#      print "          Arithmetics = %d" % pcall.insts.amo.arith
#      print "          Moves       = %d" % pcall.insts.amo.mov
#      print "        Misc:"
#      print "          Total = %d" % (pcall.insts.misc.mov + pcall.insts.misc.nop)
#      print "          Move  = %d" % pcall.insts.misc.mov
#      print "          Nops  = %d" % pcall.insts.misc.nop
#      print "        syscalls:"
#      print "          Total = %d" % (pcall.insts.sys.calls + pcall.insts.sys.ret)
#      print "          calls = %d" % pcall.insts.sys.calls
#      print "          rets  = %d" % pcall.insts.sys.ret
    
    # Total
    #csvOutput.write("\n%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" %(-1,0,0,total_xpc_stats.size, self.states[0].stat_num_insts, total_xpc_stats.insts.count, total_xpc_stats.insts.ctrl.cond, total_xpc_stats.insts.ctrl.cond, total_xpc_stats.insts.ctrl.jal, total_xpc_stats.insts.arith.ints, total_xpc_stats.insts.arith.llfu, total_xpc_stats.insts.mem.ld, total_xpc_stats.insts.mem.st, total_xpc_stats.insts.amo.mov, total_xpc_stats.insts.amo.arith, total_xpc_stats.insts.sys.calls, total_xpc_stats.insts.sys.ret, total_xpc_stats.insts.misc.mov, total_xpc_stats.insts.misc.nop))
    csvOutput.write("\n%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" %(-1, 0, 0, total_xpc_stats.size, self.states[0].stat_num_insts, total_xpc_stats.insts.count, total_xpc_stats.insts.ctrl.cond, total_xpc_stats.insts.ctrl.j, total_xpc_stats.insts.ctrl.jr, total_xpc_stats.insts.ctrl.jal, total_xpc_stats.insts.arith.ints, total_xpc_stats.insts.arith.llfu, total_xpc_stats.insts.arith.fp, total_xpc_stats.insts.mem.ld, total_xpc_stats.insts.mem.st, total_xpc_stats.insts.mem.sync, total_xpc_stats.insts.amo.mov, total_xpc_stats.insts.amo.arith, total_xpc_stats.insts.sys.calls, total_xpc_stats.insts.sys.ret, total_xpc_stats.insts.misc.mov, total_xpc_stats.insts.misc.nop))

    # Close file
    csvOutput.close()
    funcOutput.close()
    divOutput.close()
    divTOutput.close()
    instOutput.close()
    
    # Print the total
#    print ""
#    print ""
#    print ""
#    print "Total pcall stats:"
#
#    # Get to it
#    print "  count = %d" % self.states[0].xpc_stats.count
#    print "  range = %d" % total_xpc_stats.size
#    print "  Instructions:"
#    print "    Count = %d" % total_xpc_stats.insts.count
#    print "    Mix:"
#    print "      Branches:"
#    print "        Total          = %d" % (total_xpc_stats.insts.ctrl.cond + total_xpc_stats.insts.ctrl.uncond + total_xpc_stats.insts.ctrl.jal)
#    print "        Conditionals   = %d" % total_xpc_stats.insts.ctrl.cond
#    print "        Unconditionals = %d" % total_xpc_stats.insts.ctrl.uncond
#    print "        JAL            = %d" % total_xpc_stats.insts.ctrl.jal
#    print "      Arithmetics:"
#    print "        Total       = %d" % (total_xpc_stats.insts.arith.ints + total_xpc_stats.insts.arith.llfu)
#    print "        Integers    = %d" % total_xpc_stats.insts.arith.ints
#    print "        Floatpoints = %d" % total_xpc_stats.insts.arith.llfu
#    print "      Memory:"
#    print "        Totsl  = %d" % (total_xpc_stats.insts.mem.ld + total_xpc_stats.insts.mem.st)
#    print "        Loads  = %d" % total_xpc_stats.insts.mem.ld
#    print "        Stores = %d" % total_xpc_stats.insts.mem.st
#    print "      AMO:"
#    print "        Total       = %d" % (total_xpc_stats.insts.amo.arith + total_xpc_stats.insts.amo.mov)
#    print "        Arithmetics = %d" % total_xpc_stats.insts.amo.arith
#    print "        Moves       = %d" % total_xpc_stats.insts.amo.mov
#    print "      Misc:"
#    print "        Total = %d" % (total_xpc_stats.insts.misc.mov + total_xpc_stats.insts.misc.nop)
#    print "        Move  = %d" % total_xpc_stats.insts.misc.mov
#    print "        Nops  = %d" % total_xpc_stats.insts.misc.nop
#    print "      syscalls:"
#    print "        Total = %d" % (total_xpc_stats.insts.sys.calls + total_xpc_stats.insts.sys.ret)
#    print "        calls = %d" % total_xpc_stats.insts.sys.calls
#    print "        rets  = %d" % total_xpc_stats.insts.sys.ret

    # Print the total
#    print ""
#    print ""
#    print ""
#    print "Average pcall stats:"
#
#    # Get to it
#    print "  range = %d" % (total_xpc_stats.size / self.states[0].xpc_stats.count)
#    print "  Instructions:"
#    print "    Count = %d" % (total_xpc_stats.insts.count / self.states[0].xpc_stats.count)
#    print "    Mix:"
#    print "      Branches:"
#    print "        Total          = %d" % ((total_xpc_stats.insts.ctrl.cond + total_xpc_stats.insts.ctrl.uncond) / self.states[0].xpc_stats.count)
#    print "        Conditionals   = %d" % (total_xpc_stats.insts.ctrl.cond / self.states[0].xpc_stats.count)
#    print "        Unconditionals = %d" % (total_xpc_stats.insts.ctrl.uncond / self.states[0].xpc_stats.count)
#    print "      Arithmetics:"
#    print "        Total       = %d" % ((total_xpc_stats.insts.arith.ints + total_xpc_stats.insts.arith.llfu) / self.states[0].xpc_stats.count)
#    print "        Integres    = %d" % (total_xpc_stats.insts.arith.ints / self.states[0].xpc_stats.count)
#    print "        Floatpoints = %d" % (total_xpc_stats.insts.arith.llfu / self.states[0].xpc_stats.count)
#    print "      Memory:"
#    print "        Totsl  = %d" % ((total_xpc_stats.insts.mem.ld + total_xpc_stats.insts.mem.st) / self.states[0].xpc_stats.count)
#    print "        Loads  = %d" % (total_xpc_stats.insts.mem.ld / self.states[0].xpc_stats.count)
#    print "        Stores = %d" % (total_xpc_stats.insts.mem.st / self.states[0].xpc_stats.count)
#    print "      AMO:"
#    print "        Total       = %d" % ((total_xpc_stats.insts.amo.arith + total_xpc_stats.insts.amo.mov) / self.states[0].xpc_stats.count)
#    print "        Arithmetics = %d" % (total_xpc_stats.insts.amo.arith / self.states[0].xpc_stats.count)
#    print "        Moves       = %d" % (total_xpc_stats.insts.amo.mov / self.states[0].xpc_stats.count)
#    print "      Misc:"
#    print "        Total = %d" % ((total_xpc_stats.insts.misc.mov + total_xpc_stats.insts.misc.nop) / self.states[0].xpc_stats.count)
#    print "        Move  = %d" % (total_xpc_stats.insts.misc.mov / self.states[0].xpc_stats.count)
#    print "        Nops  = %d" % (total_xpc_stats.insts.misc.nop / self.states[0].xpc_stats.count)
#    print "      syscalls:"
#    print "        Total = %d" % ((total_xpc_stats.insts.sys.calls + total_xpc_stats.insts.sys.ret) / self.states[0].xpc_stats.count)
#    print "        calls = %d" % (total_xpc_stats.insts.sys.calls / self.states[0].xpc_stats.count)
#    print "        rets  = %d" % (total_xpc_stats.insts.sys.ret / self.states[0].xpc_stats.count)

# this initializes similator and allows translation and python
# interpretation

init_sim( ParcSim() )

