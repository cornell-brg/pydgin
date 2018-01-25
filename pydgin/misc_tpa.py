#=========================================================================
# misc_tpa.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : December 11th, 2017
#
# Contains misc-tpa related projects: MemRequest, MemCoalescer,
# LLFUAllocator, Reconvergence Manager, colors etc.

import math
import sys

#-------------------------------------------------------------------------
# global variable
#-------------------------------------------------------------------------

# stack pointer is reg:29 for parc
sp = 29

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
# Task
#-------------------------------------------------------------------------

class Task():

  def __init__(s):
    s.m_func_ptr        = 0
    s.m_args_ptr        = 0
    s.m_ref_count_ptr   = 0
    s.m_begin           = 0
    s.m_end             = 0
    s.m_target_chunk_sz = 0

#-------------------------------------------------------------------------
# ReconvergenceManager
#-------------------------------------------------------------------------
# NOTE: By default there is always fetch combining turned on

class ReconvergenceManager():

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s ):
    s.top_priority    = 0
    s.switch_interval = 0
    s.scheduled_list  = []
    s.unique_pcs      = []
    s.mask            = 0
    s.l0_mask         = 0
    s.coalesce        = True

  #-----------------------------------------------------------------------
  # configure
  #-----------------------------------------------------------------------

  def configure( s, num_cores, coalesce, word_match, line_sz, sched_limit ):
    s.switch_interval = sched_limit
    s.top_priority    = num_cores-1
    # enable coaelscing
    s.coalesce        = coalesce
    # mask bits used for instr coalescing
    mask_sz = line_sz
    if word_match:
      mask_sz = 4
    s.mask = ~( mask_sz - 1 ) & 0xFFFFFFFF
    # mask bits used for checking L0 hits
    s.l0_mask = ~(line_sz - 1) & 0xFFFFFFFF

    print "Coalesing enabled: ", s.coalesce
    print "Coalescing mask is %x" % s.mask
    print "L0 mask is %x" % s.l0_mask

  #-----------------------------------------------------------------------
  # collect_stats
  #-----------------------------------------------------------------------
  # NOTE: Look across all cores that will execute, find instructions that
  # are unique and count total

  def collect_stats( s, sim ):

    s.unique_pcs = []
    for core in xrange( sim.ncores ):
      if sim.states[core].active and sim.states[core].pc not in s.unique_pcs:
        s.unique_pcs.append( sim.states[core].pc )
        # collect total instructions
        if sim.states[core].spmd_mode:
          sim.unique_spmd    += 1
          sim.unique_insts   += 1
        elif sim.states[core].wsrt_mode and sim.states[core].task_mode:
          sim.unique_task    += 1
          sim.unique_insts   += 1
        elif sim.states[core].wsrt_mode and sim.states[core].runtime_mode:
          sim.unique_runtime += 1
          sim.unique_insts   += 1

      if sim.states[core].active:
        # collect total instructions
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

    #if sim.states[0].debug.enabled( "tpa" ):
    #  print "frontend: [",
    #  for core in xrange( sim.ncores ):
    #    if sim.states[core].istall:
    #      print "%d:i," % core,
    #    elif sim.states[core].stall:
    #      print "%d:s," % core,
    #    elif sim.states[core].stop:
    #      print "%d:b," % core,
    #    elif sim.states[core].clear:
    #      print "%d:w," % core,
    #    elif sim.states[core].active:
    #      print "%d:a," % core,
    #    else:
    #      print "%d:n," % core,
    #  print "]"

  #-----------------------------------------------------------------------
  # update_single_pc
  #-----------------------------------------------------------------------
  # updates a single pc

  def update_single_pc( s, sim, core ):
    sim.states[core].active = True
    sim.states[core].istall = False
    s.scheduled_list.append( core )

    # stats for non-SIMT frontend
    parallel_mode = sim.states[core].wsrt_mode or sim.states[core].spmd_mode
    if sim.states[0].stats_en and parallel_mode and not sim.simt:
      sim.unique_imem_accesses += 1
      sim.total_imem_accesses += 1

    # SIMT L0 Buffer present
    if sim.simt and sim.l0_buffer_sz != 0:
      if (sim.states[core].pc & s.l0_mask) in sim.simt_l0_buffer:
        if sim.states[0].stats_en and parallel_mode:
          sim.simt_l0_hits += 1
          sim.total_imem_accesses += 1
      else:
        # add the line to the l0 buffer if there is a l0 buffer present
        if sim.simt_l0_buffer:
          sim.simt_l0_buffer.pop(0)
        sim.simt_l0_buffer.append(sim.states[core].pc & s.l0_mask)
        if sim.states[0].stats_en and parallel_mode:
          sim.unique_imem_accesses += 1
          sim.total_imem_accesses += 1
    # SIMT but no l0 buffer present
    elif sim.simt and sim.l0_buffer_sz == 0:
      if sim.states[0].stats_en and parallel_mode:
        sim.unique_imem_accesses += 1
        sim.total_imem_accesses += 1
    # Not SIMT but l0 buffer present
    elif not sim.simt and sim.l0_buffer_sz != 0:
      # add the line to the l0 buffer if there is a l0 buffer present
      if (sim.states[core].pc & s.l0_mask) not in sim.states[core].l0_buffer:
        if sim.states[core].l0_buffer:
          sim.states[core].l0_buffer.pop(0)
        sim.states[core].l0_buffer.append(sim.states[core].pc & s.l0_mask)

  #-----------------------------------------------------------------------
  # update_pcs
  #-----------------------------------------------------------------------
  # function implements instruction coalescing and in addition if a l0
  # buffer is present and a matched value is not present then the line is
  # replaced

  def update_pcs( s, sim, line_addr ):
    # loop through cores
    for core in xrange( sim.ncores ):

      # select matching pcs
      curr_line_addr = sim.states[core].pc & s.mask
      if curr_line_addr == line_addr and core not in s.scheduled_list:
        sim.states[core].insn_str = 'C:'
        sim.states[core].active = True
        sim.states[core].istall = False
        s.scheduled_list.append( core )
        parallel_mode = sim.states[core].wsrt_mode or sim.states[core].spmd_mode
        if sim.states[0].stats_en and parallel_mode:
          sim.total_coalesces     += 1
          sim.total_imem_accesses += 1
        # add the line to the l0 buffer if there is a l0 buffer present
        if not sim.simt and sim.l0_buffer_sz != 0:
          if (sim.states[core].pc & s.l0_mask) not in sim.states[core].l0_buffer:
            if sim.states[core].l0_buffer:
              sim.states[core].l0_buffer.pop(0)
            sim.states[core].l0_buffer.append(sim.states[core].pc & s.l0_mask)

    # early exit: all cores are scheduled
    if len( s.scheduled_list ) == sim.ncores:
      return True

    return False

  #-----------------------------------------------------------------------
  # get_next_pc
  #-----------------------------------------------------------------------

  def get_next_pc( s, sim ):
    next_pc   = 0
    next_core = 0
    for x in xrange( sim.ncores ):
      s.top_priority = 0 if s.top_priority == sim.ncores-1 else s.top_priority+1
      if not s.top_priority in s.scheduled_list:
        next_pc = sim.states[s.top_priority].pc
        next_core = s.top_priority
        break

    return next_pc, next_core

  #-----------------------------------------------------------------------
  # rr_min_pc
  #-----------------------------------------------------------------------

  def rr_min_pc( s, sim ):
    min_pc   = sys.maxint
    min_core = 0
    # select the minimum-pc by considering only active cores
    if s.switch_interval > 0:
      for core in xrange( sim.ncores ):
        if sim.states[core].pc < min_pc and core not in s.scheduled_list:
          min_pc = sim.states[core].pc
          min_core = core
      s.switch_interval -= 1
      #if sim.states[0].debug.enabled( "tpa" ):
      #  print "min-pc: %x %d" % ( min_pc, min_core )
    # round-robin arbitration
    elif s.switch_interval == 0:
      min_pc, min_core = s.get_next_pc( sim )
      s.switch_interval = sim.sched_limit
      #if sim.states[0].debug.enabled( "tpa" ):
      #  print "rr   : %x %d" % ( min_pc, min_core )
    else:
      print "Something wrong in scheduling tick: %d" % sim.states[0].num_insts
      raise AssertionError

    return min_pc, min_core

  #-----------------------------------------------------------------------
  # rr_min_sp_pc
  #-----------------------------------------------------------------------

  def rr_min_sp_pc( s, sim ):
    min_sp   = sys.maxint
    min_pc   = 0
    min_core = 0
    # select the minimum-pc by considering only active cores
    if s.switch_interval > 0:
      for core in xrange( sim.ncores ):
        if core not in s.scheduled_list:
          if sim.states[core].rf[ sp ] < min_sp:
            min_pc = sim.states[core].pc
            min_core = core
          elif sim.states[core].rf[ sp ] ==  min_sp and sim.states[core].pc < min_pc:
            min_pc = sim.states[core].pc
            min_core = core
      s.switch_interval -= 1
      #if sim.states[0].debug.enabled( "tpa" ):
      #  print "min-sp: %x %d" % ( min_pc, min_core )
    # round-robin arbitration
    elif s.switch_interval == 0:
      min_pc, min_core = s.get_next_pc( sim )
      s.switch_interval = sim.sched_limit
      #if sim.states[0].debug.enabled( "tpa" ):
      #  print "rr   : %x %d" % ( min_pc, min_core )
    else:
      print "Something wrong in scheduling tick: %d" % sim.states[0].num_insts
      raise AssertionError

    return min_pc, min_core

  #-----------------------------------------------------------------------
  # xtick
  #-----------------------------------------------------------------------

  def xtick( s, sim ):

    # do not consider a core that is stalling or reached hw barroer
    s.scheduled_list = []
    for core in xrange( sim.ncores ):
      # deactivate all cores; cores get activated based on the number of
      # ports, coalescing, reconvergence policy, and l0 buffer selection
      # NOTE: if a core is at a barrier or waiting for others to catchup
      # (clear) it is deactivated but when it is stalling it is active
      if sim.states[core].stall:
        sim.states[core].active = True
      else:
        sim.states[core].active = False
        sim.states[core].istall = True
        sim.states[core].insn_str = ' :'

      if sim.states[core].stall or sim.states[core].stop or sim.states[core].clear:
        s.scheduled_list.append( core )
        sim.states[core].istall = False

    # check if any cores have cached in the line in the l0 buffer
    if sim.l0_buffer_sz != 0 and not sim.simt:
      for core in xrange( sim.ncores ):
        l0_line_addr = sim.states[core].pc & s.l0_mask
        if l0_line_addr in sim.states[core].l0_buffer and core not in s.scheduled_list:
          s.scheduled_list.append( core )
          sim.states[core].active = True
          sim.states[core].istall = False
          parallel_mode = sim.states[core].wsrt_mode or sim.states[core].spmd_mode
          if sim.states[0].stats_en and parallel_mode:
            sim.states[core].l0_hits += 1
            sim.total_imem_accesses += 1
          sim.states[core].insn_str = 'L:'

    # all cores all either stalling or have reached a barrier or have
    # instructions in L0 buffer
    if len( s.scheduled_list ) == sim.ncores:
      s.collect_stats( sim )
      return

    # select pcs based on available bandwidth
    for i in xrange( sim.inst_ports ):
      next_pc   = 0
      next_core = 0
      all_done  = False

      # round-robin for given port bandwidth
      if sim.reconvergence == 0:
        next_pc, next_core = s.get_next_pc( sim )

      # round-robin + min-pc hybrid reconvergence
      elif sim.reconvergence == 1:
        next_pc, next_core = s.rr_min_pc( sim )

      # round-robin + min-sp/pc hybrid reconvergence
      elif sim.reconvergence == 2:
        next_pc, next_core = s.rr_min_sp_pc( sim )

      # NOTE: update_single_pc updates just one core based on the policy
      # for reconvergence and resource constraints and update_pcs updates
      # other cores for a given constraint only if coalescing is enabled
      line_addr = next_pc & s.mask
      sim.states[next_core].insn_str = 'S:'
      s.update_single_pc( sim, next_core )
      if len( s.scheduled_list ) == sim.ncores:
        break

      if s.coalesce:
        # check for early exit
        all_done = s.update_pcs( sim, line_addr )
        if all_done:
          break

    # collect stats before exit
    s.collect_stats( sim )

#-------------------------------------------------------------------------
# LLFUAllocator
#-------------------------------------------------------------------------

class LLFUAllocator():

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s, mdu=True ):
    s.valid        = []    # valid requests
    s.num_reqs     = 0     # number of requests
    s.num_ports    = 0     # port bandwidth
    s.top_priority = 0     # priority
    s.mdu          = mdu   # mdu or fpu
    s.lockstep     = False # locktep execution
    s.pc_dict      = {}    # data-structure used to enforce lockstep execution

  #-----------------------------------------------------------------------
  # configure
  #-----------------------------------------------------------------------

  def configure( s, num_reqs, num_ports, lockstep ):
    s.valid     = [False]*num_reqs
    s.num_reqs  = num_reqs
    s.num_ports = num_ports
    s.lockstep  = lockstep

  #-----------------------------------------------------------------------
  # set_request
  #-----------------------------------------------------------------------

  def set_request( s, idx ):
    s.valid[ idx ] = True

  #-----------------------------------------------------------------------
  # get_grant
  #-----------------------------------------------------------------------

  def get_grant( s ):
    grant = s.top_priority
    if s.valid[ grant ]:
      return grant
    else:
      for i in xrange( s.num_reqs ):
        grant = 0 if grant == s.num_reqs-1 else grant+1
        if s.valid[ grant ]:
          return grant
    return grant

  #-----------------------------------------------------------------------
  # evaluate_pcs
  #-----------------------------------------------------------------------
  # evaluates all pcs and figures out the groups

  def evaluate_pcs( s, sim ):
    s.pc_dict = {}

    for core in xrange( sim.ncores ):
      if sim.states[core].stall and not sim.states[core].clear and sim.states[core].lockstep:
        s.pc_dict[sim.states[core].pc] = s.pc_dict.get(sim.states[core].pc, 0) + 1

  #-----------------------------------------------------------------------
  # xtick
  #-----------------------------------------------------------------------

  def xtick( s, sim ):
    compute = False
    for i in xrange( sim.ncores ):
      if s.valid[ i ]:
        compute = True
        break

    if compute:

      s.evaluate_pcs( sim )

      for i in xrange( s.num_ports ):
        grant = s.get_grant()
        if s.valid[ grant ]:
          if sim.states[grant].lockstep:
            s.valid[grant]          = False
            sim.states[grant].clear = True
            sim.states[grant].stall = False
            if s.mdu:
              sim.states[grant].mdu = False
            else:
              sim.states[grant].fpu = False
            pc = sim.states[grant].pc
            s.pc_dict[ pc ] -= 1
            if s.pc_dict[ pc ] == 0:
              for core in xrange( sim.ncores ):
                # only clear cores that are marked to be cleared
                if sim.states[core].curr_pc == pc and sim.states[core].clear:
                  sim.states[core].clear = False
          else:
            sim.states[grant].stall = False
            s.valid[grant] = False
            if s.mdu: sim.states[grant].mdu = False
            else:     sim.states[grant].fpu = False
          s.top_priority = 0 if s.top_priority == s.num_reqs-1 else s.top_priority+1

#-------------------------------------------------------------------------
# MemRequest
#-------------------------------------------------------------------------

class MemRequest():

  def __init__( s ):
    # 0 - loads, 1 - stores, 2 - amos
    s.type_ = 0
    # size of memory request in bytes
    s.len_  = 0
    # effective memory address
    s.addr  = 0

#-------------------------------------------------------------------------
# MemCoalescer
#-------------------------------------------------------------------------
# MemCoalescer class models a memory coalescing unit which accepts incoming
# memory requests and creates coalesced requests

class MemCoalescer():

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s ):
    s.valid        = []        # valid requests
    s.num_reqs     = 0         # number of requests
    s.reqs         = []        # requests list
    s.fifo         = []        # fifo to clear requests
    s.table        = {}        # key-value map, key = coalesced request, value = list of ports that coalesce
    s.num_ports    = 0         # port bandwidth
    s.lockstep     = False     # flag to enforce lockstep execution
    s.pc_dict      = {}        # data-structure used to enforce lockstep execution
    s.top_priority = 0         # priority for aribitration
    s.mask         = 0

  #-----------------------------------------------------------------------
  # configure
  #-----------------------------------------------------------------------

  def configure( s, num_reqs, num_ports, line_sz, lockstep ):
    s.valid     = [False]*num_reqs
    s.reqs      = [None]*num_reqs
    s.num_reqs  = num_reqs
    s.num_ports = num_ports
    s.lockstep  = lockstep
    # mask bits
    mask_bits = ~( line_sz - 1 )
    s.mask = mask_bits & 0xFFFFFFFF

  #-----------------------------------------------------------------------
  # set_request
  #-----------------------------------------------------------------------

  def set_request( s, idx, req ):
    s.valid[ idx ] = True
    s.reqs[ idx ]  = req

  #-----------------------------------------------------------------------
  # coalesce
  #-----------------------------------------------------------------------

  def coalesce( s, sim ):
    for i in xrange( s.num_reqs ):
      next_port = s.top_priority
      if s.valid[next_port]:
        # check the line that will be requested
        line_addr = s.reqs[next_port].addr & s.mask

        # temp entry
        entry       = MemRequest()
        entry.type_ = s.reqs[next_port].type_
        entry.len_  = 0
        entry.addr  = line_addr

        match = False
        for key in s.table.keys():
          # NOTE: coalesce only for loads; need to check both the types of
          # existing keys and the new entry
          if entry.type_ == 0 and key.type_ == 0 and entry.addr == key.addr:
            s.table[key].append( next_port )
            match = True
            parallel_mode = sim.states[next_port].wsrt_mode or sim.states[next_port].spmd_mode
            if sim.states[0].stats_en and parallel_mode:
              sim.total_dmem_accesses += 1

        if not match:
          s.table[entry] = [ next_port ]
          s.fifo.append( entry )
          parallel_mode = sim.states[next_port].wsrt_mode or sim.states[next_port].spmd_mode
          if sim.states[0].stats_en and parallel_mode:
            sim.unique_dmem_accesses += 1
            sim.total_dmem_accesses += 1

        s.valid[next_port] = False
      s.top_priority = 0 if s.top_priority == s.num_reqs-1 else s.top_priority+1

  #-----------------------------------------------------------------------
  # evaluate_pcs
  #-----------------------------------------------------------------------
  # evaluates all pcs and figures out the groups

  def evaluate_pcs( s, sim ):
    s.pc_dict = {}

    for core in xrange( sim.ncores ):
      if sim.states[core].stall and not sim.states[core].clear and sim.states[core].lockstep:
        s.pc_dict[sim.states[core].pc] = s.pc_dict.get(sim.states[core].pc, 0) + 1

  #-----------------------------------------------------------------------
  # drain
  #-----------------------------------------------------------------------

  def drain( s, sim ):

    if len( s.fifo ):
      s.evaluate_pcs( sim )

    for i in xrange( s.num_ports ):
      if len( s.fifo ):
        entry = s.fifo.pop( 0 )
        ports = s.table.pop( entry )

        for port in ports:
          if sim.states[port].lockstep:
            pc = sim.states[port].pc
            s.pc_dict[ pc ] -= 1
            sim.states[port].clear  = True
            sim.states[port].stall  = False
            sim.states[port].dmem   = False
            if s.pc_dict[pc] == 0:
              for core in xrange( sim.ncores ):
                # only clear cores that are marked to be cleared
                if sim.states[core].curr_pc == pc and sim.states[core].clear:
                  sim.states[core].clear = False
          else:
            sim.states[port].stall = False
            sim.states[port].dmem  = False

      else:
        break

  #-----------------------------------------------------------------------
  # xtick
  #-----------------------------------------------------------------------

  def xtick( s, sim ):

    # check if there are any valid mem requests
    any_valid = False
    for i in xrange( s.num_reqs ):
      if s.valid[i]:
        any_valid = True
        break

    if any_valid:
      s.coalesce(sim)

    s.drain(sim)
