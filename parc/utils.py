# trace elidable for instruction reads
from rpython.rlib.jit import elidable, unroll_safe

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
# register_inst
#-----------------------------------------------------------------------
# Utility decorator for building decode table.
def register_inst( func ):
  prefix, suffix = func.func_name.split('_')
  assert prefix == 'execute'
  decode_table[ suffix ] = func
  return func

#-----------------------------------------------------------------------
# RegisterFile
#-----------------------------------------------------------------------
#class RegisterFile( object ):
#  def __init__( self ):
#    self.regs = [0] * 32
#  def __getitem__( self, idx ):
#    return self.regs[idx]
#  def __setitem__( self, idx, value ):
#    if idx != 0:
#      self.regs[idx] = value

#-----------------------------------------------------------------------
# Memory
#-----------------------------------------------------------------------
class Memory( object ):
  def __init__( self, data=None ):
    if not data:
      self.data = [0]*2**10
    else:
      self.data = data

  @unroll_safe
  def read( self, start_addr, num_bytes ):
    assert 0 < num_bytes <= 4
    word = start_addr >> 2
    byte = start_addr &  0b11

    if   num_bytes == 4:  # TODO: byte should only be 0 (only aligned)
      return self.data[ word ]
    elif num_bytes == 2:  # TODO: byte should only be 0, 1, 2, not 3
      mask = 0xFFFF << (byte * 8)
      return (self.data[ word ] & mask) >> (byte * 8)
    elif num_bytes == 1:
      mask = 0xFF   << (byte * 8)
      return (self.data[ word ] & mask) >> (byte * 4)

    raise Exception('Not handled value for num_bytes')

  # this is instruction read, which is otherwise identical to read. The
  # only difference is the elidable annotation, which we assume the
  # instructions are not modified (no side effects, assumes the addresses
  # correspond to the same instructions)
  @elidable
  @unroll_safe
  def iread( self, start_addr, num_bytes ):
    assert start_addr & 0b11 == 0  # only aligned accesses allowed
    return self.data[ start_addr >> 2 ]

  @unroll_safe
  def write( self, start_addr, num_bytes, value ):
    assert 0 < num_bytes <= 4
    word = start_addr >> 2
    byte = start_addr &  0b11

    if   num_bytes == 4:  # TODO: byte should only be 0 (only aligned)
      self.data[ word ] = value
    elif num_bytes == 2:  # TODO: byte should only be 0, 1, 2, not 3
      mask = ~((0xFFFF << (byte * 8)) & 0xFFFFFFFF) & 0xFFFFFFFF
      self.data[ word ] |= (value << (byte * 8 ))
    elif num_bytes == 1:
      mask = ~((0xFF   << (byte * 8)) & 0xFFFFFFFF) & 0xFFFFFFFF
      self.data[ word ] |= (value << (byte * 8 ))
    else:
      raise Exception('Not handled value for num_bytes')

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  _virtualizable_ = [ 'rf[*]' ]
  def __init__( self, memory, symtable, reset_addr=0x400 ):
    self.src_ptr  = 0
    self.sink_ptr = 0
    self.pc       = reset_addr

    # TODO: to allow the register file to be virtualizable (to avoid array
    # lookups in the JIT), it needs to be an array as a member of the
    # State class. Couldn't figure out how to have rf a RegisterFile
    # object and still be virtualizable.
    #self.rf       = RegisterFile()
    self.rf       = [0] * 32
    self.mem      = memory
    self.symtable = symtable
    self.status   = 0
    self.stat_en  = 0

#-----------------------------------------------------------------------
# Instruction Fields
#-----------------------------------------------------------------------
def rd( inst ):
  return (inst >> 11) & 0x1F

def rt( inst ):
  return (inst >> 16) & 0x1F

def rs( inst ):
  return (inst >> 21) & 0x1F

def imm( inst ):
  return inst & 0xFFFF

def jtarg( inst ):
  return inst & 0x3FFFFFF

def shamt( inst ):
  return (inst >> 6) & 0x1F
