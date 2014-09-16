# trace elidable for instruction reads
from rpython.rlib.jit         import elidable, unroll_safe
from rpython.rlib.rstruct     import ieee
from rpython.rlib.rarithmetic import intmask

#-------------------------------------------------------------------------
# Debug
#-------------------------------------------------------------------------
# a class that contains different debug flags

class Debug( object ):

  # NOTE: it doesn't seem possible to have conditional debug prints
  # without incurring performance losses. So, instead we are specializing
  # the binary in translation time. This class variable will be set true
  # in translation time only if debugging is enabled. Otherwise, the
  # translator can optimize away the enabled call below

  global_enabled = False

  def __init__( self ):
    self.enabled_flags = [ ]

  #-----------------------------------------------------------------------
  # enabled
  #-----------------------------------------------------------------------
  # Returns true if debugging is turned on in translation and the
  # particular flag is turned on in command line.

  @elidable
  def enabled( self, flag ):
    return Debug.global_enabled and ( flag in self.enabled_flags )

  #-----------------------------------------------------------------------
  # set_flags
  #-----------------------------------------------------------------------
  # go through the flags and set them appropriately

  def set_flags( self, flags ):
    self.enabled_flags = flags

#-------------------------------------------------------------------------
# pad
#-------------------------------------------------------------------------
# add padding to string

def pad( str, nchars, pad_char=" ", pad_end=True ):
  pad_str = ( nchars - len( str ) ) * pad_char
  out_str = str + pad_str if pad_end else pad_str + str
  return out_str

#-------------------------------------------------------------------------
# pad_hex
#-------------------------------------------------------------------------
# easier-to-use padding function for hex values

def pad_hex( hex_val, len=8 ):
  return pad( "%x" % hex_val, len, "0", False )

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
class RegisterFile( object ):
  def __init__( self ):
    self.regs  = [0] * 32
    self.debug = Debug()
  def __getitem__( self, idx ):
    if self.debug.enabled( "rf" ):
      print ':: RD.RF[%s] = %s' % (
                          pad( "%d" % idx, 2 ),
                          pad_hex( self.regs[idx]) ),
    return self.regs[idx]
  def __setitem__( self, idx, value ):
    if idx != 0:
      self.regs[idx] = value
      if self.debug.enabled( "rf" ):
        print ':: WR.RF[%s] = %s' % (
                          pad( "%d" % idx, 2 ),
                          pad_hex( self.regs[idx] ) ),

  #-----------------------------------------------------------------------
  # print_regs
  #-----------------------------------------------------------------------
  # prints all registers (register dump)

  def print_regs( self ):
    num_regs = 32
    per_row  = 6
    for c in xrange( 0, num_regs, per_row ):
      str = ""
      for r in xrange( c, min( num_regs, c+per_row ) ):
        str += "%s:%s " % ( pad( "%d" % r, 2 ),
                            pad_hex( self.regs[r] ) )
      print str

#-------------------------------------------------------------------------
# WordMemory
#-------------------------------------------------------------------------
# Memory that uses ints instead of chars

class WordMemory( object ):
  def __init__( self, data=None, size=2**10 ):
    if not data:
      self.data = [0] * (size >> 2)
    else:
      self.data = data
    self.size = len( self.data ) >> 2

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
      return (self.data[ word ] & mask) >> (byte * 8)

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
      mask = ~(0xFFFF << (byte * 8)) & 0xFFFFFFFF
      self.data[ word ] = ( self.data[ word ] & mask ) | \
                          ( (value & 0xFFFF) << (byte * 8) )
    elif num_bytes == 1:
      mask = ~(0xFF   << (byte * 8)) & 0xFFFFFFFF
      self.data[ word ] = ( self.data[ word ] & mask ) | \
                          ( (value & 0xFF  ) << (byte * 8) )
    else:
      raise Exception('Not handled value for num_bytes')

#-----------------------------------------------------------------------
# Memory
#-----------------------------------------------------------------------
class Memory( object ):
  def __init__( self, data=None, size=2**10 ):
    if not data:
      self.data = [' '] * size
    else:
      self.data = data
    self.size = len( self.data )
    self.debug = Debug()

  def bounds_check( self, addr ):
    # check if the accessed data is larger than the memory size
    if addr > self.size:
      print "WARNING: accessing larger address than memory size. " + \
            "addr=%s size=%s" % ( pad_hex( addr ), pad_hex( self.size ) )

  @unroll_safe
  def read( self, start_addr, num_bytes ):
    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr )
    value = 0
    if self.debug.enabled( "mem" ):
      print ':: RD.MEM[%s] = ' % pad_hex( start_addr ),
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.data[ start_addr + i ] )
    if self.debug.enabled( "mem" ):
      print '%s' % pad_hex( value ),
    return value

  # this is instruction read, which is otherwise identical to read. The
  # only difference is the elidable annotation, which we assume the
  # instructions are not modified (no side effects, assumes the addresses
  # correspond to the same instructions)
  @elidable
  def iread( self, start_addr, num_bytes ):
    value = 0
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.data[ start_addr + i ] )
    return value

  @unroll_safe
  def write( self, start_addr, num_bytes, value ):
    if self.debug.enabled( "memcheck" ):
      self.bounds_check( start_addr )
    if self.debug.enabled( "mem" ):
      print ':: WR.MEM[%s] = %s' % ( pad_hex( start_addr ),
                                     pad_hex( value ) ),
    for i in range( num_bytes ):
      self.data[ start_addr + i ] = chr(value & 0xFF)
      value = value >> 8

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

