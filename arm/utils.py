#=======================================================================
# utils.py
#=======================================================================
# Collection of utility functions for ARM instruction implementations.

from pydgin.utils import trim_32, r_uint
from pydgin.misc  import FatalError
from instruction  import *

#=======================================================================
# Addressing Mode 1 - Data-processing operands (page A5-2)
#=======================================================================

#-----------------------------------------------------------------------
# shifter_operand
#-----------------------------------------------------------------------
# For data processing instructions, obtaining the value of the second
# operand is a non-trivial process.  This operand can either be:
#
# (a) A 32-bit immediate value, calculated from an 8-bit <immed_8>
#     right-rotated by a 4-bit <rotate_imm> field
# (b) A 32-bit register value "shifted" by a 5-bit <shift_imm> field
# (c) A 32-bit register value "shifted" by another 32-bit register value
#
# These options are chosen based on the following selectors:
#
# (a) if inst[25] == 1 (the <I> instruction field)
# (b) if inst[25] == 0 and inst[4] == 0
# (c) if inst[25] == 0 and inst[4] == 1 and inst[7] == 0
#
# For b) and c), the "shift" operation can actually be one of four
# transformation operations depending on the value of the <shift>
# instruction field, in inst[6:5].
#
# - inst[6:5] == 00: logical shift left
# - inst[6:5] == 01: logical shift right
# - inst[6:5] == 10: arithmetic shift right
# - inst[6:5] == 11: rotate right
#
# A fifth operation, rotate right with extend, is possible for case (b)
# when the rotate right operation is selected, and the rotation value
# present in the <shift_imm> field is zero.
# TODO: this is currently not handled!
#
# ARM has 16 data-processing instructions, these include:
#
#   and, eor, sub, rsb, add, adc, sbc, rsc
#   tst, teq, cmp, cmn, orr, mov, bic, mvn
#
def shifter_operand( s, inst ):

  # 32-bit immediate
  # http://stackoverflow.com/a/2835503
  if   inst.I == 1:
    rotate_imm = inst.rotate
    operand    = rotate_right( inst.imm_8, rotate_imm*2 )
    if rotate_imm == 0: cout = s.C
    else:               cout = (operand >> 31) & 1
    return operand, cout

  # 32-bit register shifted by 5-bit immediate
  elif (inst.bits >>  4 & 0b1) == 0:
    return shifter_operand_imm( s, inst )

  # 32-bit register shifted by 32-bit register
  elif (inst.bits >>  7 & 0b1) == 0:
    return shifter_operand_reg( s, inst )

  # Arithmetic or Load/Store instruction extension space
  else:
    raise FatalError('Not a data-processing instruction! PC: %x' % s.fetch_pc())

# Shifter constants

LOGIC_SHIFT_LEFT  = 0b00
LOGIC_SHIFT_RIGHT = 0b01
ARITH_SHIFT_RIGHT = 0b10
ROTATE_RIGHT      = 0b11

#-----------------------------------------------------------------------
# shifter_operand_imm
#-----------------------------------------------------------------------
def shifter_operand_imm( s, inst ):
  shift_op  = inst.shift
  Rm        = s.rf[ inst.rm ]
  shift_imm = inst.shift_amt
  assert 0 <= shift_imm <= 31

  if   shift_op == LOGIC_SHIFT_LEFT:
    out  = Rm   if (shift_imm == 0) else Rm << shift_imm
    cout = s.C  if (shift_imm == 0) else (Rm >> 32 - shift_imm)&1

  elif shift_op == LOGIC_SHIFT_RIGHT:
    # NOTE: shift_imm == 0 signifies a shift by 32
    out  = 0        if (shift_imm == 0) else Rm >> shift_imm
    cout = Rm >> 31 if (shift_imm == 0) else (Rm >> shift_imm - 1)&1

  elif shift_op == ARITH_SHIFT_RIGHT:
    # NOTE: shift_imm == 0 signifies a shift by 32
    if shift_imm == 0:
      if (Rm >> 31) == 0: out, cout = 0,          Rm >> 31
      else:               out, cout = 0xFFFFFFFF, Rm >> 31
    else:
      out  = arith_shift( Rm, shift_imm )
      cout = (Rm >> shift_imm - 1)&1

  elif shift_op == ROTATE_RIGHT:
    # NOTE: shift_imm == 0 signifies a rotate right with extend (RRX)
    if shift_imm == 0:
      out  = (s.C << 31) | (Rm >> 1)
      cout = Rm & 1
    else:
      out  = rotate_right( Rm, shift_imm )
      cout = (Rm >> shift_imm - 1)&1

  else:
    raise FatalError('Impossible shift_op!')

  return trim_32(out), cout

#-----------------------------------------------------------------------
# shifter_operand_reg
#-----------------------------------------------------------------------
def shifter_operand_reg( s, inst ):
  shift_op = inst.shift
  Rm       = s.rf[ inst.rm ]
  Rs       = s.rf[ inst.rs ] & 0xFF

  out = cout = 0

  if   shift_op == LOGIC_SHIFT_LEFT:
    if   Rs ==  0: out, cout = Rm,       s.C
    elif Rs <  32: out, cout = Rm << Rs, (Rm >> 32 - Rs)&1
    elif Rs == 32: out, cout = 0,        (Rm)&1
    elif Rs >  32: out, cout = 0,        0

  elif shift_op == LOGIC_SHIFT_RIGHT:
    if   Rs ==  0: out, cout = Rm,       s.C
    elif Rs <  32: out, cout = Rm >> Rs, (Rm >> (Rs-1))&1
    elif Rs == 32: out, cout = 0,        (Rm >> 31)&1
    elif Rs >  32: out, cout = 0,        0

  elif shift_op == ARITH_SHIFT_RIGHT:
    if   Rs ==  0: out, cout = Rm,       s.C
    elif Rs <  32:
      out  = arith_shift( Rm, Rs )
      cout = (Rm >> (Rs-1))&1
    elif Rs >= 32:
      out  = 0 if ((Rm >> 31) == 0) else 0xFFFFFFFF
      cout = (Rm >> 31)&1

  elif shift_op == ROTATE_RIGHT:
    Rs4 = Rs & 0b1111
    if   Rs  == 0: out, cout = Rm,                    s.C
    elif Rs4 == 0: out, cout = Rm,                    (Rm >> 31)&1
    elif Rs4 >  0: out, cout = rotate_right(Rm, Rs4), (Rm >> Rs4 - 1)&1

  else:
    raise FatalError('Impossible shift_op!')

  return trim_32(out), cout

#-----------------------------------------------------------------------
# carry_from
#-----------------------------------------------------------------------
# CarryFrom (ref: ARM DDI 0100I - Glossary-12)
#
#   if   result > (2**32 - 1)
#
def carry_from( result ):
  return result > 0xFFFFFFFF

#-----------------------------------------------------------------------
# borrow_from
#-----------------------------------------------------------------------
# BorrowFrom (ref: ARM DDI 0100I - Glossary-3)
#
#  if result < 0
#
def borrow_from( result ):
  return result < 0

#-----------------------------------------------------------------------
# not_borrow_from
#-----------------------------------------------------------------------
# NOT BorrowFrom (ref: ARM DDI 0100I - Glossary-3) (more efficient than
# "not borrow_from"
#
#  if result >= 0
#
def not_borrow_from( result ):
  return result >= 0

#-----------------------------------------------------------------------
# overflow_from_add
#-----------------------------------------------------------------------
# OverflowFrom - Add (ref: ARM DDI 0100I - Glossary-11)
#
#   if   operand_a[31] == operand_b[31] and
#    and operand_a[31] != result[31]
#
def overflow_from_add( a, b, result ):
  return (a >> 31 == b >> 31) & (a >> 31 != (result>>31)&1)

#-----------------------------------------------------------------------
# overflow_from_sub
#-----------------------------------------------------------------------
# OverflowFrom - Sub (ref: ARM DDI 0100I - Glossary-11)
#
#   if   operand_a[31] != operand_b[31]
#    and operand_a[31] != result[31]
#
def overflow_from_sub( a, b, result ):
  return (a >> 31 != b >> 31) & (a >> 31 != (result>>31)&1)

#-----------------------------------------------------------------------
# rotate_right
#-----------------------------------------------------------------------
def rotate_right( data, shift ):
  return trim_32( (data >> shift ) | (data << (32 - shift)) )

#=======================================================================
# Addressing Mode 2 - Load and Store Word or Unsigned Byte (page A5-18)
#=======================================================================

#-----------------------------------------------------------------------
# addressing_mode_2( s, inst )
#-----------------------------------------------------------------------
#
# I P W
#
# 0 1 0 Immediate Offset
# 1 1 0 Register Offset
# 1 1 0 Scaled Register Offset
# 0 1 1 Immediate Pre-Indexed
# 1 1 1 Register Pre-Indexed
# 1 1 1 Scaled Register Pre-Indexed
# 0 0 0 Immediate Post-Indexed
# 1 0 0 Register Post-Indexed
# 1 0 0 Scaled Register Post-Indexed
#
def addressing_mode_2( s, inst ):

  # Immediate vs. Register Offset
  if not inst.I: index    = inst.imm_12
  else:           index, _ = shifter_operand_imm(s, inst)

  Rn          = s.rf[inst.rn]
  offset_addr = Rn + index if inst.U else Rn - index

  # Offset Addressing/Pre-Indexed Addressing vs. Post-Indexed Addressing
  if inst.P: addr = offset_addr
  else:        addr = Rn

  # Offset Addressing vs. Pre-/Post-Indexed Addressing
  if not (inst.P ^ inst.W):
    s.rf[inst.rn] = trim_32( offset_addr )

  return trim_32( addr )

#=======================================================================
# Addressing Mode 3 - Miscellaneous Loads and Stores (page A5-33)
#=======================================================================

#-----------------------------------------------------------------------
# addressing_mode_3( s, inst )
#-----------------------------------------------------------------------
#
# I P B W
#
# 0 1 1 0 Immediate Offset
# 0 1 0 0 Register Offset
# 0 1 1 1 Immediate Pre-indexed
# 0 1 0 1 Register Pre-indexed
# 0 0 1 0 Immediate Post-indexed
# 0 0 0 0 Register Post-indexed
#
def addressing_mode_3( s, inst ):
  if inst.SH == 0b00:
    raise FatalError('Not a load/store instruction!')

  # Immediate vs. Register Offset
  if inst.B: index = (inst.imm_H << 4) | inst.imm_L
  else:        index = s.rf[inst.rm]

  Rn          = s.rf[inst.rn]
  offset_addr = Rn + index if inst.U else Rn - index

  # Offset Addressing/Pre-Indexed Addressing vs. Post-Indexed Addressing
  if inst.P: addr = offset_addr
  else:        addr = Rn

  # Offset Addressing vs. Pre-/Post-Indexed Addressing
  if not (inst.P ^ inst.W):
    s.rf[inst.rn] = trim_32( offset_addr )

  return trim_32( addr )

#=======================================================================
# Addressing Mode 4 - Load and Store Multiple (page A5-41)
#=======================================================================

#-----------------------------------------------------------------------
# addressing_mode_4
#-----------------------------------------------------------------------
# Load and Store Multiple addressing modes produce a sequential range of
# addresses. The lowest-numbered register is stored at the lowest memory
# address and the highest-numbered register at the highest memory
# address.
#
#   P U  Addressing Mode
#
#   0 1  IA Increment After
#   1 1  IB Increment Before
#   0 0  DA Decrement After
#   1 0  DB Decrement Before
#
def addressing_mode_4( s, inst ):

  IA = 0b01
  IB = 0b11
  DA = 0b00
  DB = 0b10

  mode   = (inst.P << 1) | inst.U
  Rn     = s.rf[ inst.rn ]
  nbytes = 4 * popcount( inst.register_list )

  if   mode == IA: start_addr, end_addr = Rn,          Rn+nbytes-4
  elif mode == IB: start_addr, end_addr = Rn+4,        Rn+nbytes
  elif mode == DA: start_addr, end_addr = Rn-nbytes+4, Rn
  else:            start_addr, end_addr = Rn-nbytes,   Rn-4

  if inst.W:
    s.rf[ inst.rn ] = trim_32( (Rn + nbytes) if inst.U else (Rn - nbytes) )

  return trim_32( start_addr ), trim_32( end_addr )

#=======================================================================
# Addressing Mode 5 - Load and Store Coprocessor (page A5-49)
#=======================================================================

# TODO

#=======================================================================
# Miscellaneous
#=======================================================================

#-----------------------------------------------------------------------
# condition_passed
#-----------------------------------------------------------------------
# ConditionPassed (ref: ARM DDI 0100I - Glossary-4, A3-4)
#
# Code  Ext.    Meaning                             Cond Flag
#
# 0000  EQ      Equal                               [Z:1]
# 0001  NE      Not equal                           [Z:0]
# 0010  CS/HS   Carry set/unsigned higher or same   [C:1]
# 0011  CC/LO   Carry clear/unsigned lower          [C:0]
# 0100  MI      Minus/negative                      [N:1]
# 0101  PL      Plus/positive or zero               [N:0]
# 0110  VS      Overflow                            [V:1]
# 0111  VC      No overflow                         [V:0]
# 1000  HI      Unsigned higher                     [C:1 Z:0]
# 1001  LS      Unsigned lower or same              [C:0] or
#                                                   [Z:1]
# 1010  GE      Signed greater than or equal        [N:1 V:1] or
#                                                   [N:0 V:0]
# 1011  LT      Signed less than                    [N:1 V:0] or
#                                                   [N:0 V:1]
# 1100  GT      Signed greater than                 [Z:0 N:1 V:1] or
#                                                   [Z:0 N:0 V:0]
# 1101  LE      Signed less than or equal           [Z:1] or
#                                                   [N:1 V:0] or
#                                                   [N:0 V:1]
# 1110  AL      Always (unconditional)              -
# 1111  -       See Condition code 0b1111           -
#
def condition_passed( s, cond ):
  if   cond == 0b0000: passed =     s.Z
  elif cond == 0b0001: passed = not s.Z
  elif cond == 0b0010: passed =     s.C
  elif cond == 0b0011: passed = not s.C
  elif cond == 0b0100: passed =     s.N
  elif cond == 0b0101: passed = not s.N
  elif cond == 0b0110: passed =     s.V
  elif cond == 0b0111: passed = not s.V
  elif cond == 0b1000: passed = s.C and (not s.Z)
  elif cond == 0b1001: passed = (not s.C) or s.Z
  elif cond == 0b1010: passed = s.N == s.V
  elif cond == 0b1011: passed = s.N != s.V
  elif cond == 0b1100: passed = (not s.Z) and (s.N == s.V)
  elif cond == 0b1101: passed = (    s.Z) or  (s.N != s.V)
  elif cond == 0b1110: passed = True
  else:                passed = True

  if s.debug.enabled('insts') and not passed:
    print 'Predicated False!',

  return passed

#-----------------------------------------------------------------------
# arith_shift
#-----------------------------------------------------------------------
def arith_shift( data, shift ):
  fill = r_uint( 0xFFFFFFFF if (data >> 31) else 0 )
  return (fill << (32-shift)) | (data >> shift)

#-----------------------------------------------------------------------
# sext_30
#-----------------------------------------------------------------------
# sign extend 24-bit immediates to 30-bit values
def sext_30( value ):
  if value & 0x800000:
    return 0x3F000000 | value
  return value

#-----------------------------------------------------------------------
# popcount
#-----------------------------------------------------------------------
# Implementation shamelessly borrowed from:
# http://stackoverflow.com/a/407758
# TODO: better RPython way to do this?
def popcount( i ):
 assert 0 <= i < 0x100000000
 i = i - ((i >> 1) & 0x55555555)
 i = (i & 0x33333333) + ((i >> 2) & 0x33333333)
 return (((i + (i >> 4) & 0xF0F0F0F) * 0x1010101) & 0xFFFFFFFF) >> 24

