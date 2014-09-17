#=======================================================================
# utils.py
#=======================================================================

from rpython.rlib.rstruct     import ieee
from rpython.rlib.rarithmetic import intmask

#-----------------------------------------------------------------------
# sext
#-----------------------------------------------------------------------
# Sign extend 16-bit immediate fields.
def sext( value ):
  if value & 0x8000:
    return 0xFFFF0000 | value
  return value

#-----------------------------------------------------------------------
# sext_byte
#-----------------------------------------------------------------------
# Sign extend 8-bit immediate fields.
def sext_byte( value ):
  if value & 0x80:
    return 0xFFFFFF00 | value
  return value

#-----------------------------------------------------------------------
# signed
#-----------------------------------------------------------------------
def signed( value ):
  if value & 0x80000000:
    twos_complement = ~value + 1
    return -trim( twos_complement )
  return value

#-----------------------------------------------------------------------
# bits2float
#-----------------------------------------------------------------------
def bits2float( bits ):
  #data_str = struct.pack  ( 'I', bits     )
  #flt      = struct.unpack( 'f', data_str )[0]

  flt = ieee.float_unpack( bits, 4 )
  return flt

#-----------------------------------------------------------------------
# float2bits
#-----------------------------------------------------------------------
def float2bits( flt ):
  #data_str = struct.pack  ( 'f', flt      )
  #bits     = struct.unpack( 'I', data_str )[0]

  # float_pack returns an r_int rather than an int, must cast it or
  # arithmetic operations behave differently!
  try:
    bits = trim( intmask( ieee.float_pack( flt, 4 ) ) )
  # float_pack also will throw an OverflowError if the computed value
  # won't fit in the expected number of bytes, catch this and return
  # the encoding for inf/-inf
  except OverflowError:
    bits = 0x7f800000 if flt > 0 else 0xff800000

  return bits

#-----------------------------------------------------------------------
# trim
#-----------------------------------------------------------------------
# Trim arithmetic to 16-bit values.
def trim( value ):
  return value & 0xFFFFFFFF

#-----------------------------------------------------------------------
# trim_5
#-----------------------------------------------------------------------
# Trim arithmetic to 5-bit values.
def trim_5( value ):
  return value & 0b11111

