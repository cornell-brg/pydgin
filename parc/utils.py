#=======================================================================
# utils.py
#=======================================================================

from rpython.rlib.rstruct     import ieee
from rpython.rlib.rarithmetic import intmask
from pydgin.machine           import RegisterFile

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

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  def __init__( self, memory, symtable, debug, reset_addr=0x400 ):
    self.pc       = reset_addr

    # TODO: to allow the register file to be virtualizable (to avoid array
    # lookups in the JIT), it needs to be an array as a member of the
    # State class. Couldn't figure out how to have rf a RegisterFile
    # object and still be virtualizable.
    self.rf       = RegisterFile()
    self.mem      = memory

    self.rf .debug = debug
    self.mem.debug = debug

    self.debug = debug

    # coprocessor registers
    self.status        = 0
    self.stats_en      = 0
    self.ncycles       = 0
    self.stat_ncycles  = 0

    # we need a dedicated running flag bacase status could be 0 on a
    # syscall_exit
    self.running       = True

    # parc special
    self.src_ptr  = 0
    self.sink_ptr = 0

    # syscall stuff... TODO: should this be here?
    self.breakpoint = 0

#-----------------------------------------------------------------------
# Instruction Fields
#-----------------------------------------------------------------------
def rd( inst ):
  return (inst >> 11) & 0x1F

def rt( inst ):
  return (inst >> 16) & 0x1F

def rs( inst ):
  return (inst >> 21) & 0x1F

def fd( inst ):
  return (inst >>  6) & 0x1F

def ft( inst ):
  return (inst >> 16) & 0x1F

def fs( inst ):
  return (inst >> 11) & 0x1F

def imm( inst ):
  return inst & 0xFFFF

def jtarg( inst ):
  return inst & 0x3FFFFFF

def shamt( inst ):
  return (inst >> 6) & 0x1F

