#!/usr/bin/python

from collections import OrderedDict

class PageTable:
  # Constructor for the class.
  # The default page table size is 8
  def __init__(self, table_size = 8):
    self.hits          = 0
    self.misses        = 0
    self.tlb           = None
    self.pg_table_size = table_size

  #Routine to mask the LSB bits
  def mask_lsb(self, value):
    return ((value & 0xFFFFFC00) >> 10)

  def populate_table( self, key ):
    self.tlb = OrderedDict()
    for i in xrange( key, key + self.pg_table_size ):
      # the value of the tlb dict isn't used
      self.tlb[i] = key

  def tlb_lookup( self, addr ):
    searchkey = self.mask_lsb( addr )

    if self.tlb is None:
      self.populate_table( searchkey )
      self.misses += 1
    elif searchkey not in self.tlb:
      # since the tlb is an ordered dict, we can just pop an entry in fifo
      # order and add the new entry
      #self.tlb.popitem( last=False )
      # NOTE: popitem using the last isn't rpython, so using keys to get
      # the FIFO order
      delete_key = self.tlb.keys()[0]
      del self.tlb[ delete_key ]
      self.tlb[ searchkey ] = searchkey
      self.misses += 1
    else:
      self.hits += 1

def main():
  sample_table = PageTable(8)
  sample_table.tlb_lookup(0x00222220)
  sample_table.tlb_lookup(0x00222221)
  sample_table.tlb_lookup(0x10000020)
  sample_table.tlb_lookup(0x023445020)
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
  print "Hits=" + str(sample_table.hits)
  print "Misses=" + str(sample_table.misses)

if __name__ == "__main__":
  main()

