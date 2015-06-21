#=======================================================================
# isa_RV64I.py
#=======================================================================
'RISC-V instructions for base integer instruction set.'

from utils        import sext_xlen, sext_32, sext, signed, trim
from pydgin.utils import trim_32
from helpers      import *

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [

  ['lwu',                'xxxxxxxxxxxxxxxxx110xxxxx0000011'],
  ['ld',                 'xxxxxxxxxxxxxxxxx011xxxxx0000011'],
  ['sd',                 'xxxxxxxxxxxxxxxxx011xxxxx0100011'],
  #['slli',               '000000xxxxxxxxxxx001xxxxx0010011'], # ISA manual typo
  #['srli',               '000000xxxxxxxxxxx101xxxxx0010011'], # ISA manual typo
  #['srai',               '010000xxxxxxxxxxx101xxxxx0010011'], # ISA manual typo
  ['addiw',              'xxxxxxxxxxxxxxxxx000xxxxx0011011'],
  ['slliw',              '0000000xxxxxxxxxx001xxxxx0011011'],
  ['srliw',              '0000000xxxxxxxxxx101xxxxx0011011'],
  ['sraiw',              '0100000xxxxxxxxxx101xxxxx0011011'],
  ['addw',               '0000000xxxxxxxxxx000xxxxx0111011'],
  ['subw',               '0100000xxxxxxxxxx000xxxxx0111011'],
  ['sllw',               '0000000xxxxxxxxxx001xxxxx0111011'],
  ['srlw',               '0000000xxxxxxxxxx101xxxxx0111011'],
  ['sraw',               '0100000xxxxxxxxxx101xxxxx0111011'],

]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_lwu( s, inst ):
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = s.mem.read( addr, 4 )
  s.pc += 4

def execute_ld( s, inst ):
  # TODO: make memory support 64-bit ops
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = ( s.mem.read( addr+4, 4 ) << 32 ) \
                  | s.mem.read( addr, 4 )
  s.pc += 4

def execute_sd( s, inst ):
  # TODO: make memory support 64-bit ops
  addr = s.rf[inst.rs1] + inst.s_imm
  s.mem.write( addr,   4, trim_32( s.rf[inst.rs2] ) )
  s.mem.write( addr+4, 4, trim_32( s.rf[inst.rs2] >> 32 ) )
  s.pc += 4

def execute_addiw( s, inst ):
  s.rf[ inst.rd ] = sext_32( inst.i_imm + s.rf[inst.rs1] )
  s.pc += 4

def execute_slliw( s, inst ):
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] << SHAMT( s, inst ) )
  s.pc += 4

def execute_srliw( s, inst ):
  s.rf[ inst.rd ] = sext_32( trim_32( s.rf[inst.rs1] ) >> SHAMT( s, inst ) )
  s.pc += 4

def execute_sraiw( s, inst ):
  s.rf[ inst.rd ] = signed( s.rf[inst.rs1], 32 ) >> SHAMT( s, inst )
  s.pc += 4

def execute_addw( s, inst ):
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] + s.rf[inst.rs2] )
  s.pc += 4

def execute_subw( s, inst ):
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] - s.rf[inst.rs2])
  s.pc += 4

def execute_sllw( s, inst ):
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] << (s.rf[inst.rs2] & 0x1F ) )
  s.pc += 4

def execute_srlw( s, inst ):
  s.rf[ inst.rd ] = sext_32( trim_32( s.rf[inst.rs1] ) >> (s.rf[inst.rs2] & 0x1F) )
  s.pc += 4

def execute_sraw( s, inst ):
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] >> (s.rf[inst.rs2] & 0x1F) )
  s.pc += 4

