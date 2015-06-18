#=======================================================================
# utils.py
#=======================================================================
# General-purpose bitwise operation utilities.

try:
  from rpython.rlib.rarithmetic import r_uint, intmask, r_ulonglong
  from rpython.rlib.objectmodel import specialize
except ImportError:
  r_uint = lambda x : x
  r_ulonglong = lambda x : x
  intmask = lambda x : x
  class Specialize:
    def argtype( self, fun, *args ):
      return lambda fun : fun
  specialize = Specialize()

#-----------------------------------------------------------------------
# sext_16
#-----------------------------------------------------------------------
# Sign extend 16-bit value.
def sext_16( value ):
  if value & 0x8000:
    return r_uint( 0xFFFF0000 ) | value
  return value

#-----------------------------------------------------------------------
# sext_8
#-----------------------------------------------------------------------
# Sign extend 8-bit value
def sext_8( value ):
  if value & 0x80:
    return r_uint( 0xFFFFFF00 ) | value
  return value

#-----------------------------------------------------------------------
# signed
#-----------------------------------------------------------------------
def signed( value ):
  if value & r_uint( 0x80000000 ):
    twos_complement = ~value + 1
    return -intmask( trim_32( twos_complement ) )
  return intmask( value )


#-----------------------------------------------------------------------
# trim_32
#-----------------------------------------------------------------------
# Trim arithmetic to 32-bit values.
@specialize.argtype(0)
def trim_32( value ):
  value = r_uint( value )
  return value & r_uint( 0xFFFFFFFF )

#-----------------------------------------------------------------------
# trim_16
#-----------------------------------------------------------------------
def trim_16( value ):
  return value & 0xFFFF

#-----------------------------------------------------------------------
# trim_8
#-----------------------------------------------------------------------
def trim_8( value ):
  return value & 0xFF

try:
  # use efficient rpython int/float conversion only if rpython is in path

  from rpython.rlib.rarithmetic import r_uint32, widen
  from rpython.rlib.longlong2float import uint2singlefloat, \
                                          singlefloat2uint
  from rpython.rtyper.lltypesystem import lltype, rffi

  #---------------------------------------------------------------------
  # bits2float
  #---------------------------------------------------------------------
  def bits2float( bits ):

    # This is a bit convoluted, but this is much faster than ieee.pack
    # stuff. In addition to normal casting through uint2singlefloat, we have
    # additional casting because integer and float types that we can do
    # arithmetic operations on are standard Python sizes (native machine
    # size). Here's the typing going on below:
    # Python Int (64-bit) -> r_uint32 -> r_singlefloat -> Python Float (64-bit)
    flt = rffi.cast( lltype.Float, uint2singlefloat( r_uint32( bits ) ) )
    return flt

  #---------------------------------------------------------------------
  # float2bits
  #---------------------------------------------------------------------
  def float2bits( flt ):

    # See note above for bits2float. We're doing the reverse:
    # Python Float (64-bit) -> r_singlefloat -> r_uint32 -> Python Int (64-bit)
    bits = widen( singlefloat2uint( rffi.cast( lltype.SingleFloat, flt ) ) )
    return bits

except ImportError:
  # if rpython not in path, use structs to pack/unpack
  import struct

  #---------------------------------------------------------------------
  # bits2float
  #---------------------------------------------------------------------
  def bits2float( bits ):
    raw_data  = struct.pack( "I", bits )
    conv_data = struct.unpack( "f", raw_data )
    return conv_data[0]

  #---------------------------------------------------------------------
  # float2bits
  #---------------------------------------------------------------------
  def float2bits( flt ):
    raw_data  = struct.pack( "f", flt )
    conv_data = struct.unpack( "I", raw_data )
    return conv_data[0]
