#=======================================================================
# utils.py
#=======================================================================
# Collection of utility functions for ARM instruction implementations.

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
  if   I(inst) == 1:
    if rn( inst ) == 15: raise Exception('Modifying stack pointer not implemented!')
    rotate_imm = rotate( inst )
    operand    = rotate_right( imm_8(inst), rotate_imm*2 )
    if rotate_imm == 0: cout = s.C
    else:               cout = operand >> 3
    return operand, cout

  # 32-bit register shifted by 5-bit immediate
  elif (inst >>  4 & 0b1) == 0:
    if rn( inst ) == 15: raise Exception('Modifying stack pointer not implemented!')
    if rm( inst ) == 15: raise Exception('Modifying stack pointer not implemented!')
    return shift_operand_imm( s, inst )

  # 32-bit register shifted by 32-bit register
  elif (inst >>  7 & 0b1) == 0:
    return shift_operand_reg( s, inst )

  # Arithmetic or Load/Store instruction extension space
  else:
    raise Exception('Not a data-processing instruction!')

# Shifter constants

LOGIC_SHIFT_LEFT  = 0b00
LOGIC_SHIFT_RIGHT = 0b01
ARITH_SHIFT_RIGHT = 0b10
ROTATE_RIGHT      = 0b11

#-----------------------------------------------------------------------
# shifter_operand_imm
#-----------------------------------------------------------------------
def shifter_operand_imm( s, inst ):
  shift_op  = shift( inst )
  Rm        = s.rf[ rm(inst) ]
  shift_imm = shift_amt( inst )
  assert 0 <= off <= 31

  if   shift_op == LOGIC_SHIFT_LEFT:
    out  = Rm   if (shift_imm == 0) else Rm << shift_imm
    cout = s.C  if (shift_imm == 0) else (Rm >> 32 - shift_imm)&1

  elif shift_op == LOGIC_SHIFT_RIGHT:
    # NOTE: shift_imm == 0 signifies a shift by 32
    out  = 0          if (shift_imm == 0) else data >> shift_imm
    cout = data >> 31 if (shift_imm == 0) else (data >> shift_imm - 1)&1

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

  return out, cout

#-----------------------------------------------------------------------
# shifter_operand_reg
#-----------------------------------------------------------------------
def shifter_operand_reg( s, inst ):
  shift_op = shift( inst )
  Rm       = s.rf[ rm(inst) ]
  Rs       = s.rf[ rs(inst) ] & 0xFF
  assert 0 <= off <= 31

  if   shift_op == LOGIC_SHIFT_LEFT:
    if   Rs ==  0: out, cout = Rm,       s.C
    elif Rs <  32: out, cout = Rm << Rs, (Rm >> 32 - Rs)&1
    elif Rs == 32: out, cout = 0,        (Rm)&1
    elif Rs >  32: out, cout = 0,        0

  elif shift_op == LOGIC_SHIFT_RIGHT:
    if   Rs ==  0: out, cout = Rm,       s.C
    elif Rs <  32: out, cout = Rm >> Rs, (Rm >> Rs - 1)&1
    elif Rs == 32: out, cout = 0,        (Rm >> 31)&1
    elif Rs >  32: out, cout = 0,        0

  elif shift_op == ARITH_SHIFT_RIGHT:
    if   Rs ==  0: out, cout = Rm,       s.C
    elif Rs <  32:
      out  = arith_shift( Rm, shift_imm )
      cout = (Rm >> Rs - 1)&1
    elif Rs >= 32:
      out  = 0 if ((Rm >> 31) == 0) else 0xFFFFFFFF
      cout = (Rm >> 31)&1

  elif shift_op == ROTATE_RIGHT:
    Rs4 = Rs & 0b1111
    if   Rs  == 0: out, cout = Rm,                    s.C
    elif Rs4 == 0: out, cout = Rm,                    (Rm >> 31)&1
    elif Rs4 >  0: out, cout = rotate_right(Rm, Rs4), (Rm >> Rs4 - 1)&1

  return out, cout

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
  if   cond == 0b0000: return     s.Z
  elif cond == 0b0001: return not s.Z
  elif cond == 0b0010: return     s.C
  elif cond == 0b0011: return not s.C
  elif cond == 0b0100: return     s.N
  elif cond == 0b0101: return not s.N
  elif cond == 0b0110: return     s.V
  elif cond == 0b0111: return not s.V
  elif cond == 0b1000: return s.C and (not s.Z)
  elif cond == 0b1001: return (not s.C) and s.Z
  elif cond == 0b1010: return s.N == s.V
  elif cond == 0b1011: return s.N != s.V
  elif cond == 0b1100: return (not s.Z) and (s.N == s.V)
  elif cond == 0b1101: return (    s.Z) or  (s.N != s.V)
  elif cond == 0b1110: return True
  return True

#-----------------------------------------------------------------------
# carry_from
#-----------------------------------------------------------------------
# CarryFrom (ref: ARM DDI 0100I - Glossary-12)
#
#   if   result > (2**32 - 1)
#    and is_unsigned( operand_a )
#    and is_unsigned( operand_b )
#
def carry_from( cond ):
  print 'WARNING: implement carry_from!'

#-----------------------------------------------------------------------
# overflow_from_add
#-----------------------------------------------------------------------
# OverflowFrom - Add (ref: ARM DDI 0100I - Glossary-11)
#
#   if   operand_a[31] == operand_b[31] and
#    and operand_a[31] != result[31]
#
def overflow_from_add( cond ):
  print 'WARNING: implement overflow_from_add!'
  return True

#-----------------------------------------------------------------------
# overflow_from_sub
#-----------------------------------------------------------------------
# OverflowFrom - Sub (ref: ARM DDI 0100I - Glossary-11)
#
#   if   operand_a[31] != operand_b[31]
#    and operand_a[31] != result[31]
#
def overflow_from_sub( cond ):
  print 'WARNING: implement overflow_from_sub!'
  return True

#-----------------------------------------------------------------------
# rotate_right
#-----------------------------------------------------------------------
def rotate_right( data, shift )
  return trim_32( (data >> shift ) | (data << (32 - shift)) )

#-----------------------------------------------------------------------
# arith_shift
#-----------------------------------------------------------------------
def arith_shift( data, shift ):
  fill = 0xFFFFFFFF if (data >> 31) else 0
  return (fill << (32-shift)) | (data >> shift)

#-----------------------------------------------------------------------
# trim_32
#-----------------------------------------------------------------------
def trim_32( val )
  return val & 0xFFFFFFFF

