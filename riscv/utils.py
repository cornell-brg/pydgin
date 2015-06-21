
from pydgin.utils import intmask, r_ulonglong, specialize, trim_32

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
def sext_xlen( val ):
  return val

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

def multhi64( a, b ):
  # returns the high 64 bits of 64 bit multiplication
  # using this trick to get the high bits of 64-bit multiplication:
  # http://stackoverflow.com/questions/28868367/getting-the-high-part-of-64-bit-integer-multiplication
  a_hi, a_lo = trim_32(a >> 32), trim_32(a)
  b_hi, b_lo = trim_32(b >> 32), trim_32(b)

  a_x_b_hi =  a_hi * b_hi
  a_x_b_mid = a_hi * b_lo
  b_x_a_mid = b_hi * a_lo
  a_x_b_lo =  a_lo * b_lo

  carry_bit = ( trim_32( a_x_b_mid ) + trim_32( b_x_a_mid ) +
                (a_x_b_lo >> 32) ) >> 32

  return a_x_b_hi + (a_x_b_mid >> 32) + (b_x_a_mid >> 32) + carry_bit

def fp_neg( value, nbits ):
  sign_mask = 1 << (nbits - 1)
  return sign_mask ^ value
