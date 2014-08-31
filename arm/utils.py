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
def shifter_operand( inst ):
  # http://stackoverflow.com/a/2835503
  # 32-bit immediate
  if   I(inst) == 1:
    val, rot = imm_8( inst ), rotate( inst )
    if rot == 0: return val
    else:        return rotate_right( val, 2*rot )
  elif (inst >>  4 & 0b1) == 0:
    return shift_op( s.rf[rm( inst )], shift_amt( inst ), kind=shift( inst ) )
  elif (inst >>  7 & 0b1) == 0:
    return shift_op( s.rf[rm( inst )], s.rf[rs( inst )],  kind=shift( inst ) )
  else: raise Exception('Decoding error!')

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
def rotate_right( val, rot )
  return trim_32( (val >> rot) | (val << (32 - rot)) )

#-----------------------------------------------------------------------
# shift_op
#-----------------------------------------------------------------------
def shift_op( val, shift_amt, op )
  if   kind == 0b00:  # logical shift left
    return val << shift_amt
  elif kind == 0b01:  # logical shift right
    return val >> shift_amt
  elif kind == 0b10:  # arithmetic shift right
    return (0xFFFFFFFF << (32-shift_amt)) | (val >> shift_amt)
  else:               # rotate right
    if shift_amt == 0: raise Exception('TODO: implement rotate right extend!')
    return rotate_right( val, shift_amt )

#-----------------------------------------------------------------------
# trim_32
#-----------------------------------------------------------------------
def trim_32( val )
  return val & 0xFFFFFFFF

