#=========================================================================
# PageTable_test
#=========================================================================
# Test suite for the TLB model with FIFO

from pymtl            import *
from tlb.PageTable    import PageTable_FIFO
from tlb.PageTable    import PageTable_LRU
from tlb.PageTable    import PageTable_LFU


def test_basic_fifo():

  # Create a page table

  sample_table = PageTable_FIFO(8,64)

  # Unit test case

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

  # Verify results

  assert sample_table.hits == 7
  assert sample_table.misses == 10

def test_basic_lru():

  # Create a page table

  sample_table = PageTable_LRU(8,64)

  # Unit test case

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

  # Verify results

  assert sample_table.hits == 6
  assert sample_table.misses == 11

def test_basic_lfu():

  # Create a page table

  sample_table = PageTable_LFU(8,64)

  # Unit test case

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

  # Verify results

  assert sample_table.hits == 7
  assert sample_table.misses == 10

