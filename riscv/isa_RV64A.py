#=======================================================================
# isa_RV64A.py
#=======================================================================
'RISC-V instructions for the atomic instructions extension.'

from utils        import sext_xlen, sext_32, sext, signed, trim
from pydgin.utils import trim_32
from helpers      import *

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [

  ['lr_d',               '00010xx00000xxxxx011xxxxx0101111'],
  ['sc_d',               '00011xxxxxxxxxxxx011xxxxx0101111'],
  ['amoswap_d',          '00001xxxxxxxxxxxx011xxxxx0101111'],
  ['amoadd_d',           '00000xxxxxxxxxxxx011xxxxx0101111'],
  ['amoxor_d',           '00100xxxxxxxxxxxx011xxxxx0101111'],
  ['amoor_d',            '01000xxxxxxxxxxxx011xxxxx0101111'],
  ['amoand_d',           '01100xxxxxxxxxxxx011xxxxx0101111'],
  ['amomin_d',           '10000xxxxxxxxxxxx011xxxxx0101111'],
  ['amomax_d',           '10100xxxxxxxxxxxx011xxxxx0101111'],
  ['amominu_d',          '11000xxxxxxxxxxxx011xxxxx0101111'],
  ['amomaxu_d',          '11100xxxxxxxxxxxx011xxxxx0101111'],

]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_lr_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sc_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoswap_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amoadd_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = value + s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amoxor_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = value ^ s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amoor_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = value | s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amoand_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = value & s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amomin_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = min( signed(value, 64), signed(s.rf[inst.rs2], 64) )
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amomax_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = max( signed(value, 64), signed(s.rf[inst.rs2], 64) )
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amominu_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = min( value, s.rf[inst.rs2] )
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amomaxu_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = max( value, s.rf[inst.rs2] )
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

