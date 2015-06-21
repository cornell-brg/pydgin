#=======================================================================
# isa_RV32A.py
#=======================================================================
'RISC-V instructions for the atomic instructions extension.'

from utils        import sext_xlen, sext_32, sext, signed, trim
from pydgin.utils import trim_32
from helpers      import *

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [

  ['lr_w',               '00010xx00000xxxxx010xxxxx0101111'],
  ['sc_w',               '00011xxxxxxxxxxxx010xxxxx0101111'],
  ['amoswap_w',          '00001xxxxxxxxxxxx010xxxxx0101111'],
  ['amoadd_w',           '00000xxxxxxxxxxxx010xxxxx0101111'],
  ['amoxor_w',           '00100xxxxxxxxxxxx010xxxxx0101111'],
  ['amoor_w',            '01000xxxxxxxxxxxx010xxxxx0101111'],
  ['amoand_w',           '01100xxxxxxxxxxxx010xxxxx0101111'],
  ['amomin_w',           '10000xxxxxxxxxxxx010xxxxx0101111'],
  ['amomax_w',           '10100xxxxxxxxxxxx010xxxxx0101111'],
  ['amominu_w',          '11000xxxxxxxxxxxx010xxxxx0101111'],
  ['amomaxu_w',          '11100xxxxxxxxxxxx010xxxxx0101111'],

]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_lr_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sc_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoswap_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  s.mem.write( addr, 4, trim(s.rf[inst.rs2], 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_amoadd_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  s.mem.write( addr, 4, trim(value + s.rf[inst.rs2], 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_amoxor_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  s.mem.write( addr, 4, trim(value ^ s.rf[inst.rs2], 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_amoor_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  s.mem.write( addr, 4, trim(value | s.rf[inst.rs2], 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_amoand_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  s.mem.write( addr, 4, trim(value & s.rf[inst.rs2], 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_amomin_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  new   = min( signed(value, 32), signed(s.rf[inst.rs2], 32) )
  s.mem.write( addr, 4, trim(new, 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_amomax_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  new   = max( signed(value, 32), signed(s.rf[inst.rs2], 32) )
  s.mem.write( addr, 4, trim(new, 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_amominu_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  new   = min( value, s.rf[inst.rs2] )
  s.mem.write( addr, 4, trim(new, 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_amomaxu_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  new   = max( value, s.rf[inst.rs2] )
  s.mem.write( addr, 4, trim(new, 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

