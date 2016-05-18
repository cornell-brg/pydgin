#!/usr/bin/python

#-----------------------------------------------------------------------------
# TLB Model with LRU Replacement Policy
#-----------------------------------------------------------------------------
# This file contains the R-python model for varying page table size and page
# table entry size with LRU replacement policy

from collections import OrderedDict

class PageTable:

  ##############################################################
  #  Constructor for the class
  ##############################################################
  # The constructor initializes the hits, miss varibale and also
  # a tlb dictionary with default page table entry size of 8 and 
  # page size as 8KB

  def __init__( self, table_size = 8 , page_size = 8):

    self.hits          = 0
    self.misses        = 0
    self.tlb           = None
    self.pg_table_size = table_size
    self.pg_page_size  = page_size

  ##############################################################
  # Routine to mask the LSB bits
  ##############################################################
  # This function masks the input address with the page size
  # for searching the address in the page table in TLB

  def mask_lsb( self, value ):

    if ( self.pg_page_size == 8 ):
      new_addr = ( ( value & 0xFFFFE000 ) >> 13 )

    elif ( self.pg_page_size == 16 ):
      new_addr = ( ( value & 0xFFFFC000 ) >> 14 )

    elif ( self.pg_page_size == 32 ):
      new_addr = ( ( value & 0xFFFF8000 ) >> 15 )

    elif ( self.pg_page_size == 64 ):
      new_addr = ( ( value & 0xFFFF0000 ) >> 16 )

    elif ( self.pg_page_size == 128 ):
      new_addr = ( ( value & 0xFFFE0000 ) >> 17 )

    return new_addr

  ##############################################################
  #  Create the page table for TLB
  ##############################################################
  # This function actually initializes the page table for TLB
  # when there is a compulsory miss

  def populate_table( self, key ):

    self.tlb = OrderedDict()

    for x in range( 1, self.pg_table_size ):
      self.tlb.update( { key + x : 1 } )

  ##############################################################
  #  Update the page table in TLB
  ##############################################################
  # This function updates the TLB with new entry by replacing the
  # least used entry from the table

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

      #There is a hit and hence LRU value needs to be updated accordingly.
      lru_value = self.tlb[ searchkey ]
      lru_value = lru_value + 1
      del self.tlb[ searchkey ]
      self.tlb.update( { searchkey :  lru_value } )
      self.hits += 1

    return

#-----------------------------------------------------------------------
#  Main function
#-----------------------------------------------------------------------
# Main function with few sample address is written to test the working of
# modeled TLB before integrating in pydgin

def main():
  sample_table = PageTable(8,64)
  sample_table.tlb_lookup(0x00222220)
  sample_table.tlb_lookup(0x00222221)
  sample_table.tlb_lookup(0x10000020)
  sample_table.tlb_lookup(0x02344502)
  sample_table.tlb_lookup(0x00222220)
  sample_table.tlb_lookup(0x00222221)
  sample_table.tlb_lookup(0x00002221)
  sample_table.tlb_lookup(0x00000201)
  sample_table.tlb_lookup(0x00100201)
  sample_table.tlb_lookup(0x00100001)
  sample_table.tlb_lookup(0x00002221)
  sample_table.tlb_lookup(0x00002221)
  sample_table.tlb_lookup(0x00000221)
  sample_table.tlb_lookup(0x20000221)
  sample_table.tlb_lookup(0x22000221)
  sample_table.tlb_lookup(0x20030221)
  sample_table.tlb_lookup(0x22040221)
  print "Hits=" + str( sample_table.hits )
  print "Misses=" + str( sample_table.misses )
    
if __name__ == "__main__":
  main()

