

def signed( value, nbits ):
  mask = 0x1 << (nbits - 1)
  if value & mask:
    twos_complement = ~value + 1
    return -trim_64( twos_complement )

def trim_64( value ):
  return value & 0xffffffffffffffff

