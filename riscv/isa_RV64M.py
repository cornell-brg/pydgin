#=======================================================================
# isa_RV64M.py
#=======================================================================
'RISC-V instructions for integer multiplication and division.'

from utils        import sext_xlen, sext_32, sext, signed, trim
from pydgin.utils import trim_32
from helpers      import *

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [

  ['mulw',               '0000001xxxxxxxxxx000xxxxx0111011'],
  ['divw',               '0000001xxxxxxxxxx100xxxxx0111011'],
  ['divuw',              '0000001xxxxxxxxxx101xxxxx0111011'],
  ['remw',               '0000001xxxxxxxxxx110xxxxx0111011'],
  ['remuw',              '0000001xxxxxxxxxx111xxxxx0111011'],

]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_mulw( s, inst ):
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] * s.rf[inst.rs2])
  s.pc += 4

def execute_divw( s, inst ):
  a = signed( s.rf[inst.rs1], 64 )
  b = signed( s.rf[inst.rs2], 64 )
  if b == 0:
    s.rf[ inst.rd ] = -1
  else:
    sign = -1 if (a < 0) ^ (b < 0) else 1
    s.rf[ inst.rd ] = sext_32( abs(a) / abs(b) * sign )
  s.pc += 4

def execute_divuw( s, inst ):
  a = s.rf[inst.rs1]
  b = s.rf[inst.rs2]
  if b == 0:
    s.rf[ inst.rd ] = -1
  else:
    s.rf[ inst.rd ] = sext_32( a / b )
  s.pc += 4

def execute_remw( s, inst ):
  a = signed( s.rf[inst.rs1], 64 )
  b = signed( s.rf[inst.rs2], 64 )
  if b == 0:
    s.rf[ inst.rd ] = a
  else:
    sign = 1 if (a > 0) else -1
    s.rf[ inst.rd ] = sext_32( abs(a) % abs(b) * sign )
  s.pc += 4

def execute_remuw( s, inst ):
  a = s.rf[inst.rs1]
  b = s.rf[inst.rs2]
  if b == 0:
    s.rf[ inst.rd ] = a
  else:
    s.rf[ inst.rd ] = sext_32( a % b )
  s.pc += 4

