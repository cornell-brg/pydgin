#=======================================================================
# utils.py
#=======================================================================
# General-purpose bitwise operation utilities.

from rpython.rlib.rarithmetic import r_uint32, widen
from rpython.rlib.longlong2float import uint2singlefloat, \
                                        singlefloat2uint
from rpython.rtyper.lltypesystem import lltype, rffi

#-----------------------------------------------------------------------
# sext_16
#-----------------------------------------------------------------------
# Sign extend 16-bit value.
def sext_16( value ):
  if value & 0x8000:
    return 0xFFFF0000 | value
  return value

#-----------------------------------------------------------------------
# sext_8
#-----------------------------------------------------------------------
# Sign extend 8-bit value
def sext_8( value ):
  if value & 0x80:
    return 0xFFFFFF00 | value
  return value

#-----------------------------------------------------------------------
# signed
#-----------------------------------------------------------------------
def signed( value ):
  if value & 0x80000000:
    twos_complement = ~value + 1
    return -trim_32( twos_complement )
  return value

#-----------------------------------------------------------------------
# bits2float
#-----------------------------------------------------------------------
def bits2float( bits ):

  # This is a bit convoluted, but this is much faster than ieee.pack
  # stuff. In addition to normal casting through uint2singlefloat, we have
  # additional casting because integer and float types that we can do
  # arithmetic operations on are standard Python sizes (native machine
  # size). Here's the typing going on below:
  # Python Int (64-bit) -> r_uint32 -> r_singlefloat -> Python Float (64-bit)
  flt = rffi.cast( lltype.Float, uint2singlefloat( r_uint32( bits ) ) )
  return flt

#-----------------------------------------------------------------------
# float2bits
#-----------------------------------------------------------------------
def float2bits( flt ):

  # See note above for bits2float. We're doing the reverse:
  # Python Float (64-bit) -> r_singlefloat -> r_uint32 -> Python Int (64-bit)
  bits = widen( singlefloat2uint( rffi.cast( lltype.SingleFloat, flt ) ) )
  return bits

#-----------------------------------------------------------------------
# trim
#-----------------------------------------------------------------------
# Trim arithmetic to 32-bit values.
def trim_32( value ):
  return value & 0xFFFFFFFF


