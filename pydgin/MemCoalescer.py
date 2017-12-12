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

  def __init__( s, line_sz ):
    s.valid     = []  # valid requests
    s.num_reqs  = 0   # number of requests
    s.reqs      = []  # requests list
    s.fifo      = []  # fifo to clear requests
    s.table     = {}  # key-value map, key = coalesced request, value = list of ports that coalesce
    s.num_ports = 0   # port bandwidth
    # mask bits
    mask_bits = ~( line_sz - 1 )
    s.mask = mask_bits & 0xFFFFFFFF

  def configure( s, num_reqs, num_ports ):
    s.valid     = [False]*num_reqs
    s.reqs      = [None]*num_reqs
    s.num_reqs  = num_reqs
    s.num_ports = num_ports

  def set_request( s, idx, req ):
    s.valid[ idx ] = True
    s.reqs[ idx ]  = req

  def coalesce( s ):
    for i in range( s.num_reqs ):
      if s.valid[i]:
        # check the line that will be requested
        line_addr = s.reqs[i].addr & s.mask

        # temp entry
        entry       = MemRequest()
        entry.type_ = s.reqs[i].type_
        entry.len_  = 0
        entry.addr  = line_addr

        match = False
        for key in s.table.keys():
          # NOTE: coalesce only for loads
          if entry.type_ == 0 and entry.addr == key.addr:
            s.table[key].append( i )
            match = True

        if not match:
          s.table[entry] = [ i ]
          s.fifo.append( entry )
        s.valid[i] = False

  def drain( s, sim ):
    for i in range( s.num_ports ):
      if len( s.fifo ):
        entry = s.fifo.pop( 0 )
        ports = s.table.pop( entry )
        for p in ports:
          sim.states[p].stall = False

  def xtick( s, sim ):
    s.coalesce()
    s.drain(sim)
