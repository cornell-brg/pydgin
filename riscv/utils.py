

def signed( value, nbits ):
  mask = 0x1 << (nbits - 1)
  if value & mask:
    twos_complement = ~value + 1
    return -trim_64( twos_complement )
  return value

def trim_64( value ):
  return value & 0xffffffffffffffff

def sext_32( value ):
  if value & 0x80000000:
    return 0xffffffff00000000 | value
  return value

def sext( value, nbits ):
  sign_mask = 0x1 << (nbits - 1)
  mask = trim_64( 0xffffffffffffff << nbits )
  if value & sign_mask:
    return mask | value
  return value
