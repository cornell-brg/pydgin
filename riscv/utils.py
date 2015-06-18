
from pydgin.utils import intmask, r_ulonglong, specialize

def signed( value, nbits ):
  mask = 0x1 << (nbits - 1)
  value = trim( value, nbits )
  if value & mask:
    twos_complement = ~value + 1
    return -intmask( trim( twos_complement, nbits ) )
  return intmask( value )

@specialize.argtype(0)
def trim( value, nbits ):
  value = r_ulonglong( value )
  mask = r_ulonglong( 0xffffffffffffffff ) >> (64 - nbits)
  return value & mask

@specialize.argtype(0)
def trim_64( value ):
  value = r_ulonglong( value )
  return value & r_ulonglong( 0xffffffffffffffff )

@specialize.argtype(0)
def sext_32( value ):
  value = r_ulonglong( value )
  value = 0x00000000ffffffff & value
  if value & 0x80000000:
    return r_ulonglong( 0xffffffff00000000 ) | value
  return value

def sext( value, nbits ):
  value = trim( value, nbits )
  sign_mask = 0x1 << (nbits - 1)
  mask = trim_64( r_ulonglong( 0xffffffffffffff ) << nbits )
  if value & sign_mask:
    return mask | value
  return value
