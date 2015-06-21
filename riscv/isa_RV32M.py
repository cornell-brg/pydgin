#=======================================================================
# isa_RV32M.py
#=======================================================================
'RISC-V instructions for integer multiplication and division.'

from utils        import sext_xlen, sext_32, sext, signed, trim, multhi64
from pydgin.utils import trim_32
from helpers      import *

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [

  ['mul',                '0000001xxxxxxxxxx000xxxxx0110011'],
  ['mulh',               '0000001xxxxxxxxxx001xxxxx0110011'],
  ['mulhsu',             '0000001xxxxxxxxxx010xxxxx0110011'],
  ['mulhu',              '0000001xxxxxxxxxx011xxxxx0110011'],
  ['div',                '0000001xxxxxxxxxx100xxxxx0110011'],
  ['divu',               '0000001xxxxxxxxxx101xxxxx0110011'],
  ['rem',                '0000001xxxxxxxxxx110xxxxx0110011'],
  ['remu',               '0000001xxxxxxxxxx111xxxxx0110011'],

]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_mul( s, inst ):
  s.rf[ inst.rd ] = sext_xlen( s.rf[inst.rs1] * s.rf[inst.rs2])
  s.pc += 4

def execute_mulh( s, inst ):
  a, b = s.rf[inst.rs1], s.rf[inst.rs2]
  a_s, b_s = signed(a, 64), signed(b, 64)
  a, b = abs(a_s), abs(b_s)

  multlo = trim_64( a * b )
  multhi = multhi64( a, b )

  # negate -- taken from
  # http://stackoverflow.com/questions/1541426/computing-high-64-bits-of-a-64x64-int-product-in-c
  # this requires us to do low multiplication as well, so it's probably
  # not very efficient
  if (a_s < 0) ^ (b_s < 0):
    multhi = ~multhi
    if multlo == 0:
      multhi += 1

  s.rf[ inst.rd ] = sext_xlen( multhi )
  s.pc += 4

def execute_mulhsu( s, inst ):
  a, b = s.rf[inst.rs1], s.rf[inst.rs2]
  a_s = signed(a, 64)
  a = abs(a_s)

  multlo = trim_64( a * b )
  multhi = multhi64( a, b )

  # negate -- taken from
  # http://stackoverflow.com/questions/1541426/computing-high-64-bits-of-a-64x64-int-product-in-c
  # this requires us to do low multiplication as well, so it's probably
  # not very efficient
  if a_s < 0:
    multhi = ~multhi
    if multlo == 0:
      multhi += 1

  s.rf[ inst.rd ] = sext_xlen( multhi )
  s.pc += 4

def execute_mulhu( s, inst ):
  a, b = s.rf[inst.rs1], s.rf[inst.rs2]

  multhi = multhi64( a, b )

  s.rf[ inst.rd ] = sext_xlen( multhi )
  s.pc += 4

def execute_div( s, inst ):
  a = signed( s.rf[inst.rs1], 64 )
  b = signed( s.rf[inst.rs2], 64 )
  if b == 0:
    s.rf[ inst.rd ] = -1
  else:
    s.rf[ inst.rd ] = sext_xlen( abs(a) / abs(b) *
                                 (-1 if (a < 0) ^ (b < 0) else 1) )
  s.pc += 4

def execute_divu( s, inst ):
  a = s.rf[inst.rs1]
  b = s.rf[inst.rs2]
  if b == 0:
    s.rf[ inst.rd ] = -1
  else:
    s.rf[ inst.rd ] = sext_xlen( a / b )
  s.pc += 4

def execute_rem( s, inst ):
  a = signed( s.rf[inst.rs1], 64 )
  b = signed( s.rf[inst.rs2], 64 )
  if b == 0:
    s.rf[ inst.rd ] = a
  else:
    s.rf[ inst.rd ] = sext_xlen( abs(a) % abs(b) * (1 if (a > 0) else -1) )
  s.pc += 4

def execute_remu( s, inst ):
  a = s.rf[inst.rs1]
  b = s.rf[inst.rs2]
  if b == 0:
    s.rf[ inst.rd ] = a
  else:
    s.rf[ inst.rd ] = sext_xlen( a % b )
  s.pc += 4

