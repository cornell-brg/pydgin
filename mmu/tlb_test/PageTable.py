#!/usr/bin/python

#-----------------------------------------------------------------------------
# TLB Model with FIFO Replacement Policy
#-----------------------------------------------------------------------------
# This file contains the R-python model for varying page table size and page
# table entry size with FIFO replacement policy

from collections import OrderedDict

class PageTable_FIFO:

  ##############################################################
  #  Constructor for the class
  ##############################################################
  # The constructor initializes the hits, miss varibale and also
  # a tlb dictionary with default page table entry size of 8 

  def __init__( self, tlb_size = 8 , page_size = 8):

    self.hits          = 0
    self.misses        = 0
    self.tlb           = None
    self.pg_tlb_size   = tlb_size
    self.pg_page_size  = page_size

  ##############################################################
  # Routine to mask the LSB bits
  ##############################################################
  # This function masks the input address with the page table size
  # for searching the address in the page table in TLB

  def mask_lsb( self, value ):

    if ( self.pg_page_size == 8 ):
      return ( ( value & 0xFFFFE000 ) >> 13 )

    elif ( self.pg_page_size == 16 ):
      return ( ( value & 0xFFFFC000 ) >> 14 )

    elif ( self.pg_page_size == 32 ):
      return ( ( value & 0xFFFF8000 ) >> 15 )

    elif ( self.pg_page_size == 64 ):
      return ( ( value & 0xFFFF0000 ) >> 16 )

    elif ( self.pg_page_size == 128 ):
      return ( ( value & 0xFFFE0000 ) >> 17 )


  ##############################################################
  #  Create the page table for TLB
  ##############################################################
  # This function actually initializes the page table for TLB 
  # when there is a compulsory miss
 
  def populate_table( self, key ):
    self.tlb = OrderedDict()
 
    for i in xrange( key, key + self.pg_tlb_size ):
      # the value of the tlb dict isn't used
      self.tlb[i] = key + i

  ##############################################################
  #  Search the virtual address
  ##############################################################
  # This function search for the given virtual address for the
  # required translation but here only virtual address is stored

  def tlb_lookup( self, addr ):
    searchkey = self.mask_lsb( addr )

    if self.tlb is None:

      # For Compulsory Miss populate the full table
      self.populate_table( searchkey )
      self.misses += 1

    elif searchkey not in self.tlb:
      # since the tlb is an ordered dict, we can just pop an entry 
      # in fifo order and add the new entry
      # self.tlb.popitem( last=False )
      # NOTE: popitem using the last isn't rpython, so using keys 
      # to get the FIFO order

      # Delete the first entry in the table
      delete_key = self.tlb.keys()[0]
      del self.tlb[ delete_key ]
 
      # Update the new entry
      self.tlb[ searchkey ] = searchkey
      self.misses += 1

    else:

      self.hits += 1

#-----------------------------------------------------------------------------
# TLB Model with LFU Replacement Policy
#-----------------------------------------------------------------------------
# This file contains the R-python model for varying page table size and page
# table entry size with LRU replacement policy

class PageTable_LFU:

  ##############################################################
  #  Constructor for the class
  ##############################################################
  # The constructor initializes the hits, miss varibale and also
  # a tlb dictionary with default page table entry size of 8 and 
  # page size as 8KB

  def __init__( self, tlb_size = 8 , page_size = 8):

    self.hits          = 0
    self.misses        = 0
    self.tlb           = None
    self.pg_tlb_size   = tlb_size
    self.pg_page_size  = page_size

  ##############################################################
  # Routine to mask the LSB bits
  ##############################################################
  # This function masks the input address with the page size
  # for searching the address in the page table in TLB

  def mask_lsb( self, value ):

    if ( self.pg_page_size == 8 ):
      return ( ( value & 0xFFFFE000 ) >> 13 )

    elif ( self.pg_page_size == 16 ):
      return ( ( value & 0xFFFFC000 ) >> 14 )

    elif ( self.pg_page_size == 32 ):
      return ( ( value & 0xFFFF8000 ) >> 15 )

    elif ( self.pg_page_size == 64 ):
      return ( ( value & 0xFFFF0000 ) >> 16 )

    elif ( self.pg_page_size == 128 ):
      return ( ( value & 0xFFFE0000 ) >> 17 )


  ##############################################################
  #  Create the page table for TLB
  ##############################################################
  # This function actually initializes the page table for TLB
  # when there is a compulsory miss

  def populate_table( self, key ):

    self.tlb = OrderedDict()

    for x in range( 1, self.pg_tlb_size ):
      self.tlb.update( { key + x : 1 } )

  ##############################################################
  #  Update the page table in TLB
  ##############################################################
  # This function updates the TLB with new entry by replacing the
  # least frequently used entry from the table

  def update_table( self, key ):

    stale_key = self.tlb.keys()[0]
    old_index = self.tlb[ stale_key ]
    highest_index = old_index

    for delete_key in self.tlb.keys():
      if ( self.tlb[ delete_key ] < old_index ):
        stale_key = delete_key
        old_index = self.tlb[ delete_key ]

    del self.tlb[ stale_key ] 
    self.tlb.update( { key : 1 } )

    return

  ##############################################################
  #  Search the virtual address
  ##############################################################
  # This function search for the given virtual address for the
  # required translation but here only virtual address is stored

  def tlb_lookup( self, addr ):

    searchkey = self.mask_lsb( addr )

    #First time, hash will be empty, so returns an empty list
    if self.tlb is None:

      self.misses += 1
      self.populate_table( searchkey )

      return

    elif searchkey not in self.tlb:

      #Update the page table now using LRU
      self.update_table( searchkey ) 
      self.misses += 1

    else:

      #There is a hit and hence LFU value needs to be updated accordingly.
      lfu_value = self.tlb[ searchkey ]
      lfu_value = lfu_value + 1
      del self.tlb[ searchkey ]
      self.tlb.update( { searchkey :  lfu_value } )
      self.hits += 1

    return

