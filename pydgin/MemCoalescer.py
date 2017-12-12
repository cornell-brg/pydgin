#=========================================================================
# MemCoalescer.py
#=========================================================================
# Author : Shreesha Srinath
# Date   : December 11th, 2017
#
# MemCoalescer class models a memory coalescing unit which accepts incoming
# memory requests and creates coalesced requests

import math

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
# NOTE: Need to check fairness?

class MemCoalescer():

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s, line_sz ):
    s.valid     = []  # valid requests
    s.num_reqs  = 0   # number of requests
    s.reqs      = []  # requests list
    s.fifo      = []  # fifo to clear requests
    s.table     = {}  # key-value map, key = coalesced request, value = list of ports that coalesce
    s.num_ports = 0   # port bandwidth
    s.top_priority = 0
    # mask bits
    mask_bits = ~( line_sz - 1 )
    s.mask = mask_bits & 0xFFFFFFFF

  #-----------------------------------------------------------------------
  # configure
  #-----------------------------------------------------------------------

  def configure( s, num_reqs, num_ports ):
    s.valid     = [False]*num_reqs
    s.reqs      = [None]*num_reqs
    s.num_reqs  = num_reqs
    s.num_ports = num_ports

  #-----------------------------------------------------------------------
  # set_request
  #-----------------------------------------------------------------------

  def set_request( s, idx, req ):
    s.valid[ idx ] = True
    s.reqs[ idx ]  = req

  #-----------------------------------------------------------------------
  # caolesce
  #-----------------------------------------------------------------------

  def coalesce( s ):
    for i in range( s.num_reqs ):
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
    for i in range( s.num_ports ):
      if len( s.fifo ):
        entry = s.fifo.pop( 0 )
        ports = s.table.pop( entry )
        for p in ports:
          sim.states[p].stall = False
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
