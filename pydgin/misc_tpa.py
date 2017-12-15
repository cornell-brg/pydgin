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

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s ):
    s.top_priority    = 0
    s.switch_interval = 0

  #-----------------------------------------------------------------------
  # configure
  #-----------------------------------------------------------------------

  def configure( s, num_cores ):
    s.switch_interval = num_cores
    s.top_priority    = num_cores-1

  #-----------------------------------------------------------------------
  # xtick
  #-----------------------------------------------------------------------

  def xtick( s, sim ):

    scheduled_list = []
    for core in xrange( sim.ncores ):
      # do not consider a core that is stalling or reached hw barroer
      if sim.states[core].stall or sim.states[core].stop:
        scheduled_list.append( core )

    # NOTE: Need to check this again
    # if all thread are stalled then skip the analysis
    if len( scheduled_list ) == sim.ncores:
      return

    #---------------------------------------------------------------------
    # No reconvergence
    #---------------------------------------------------------------------

    if sim.reconvergence == 0:
      next_pc = 0
      next_core = 0
      # round-robin for given port bandwidth
      for i in xrange( sim.inst_ports ):

        for x in xrange( sim.ncores ):
          s.top_priority = 0 if s.top_priority == sim.ncores-1 else s.top_priority+1
          if not s.top_priority in scheduled_list:
            next_pc = sim.states[s.top_priority].pc
            next_core = s.top_priority
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
        for core in xrange( sim.ncores ):

          # select matching pcs
          if sim.states[core].pc == next_pc and not( sim.states[core].stop or sim.states[core].stall ):
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

          # NOTE: do not modify a core that has hit a hw barrier or has been stalling
          elif core not in scheduled_list:
            sim.states[core].active = False

        # early exit: all cores are scheduled
        if len( scheduled_list ) == sim.ncores:
          break

    #---------------------------------------------------------------------
    # Round-Robin + Min-PC hybrid reconvergence
    #---------------------------------------------------------------------
    # FIXME: Add instruction port modeling

    elif sim.reconvergence == 1:

      for port in xrange( sim.inst_ports ):
        min_core = 0
        min_pc   = sys.maxint

        # Select the minimum-pc by considering only active cores
        if s.switch_interval == 0:
          for core in xrange( sim.ncores ):
            if sim.states[core].pc < min_pc and core not in scheduled_list:
              min_pc = sim.states[core].pc
              min_core = core
          s.switch_interval = sim.ncores + 1

        # Round-robin arbitration
        else:
          for x in xrange( sim.ncores ):
            s.top_priority = 0 if s.top_priority == sim.ncores-1 else s.top_priority+1
            if not s.top_priority in scheduled_list:
              min_pc = sim.states[s.top_priority].pc
              min_core = s.top_priority
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
        for core in xrange( sim.ncores ):

          # advance pcs that match the min-pc and make sure to not activate
          # cores that have reached the barrier
          if sim.states[core].pc == min_pc and not( sim.states[core].stop or sim.states[core].stall ):
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

          # NOTE: do not modify a core that has hit a hw barrier or has been stalling
          elif core not in scheduled_list:
            sim.states[core].active = False

        s.switch_interval -= 1

        # early exit: all cores are scheduled
        if len( scheduled_list ) == sim.ncores:
          break

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
      if sim.states[core].active and not sim.states[core].clear:
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
      if s.lockstep:
        s.evaluate_pcs( sim )

      for i in xrange( s.num_ports ):
        grant = s.get_grant()
        if s.valid[ grant ]:
          if s.lockstep:
            sim.states[grant].clear = True
            s.valid[grant] = False
            s.pc_dict[ sim.states[0].pc ] -= 1
            if s.pc_dict[ sim.states[0].pc ] == 0:
              for core in xrange( sim.ncores ):
                sim.states[core].clear = False
                sim.states[core].stall = False
                if s.mdu: sim.states[core].mdu = False
                else:     sim.states[core].fpu = False
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

  def __init__( s, line_sz ):
    s.valid        = []        # valid requests
    s.num_reqs     = 0         # number of requests
    s.reqs         = []        # requests list
    s.fifo         = []        # fifo to clear requests
    s.table        = {}        # key-value map, key = coalesced request, value = list of ports that coalesce
    s.num_ports    = 0         # port bandwidth
    s.lockstep     = False     # flag to enforce lockstep execution
    s.pc_dict      = {}        # data-structure used to enforce lockstep execution
    s.top_priority = 0         # priority for aribitration
    # mask bits
    mask_bits = ~( line_sz - 1 )
    s.mask = mask_bits & 0xFFFFFFFF

  #-----------------------------------------------------------------------
  # configure
  #-----------------------------------------------------------------------

  def configure( s, num_reqs, num_ports, lockstep ):
    s.valid     = [False]*num_reqs
    s.reqs      = [None]*num_reqs
    s.num_reqs  = num_reqs
    s.num_ports = num_ports
    s.lockstep  = lockstep

  #-----------------------------------------------------------------------
  # set_request
  #-----------------------------------------------------------------------

  def set_request( s, idx, req ):
    s.valid[ idx ] = True
    s.reqs[ idx ]  = req

  #-----------------------------------------------------------------------
  # evaluate_pcs
  #-----------------------------------------------------------------------
  # evaluates all pcs and figures out the groups

  def evaluate_pcs( s, sim ):
    s.pc_dict = {}

    for core in xrange( sim.ncores ):
      if sim.states[core].active and not sim.states[core].clear:
        s.pc_dict[sim.states[core].pc] = s.pc_dict.get(sim.states[core].pc, 0) + 1

  #-----------------------------------------------------------------------
  # coalesce
  #-----------------------------------------------------------------------

  def coalesce( s ):
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
          # NOTE: coalesce only for loads
          if entry.type_ == 0 and entry.addr == key.addr:
            s.table[key].append( next_port )
            match = True

        if not match:
          s.table[entry] = [ next_port ]
          s.fifo.append( entry )
        s.valid[next_port] = False
      s.top_priority = 0 if s.top_priority == s.num_reqs-1 else s.top_priority+1

  #-----------------------------------------------------------------------
  # drain
  #-----------------------------------------------------------------------

  def drain( s, sim ):

    if len( s.fifo ) and s.lockstep:
      s.evaluate_pcs( sim )

    for i in xrange( s.num_ports ):
      if len( s.fifo ):
        entry = s.fifo.pop( 0 )
        ports = s.table.pop( entry )

        if s.lockstep:
          for p in ports:
            pc = sim.states[p].pc
            s.pc_dict[ pc ] -= 1
            sim.states[p].clear = True
            if s.pc_dict[pc] == 0:
              for core in xrange( sim.ncores ):
                if sim.states[core].pc == pc:
                  sim.states[core].stall = False
                  sim.states[core].dmem  = False
                  sim.states[core].clear = False
        else:
          for p in ports:
            sim.states[p].stall = False
            sim.states[p].dmem  = False

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
      s.coalesce()

    s.drain(sim)
