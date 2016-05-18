#!/usr/bin/python

#-----------------------------------------------------------------------------
# TLB Model with FIFO Replacement Policy
#-----------------------------------------------------------------------------
# This file contains the R-python model for varying page table size and page
# table entry size with FIFO replacement policy

from collections import OrderedDict

class PageTable:

  ##############################################################
  #  Constructor for the class
  ##############################################################
  # The constructor initializes the hits, miss varibale and also
  # a tlb dictionary with default page table entry size of 8 

  def __init__( self, table_size = 64 ):

    self.hits          = 0
    self.misses        = 0
    self.tlb           = None
    self.pg_table_size = table_size

  ##############################################################
  # Routine to mask the LSB bits
  ##############################################################
  # This function masks the input address with the page table size
  # for searching the address in the page table in TLB

  def mask_lsb( self, value ):
    return ( ( value & 0xFFFF8000 ) >> 15 )

  ##############################################################
  #  Create the page table for TLB
  ##############################################################
  # This function actually initializes the page table for TLB 
  # when there is a compulsory miss
 
  def populate_table( self, key ):
    self.tlb = OrderedDict()
 
    for i in xrange( key, key + self.pg_table_size ):
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

#-----------------------------------------------------------------------
#  Main function
#-----------------------------------------------------------------------
# Main function with few sample address is written to test the working of 
# modeled TLB before integrating in pydgin

def main():
  sample_table = PageTable(64)
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

