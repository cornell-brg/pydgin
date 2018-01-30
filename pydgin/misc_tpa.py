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

#-------------------------------------------------------------------------
# GangEntry
#-------------------------------------------------------------------------

class GangEntry():
  def __init__( s ):
    s.pc    = 0
    s.cores = []

#-------------------------------------------------------------------------
# GangTable
#-------------------------------------------------------------------------

class GangTable():

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s ):
    s.num_ports = 0
    # table stores gang entries
    s.gang_table = []
    s.limit_lockstep = False

  #-----------------------------------------------------------------------
  # insert_entry
  #-----------------------------------------------------------------------

  def insert_entry( s, sim, core ):
    match = False
    if sim.states[core].lockstep:
      for entry in s.gang_table:
        # a match exists
        if sim.states[core].pc == entry.pc:
          # append to existing group if can fit it
          if s.limit_lockstep and len( entry.cores ) != s.num_ports or not s.limit_lockstep:
            entry.count += 1
            #print "appending to entry for pc: %x, %d" % (sim.states[core].pc, entry.count)
            sim.states[core].ganged = True
            entry.cores.append( core )
            match = True
            break

    # create a new entry
    if not match:
      #print "creating a new entry for pc: %x" % sim.states[core].pc
      new_entry = GangEntry()
      new_entry.pc = sim.states[core].pc
      new_entry.cores.append( core )
      new_entry.count = 1
      sim.states[core].ganged = True
      s.gang_table.append( new_entry )

  #-----------------------------------------------------------------------
  # update_table
  #-----------------------------------------------------------------------

  def update_table( s, sim, grant ):
    free_entry = False
    free_idx = 0
    pc = sim.states[grant].pc
    for entry in s.gang_table:
      if pc == entry.pc:
        #print "match for pc: %x" % pc
        if grant in entry.cores:
          entry.count -= 1
          #print "core in list and count is: ", entry.count
          if entry.count == 0:
            #print "going to free cores:", entry.cores
            free_gang = True
            for core in entry.cores:
              sim.states[core].clear = False
              sim.states[core].ganged = False
            free_entry = True
            break
      free_idx += 1
    if free_entry:
      free_entry = False
      del s.gang_table[free_idx]

# GangTable --------------------------------------------------------------

#-------------------------------------------------------------------------
# LLFUAllocator
#-------------------------------------------------------------------------

class LLFUAllocator():

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s, mdu=True ):
    s.valid          = []    # valid requests
    s.num_reqs       = 0     # number of requests
    s.num_ports      = 0     # port bandwidth
    s.top_priority   = 0     # priority
    s.mdu            = mdu   # mdu or fpu
    s.lockstep       = False # locktep execution
    s.limit_lockstep = False # match lockstep group size to resources
    s.gang_table     = GangTable()

  #-----------------------------------------------------------------------
  # configure
  #-----------------------------------------------------------------------

  def configure( s, num_reqs, num_ports, lockstep, limit_lockstep ):
    s.valid     = [False]*num_reqs
    s.num_reqs  = num_reqs
    s.num_ports = num_ports
    s.lockstep  = lockstep
    # pass params to gang table
    s.gang_table.num_ports = num_ports
    s.gang_table.limit_lockstep = limit_lockstep

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
  # create gangs
  #-----------------------------------------------------------------------

  def create_gangs( s, sim ):
    for core in xrange( sim.ncores ):
      # if a core has a request, is not ganged yet, and if lockstep is enabled
      if s.valid[core] and not sim.states[core].ganged and sim.states[core].lockstep:
        s.gang_table.insert_entry( sim, core )

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

      s.create_gangs( sim )

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
            s.gang_table.update_table( sim, grant )
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
    s.top_priority = 0         # priority for aribitration
    s.mask         = 0
    s.gang_table   = GangTable()

  #-----------------------------------------------------------------------
  # configure
  #-----------------------------------------------------------------------

  def configure( s, num_reqs, num_ports, line_sz, lockstep, limit_lockstep ):
    s.valid     = [False]*num_reqs
    s.reqs      = [None]*num_reqs
    s.num_reqs  = num_reqs
    s.num_ports = num_ports
    s.lockstep  = lockstep
    # mask bits
    mask_bits = ~( line_sz - 1 )
    s.mask = mask_bits & 0xFFFFFFFF
    # pass params to gang table
    s.gang_table.num_ports = num_ports
    s.gang_table.limit_lockstep = limit_lockstep

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
  # create_gangs
  #-----------------------------------------------------------------------

  def create_gangs( s, sim ):
    for core in xrange( sim.ncores ):
      # if a core has a request, is not ganged yet, and if lockstep is enabled
      # NOTE: determining a valid mem request is a bit weird as I clear the
      # valid bit in creating coalesced entries function
      valid_request = False
      valid_request = sim.states[core].stall and sim.states[core].dmem
      if valid_request and not sim.states[core].ganged and sim.states[core].lockstep:
        s.gang_table.insert_entry( sim, core )

  #-----------------------------------------------------------------------
  # drain
  #-----------------------------------------------------------------------

  def drain( s, sim ):

    if len( s.fifo ):
      s.create_gangs( sim )

    for i in xrange( s.num_ports ):
      if len( s.fifo ):
        entry = s.fifo.pop( 0 )
        ports = s.table.pop( entry )

        for port in ports:
          if sim.states[port].lockstep:
            sim.states[port].clear  = True
            sim.states[port].stall  = False
            sim.states[port].dmem   = False
            s.gang_table.update_table( sim, port )
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
