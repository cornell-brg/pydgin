#=======================================================================
# isa.py
#=======================================================================

import py
import re
import sys

from instruction import *
from utils       import shifter_operand, rotate_right, shift_op
from utils       import trim_32, condition_passed, carry_from
from utils       import overflow_from_add, overflow_from_sub

from utils       import sign_extend_30

#=======================================================================
# Register Definitions
#=======================================================================

reg_map = {
  '$0'   :  0,   '$1'   :  1,   '$2'   :  2,   '$3'   :  3,
  '$4'   :  4,   '$5'   :  5,   '$6'   :  6,   '$7'   :  7,
  '$8'   :  8,   '$9'   :  9,   '$10'  : 10,   '$11'  : 11,
  '$12'  : 12,   '$13'  : 13,   '$14'  : 14,   '$15'  : 15,
  '$16'  : 16,   '$17'  : 17,   '$18'  : 18,   '$19'  : 19,
  '$20'  : 20,   '$21'  : 21,   '$22'  : 22,   '$23'  : 23,
  '$24'  : 24,   '$25'  : 25,   '$26'  : 26,   '$27'  : 27,
  '$28'  : 28,   '$29'  : 29,   '$30'  : 30,   '$31'  : 31,

  'r0'   :  0,   'r1'   :  1,   'r2'   :  2,   'r3'   :  3,
  'r4'   :  4,   'r5'   :  5,   'r6'   :  6,   'r7'   :  7,
  'r8'   :  8,   'r9'   :  9,   'r10'  : 10,   'r11'  : 11,
  'r12'  : 12,   'r13'  : 13,   'r14'  : 14,   'r15'  : 15,
  'r16'  : 16,   'r17'  : 17,   'r18'  : 18,   'r19'  : 19,
  'r20'  : 20,   'r21'  : 21,   'r22'  : 22,   'r23'  : 23,
  'r24'  : 24,   'r25'  : 25,   'r26'  : 26,   'r27'  : 27,
  'r28'  : 28,   'r29'  : 29,   'r30'  : 30,   'r31'  : 31,

  'sp'   : 13,  # stack pointer
  'lr'   : 13,  # link register
  # NOTE: in ARM the PC is address of the current instruction being
  #       executed + 8!! That means for a given cycle in our simulator,
  #       PC read by fetch and PC read by execute need different values.
  #       Best way to do this?
  'pc'   : 15,  # pc

  # cpsr/spsr bits
  #
  #  N         31
  #  Z         30
  #  C         29
  #  V         28
  #  Q         27
  #  RESERVED  26
  #  J         24
  #  RESERVED  23:20
  #  GE[3:0]   19:16
  #  RESERVED  15:10
  #  E          9
  #  A          8
  #  I          7
  #  F          6
  #  T          5
  #  M[4:0]     4:0

}

#=======================================================================
# Instruction Encodings
#=======================================================================
#
# ARM ISA Manual: (ARM DDI 0100I)
#
# - pg. A4-286
# - pg. A3-2
# - pg. A4-2
#
encodings = [
  ['nop',      '00000000000000000000000000000000'],
  ['adc',      '____00x0101xxxxxxxxxxxxxxxxxxxxx'],
  ['add',      '____00x0100xxxxxxxxxxxxxxxxxxxxx'],
  ['and',      '____00x0000xxxxxxxxxxxxxxxxxxxxx'],
  ['b',        '____1010xxxxxxxxxxxxxxxxxxxxxxxx'],
  ['bl',       '____1011xxxxxxxxxxxxxxxxxxxxxxxx'],
  ['bic',      '____00x1110xxxxxxxxxxxxxxxxxxxxx'],
  ['bkpt',     '111000010010xxxxxxxxxxxx0111xxxx'],
  ['blx1'      '1111101xxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['blx2',     'xxxx00010010xxxxxxxxxxxx0011xxxx'],
  ['bx',       '____00010010xxxxxxxxxxxx0001xxxx'],
#?['bxj',      '____00010010xxxxxxxxxxxx0010xxxx'],
  ['cdp',      '____1110xxxxxxxxxxxxxxxxxxx0xxxx'],
  ['clz',      '____00010110xxxxxxxxxxxx0001xxxx'],
  ['cmn',      '____00x10111xxxxxxxxxxxxxxxxxxxx'],
  ['cmp',      '____00x10101xxxxxxxxxxxxxxxxxxxx'],
# ['cps',      '111100010000xxx0xxxxxxxxxxx0xxxx'], # v6
# ['cpy',      '____00011010xxxxxxxx00000000xxxx'], # v6
  ['eor',      '____00x0001xxxxxxxxxxxxxxxxxxxxx'],
  ['ldc',      '____110xxxx1xxxxxxxxxxxxxxxxxxxx'],
  ['ldc2',     '1111110xxxx1xxxxxxxxxxxxxxxxxxxx'],
  ['ldm1',     '____100xx0x1xxxxxxxxxxxxxxxxxxxx'],
  ['ldm2',     '____100xx101xxxx0xxxxxxxxxxxxxxx'],
  ['ldm3',     '____100xx1x1xxxx1xxxxxxxxxxxxxxx'],
  ['ldr',      '____01xxx0x1xxxxxxxxxxxxxxxxxxxx'],

  ['ldrb',     '____01xxx1x1xxxxxxxxxxxxxxxxxxxx'],
  ['ldrbt',    '____01x0x111xxxxxxxxxxxxxxxxxxxx'],
#?['ldrd',     '____000puiw0xxxxxxxxxxxx1101xxxx'],
# ['ldrex',    '____000110001xxxxxxxxxxx1001xxxx'], # v6
  ['ldrh',     '____000xxxx1xxxxxxxxxxxx1011xxxx'],
  ['ldrsb',    '____000xxxx1xxxxxxxxxxxx1101xxxx'],
  ['ldrsh',    '____000xxxx1xxxxxxxxxxxx1111xxxx'],
  ['ldrt',     '____01x0x011xxxxxxxxxxxxxxxxxxxx'],
  ['mcr',      '____1110xxx0xxxxxxxxxxxxxxx1xxxx'],
  ['mcr2',     '11111110xxx0xxxxxxxxxxxxxxx1xxxx'],
  ['mcrr',     '____11000100xxxxxxxxxxxxxxxxxxxx'],
  ['mcrr2',    '111111000100xxxxxxxxxxxxxxxxxxxx'],
  ['mla',      '____0000001xxxxxxxxxxxxx1001xxxx'],
  ['mov',      '____00x1101xxxxxxxxxxxxxxxxxxxxx'],
  ['mrc',      '____1110xxx1xxxxxxxxxxxxxxx1xxxx'],
  ['mrc2',     '11111110xxx1xxxxxxxxxxxxxxx1xxxx'],
#?['mrrc',     '____11000101xxxxxxxxxxxxxxxxxxxx'],
# ['mrrc2',    '111111000101xxxxxxxxxxxxxxxxxxxx'], # v6
  ['mrs',      '____00010x00xxxxxxxxxxxxxxxxxxxx'],
  ['msr',      '____00x10x10xxxxxxxxxxxxxxxxxxxx'], # TODO
  ['mul',      '____0000000xxxxxxxxxxxxx1001xxxx'],
  ['mvn',      '____00x1111xxxxxxxxxxxxxxxxxxxxx'],
  ['orr',      '____00x1100xxxxxxxxxxxxxxxxxxxxx'],
# ['pkhbt',    '____01101000xxxxxxxxxxxxx001xxxx'], # v6
# ['pkhtb',    '____01101000xxxxxxxxxxxxx101xxxx'], # v6

#?['pld',      '111101x1x101xxxx1111xxxxxxxxxxxx'],
#?['qadd',     '____00010000xxxxxxxxxxxx0101xxxx'],
# ['qadd16',   '____01100010xxxxxxxxxxxx0001xxxx'], # v6
# ['qadd8',    '____01100010xxxxxxxxxxxx1001xxxx'], # v6
# ['qaddsubx', '____01100010xxxxxxxxxxxx0011xxxx'], # v6
#?['qdadd',    '____00010100xxxxxxxxxxxx0101xxxx'],
#?['qdsub',    '____00010110xxxxxxxxxxxx0101xxxx'],
#?['qsub',     '____00010010xxxxxxxxxxxx0101xxxx'],
# ['qsub16',   '____01100010xxxxxxxxxxxx0111xxxx'], # v6
# ['qsub8',    '____01100010xxxxxxxxxxxx1111xxxx'], # v6
# ['qsubaddx', '____01100010xxxxxxxxxxxx0101xxxx'], # v6
# ['rev',      '____01101011xxxxxxxxxxxx0011xxxx'], # v6
# ['rev16',    '____01101011xxxxxxxxxxxx1011xxxx'], # v6
# ['revsh',    '____01101111xxxxxxxxxxxx1011xxxx'], # v6
# ['rfe',      '1111100xx0x1xxxxxxxx1010xxxxxxxx'], # v6
  ['rsb',      '____00x0011xxxxxxxxxxxxxxxxxxxxx'],
  ['rsc',      '____00x0111xxxxxxxxxxxxxxxxxxxxx'],
# ['sadd16',   '____01100001xxxxxxxxxxxx0001xxxx'], # v6
# ['sadd8',    '____01100001xxxxxxxxxxxx1001xxxx'], # v6
# ['saddsubx', '____01100001xxxxxxxxxxxx0011xxxx'], # v6
  ['sbc',      '____00x0110xxxxxxxxxxxxxxxxxxxxx'],
# ['sel',      '____01101000xxxxxxxxxxxx1011xxxx'], # v6
# ['setend',   '1111000100000001xxxxxxxx0000xxxx'], # v6
# ['shadd16',  '____01100011xxxxxxxxxxxx0001xxxx'], # v6
# ['shadd8',   '____01100011xxxxxxxxxxxx1001xxxx'], # v6
# ['shaddsubx','____01100011xxxxxxxxxxxx0011xxxx'], # v6
# ['shsub16',  '____01100011xxxxxxxxxxxx0111xxxx'], # v6
# ['shsub8',   '____01100011xxxxxxxxxxxx1111xxxx'], # v6
# ['shsubaddx','____01100011xxxxxxxxxxxx0101xxxx'], # v6
# ['smlad',    '____01110000xxxxxxxxxxxx00x1xxxx'], # v6
  ['smlal',    '____0000111xxxxxxxxxxxxx1001xxxx'],
# ['smlald',   '____01110100xxxxxxxxxxxx00x1xxxx'], # v6

#?['smla_xy',  '____00010000xxxxxxxxxxxx1xx0xxxx'],
#?['smlal_xy', '____00010100xxxxxxxxxxxx1xx0xxxx'],
#?['smlaw_y',  '____00010010xxxxxxxxxxxx1x00xxxx'],
# ['smlsd',    '____01110000xxxxxxxxxxxx01x1xxxx'], # v6
# ['smlsld',   '____01110100xxxxxxxxxxxx01x1xxxx'], # v6
# ['smmla',    '____01110101xxxxxxxxxxxx00x1xxxx'], # v6
# ['smmls',    '____01110101xxxxxxxxxxxx11x1xxxx'], # v6
# ['smmul',    '____01110101xxxx1111xxxx00x1xxxx'], # v6
# ['smuad',    '____01110000xxxx1111xxxx00x1xxxx'], # v6
  ['smull',    '____0000110xxxxxxxxxxxxx1001xxxx'],
#?['smul_xy',  '____00010110xxxxxxxxxxxx1xx0xxxx'],
#?['smulw',    '____00010010xxxxxxxxxxxx1x10xxxx'],
# ['smusd',    '____01110000xxxx1111xxxx01x1xxxx'], # v6
# ['srs',      '1111100xx1x01101xxxx0101xxxxxxxx'], # v6
# ['ssat',     '____0110101xxxxxxxxxxxxxxx01xxxx'], # v6
# ['ssat16',   '____01101010xxxxxxxxxxxx0011xxxx'], # v6
# ['ssub16',   '____01100001xxxxxxxxxxxx0111xxxx'], # v6
# ['ssub8',    '____01100001xxxxxxxxxxxx1111xxxx'], # v6
# ['ssubaddx', '____01100001xxxxxxxxxxxx0101xxxx'], # v6
  ['stc',      '____110xxxx0xxxxxxxxxxxxxxxxxxxx'],
# ['stc2',     '1111110xxxx0xxxxxxxxxxxxxxxxxxxx'], # v6
  ['stm1',     '____110xx0x0xxxxxxxxxxxxxxxxxxxx'],
  ['stm2',     '____100xx100xxxxxxxxxxxxxxxxxxxx'],
  ['str',      '____01xxx0x0xxxxxxxxxxxxxxxxxxxx'],
  ['strb',     '____01xxx1x0xxxxxxxxxxxxxxxxxxxx'],
  ['strbt',    '____01x0x110xxxxxxxxxxxxxxxxxxxx'],
#?['strd',     '____000xxxx0xxxxxxxxxxxx1111xxxx'],
# ['strex',    '____00011000xxxxxxxxxxxx1001xxxx'], # v6

  ['strh',     '____000xxxx0xxxxxxxxxxxx1011xxxx'],
  ['strt',     '____01x0x010xxxxxxxxxxxxxxxxxxxx'],
  ['sub',      '____00x0010xxxxxxxxxxxxxxxxxxxxx'],
  ['swi',      '____1111xxxxxxxxxxxxxxxxxxxxxxxx'],
  ['swp',      '____00010000xxxxxxxxxxxx1001xxxx'],
  ['swpb',     '____00010100xxxxxxxxxxxx1001xxxx'],
# ['sxtb',     '____011010101111xxxxxxxx0111xxxx'], # v6
# ['sxtb16',   '____011010001111xxxxxxxx0111xxxx'], # v6
# ['sxth',     '____011010111111xxxxxxxx0111xxxx'], # v6
# ['sxtab',    '____01101010xxxxxxxxxxxx0111xxxx'], # v6
# ['sxtab16',  '____01101000xxxxxxxxxxxx0111xxxx'], # v6
# ['sxtah',    '____01101011xxxxxxxxxxxx0111xxxx'], # v6
  ['teq',      '____00x10011xxxxxxxxxxxxxxxxxxxx'],
  ['tst',      '____00x10001xxxxxxxxxxxxxxxxxxxx'],
# ['uadd16',   '____01100101xxxxxxxxxxxx0001xxxx'], # v6
# ['uadd8',    '____01100101xxxxxxxxxxxx1001xxxx'], # v6
# ['uadd8subx','____01100101xxxxxxxxxxxx0011xxxx'], # v6
# ['uhadd16',  '____01100111xxxxxxxxxxxx0001xxxx'], # v6
# ['uhadd8',   '____01100111xxxxxxxxxxxx1001xxxx'], # v6
# ['uhaddsubx','____01100111xxxxxxxxxxxx0011xxxx'], # v6
# ['uhsub16',  '____01100111xxxxxxxxxxxx0111xxxx'], # v6
# ['uhsub8',   '____01100111xxxxxxxxxxxx1111xxxx'], # v6
# ['uhsubaddx','____01100111xxxxxxxxxxxx0101xxxx'], # v6
# ['umaal',    '____00000100xxxxxxxxxxxx1001xxxx'], # v6
  ['umlal',    '____0000101xxxxxxxxxxxxx1001xxxx'],
  ['umull',    '____0000100xxxxxxxxxxxxx1001xxxx'],
# ['uqadd16',  '____01100110xxxxxxxxxxxx0001xxxx'], # v6
# ['uqadd8',   '____01100110xxxxxxxxxxxx1001xxxx'], # v6
# ['uqaddsubx','____01100110xxxxxxxxxxxx0011xxxx'], # v6
# ['uqsub16',  '____01100110xxxxxxxxxxxx0111xxxx'], # v6
# ['uqsub8',   '____01100110xxxxxxxxxxxx1111xxxx'], # v6
# ['uqsubaddx','____01100110xxxxxxxxxxxx0101xxxx'], # v6
# ['usad8',    '____01111000xxxx1111xxxx0001xxxx'], # v6
# ['usada8',   '____01111000xxxxxxxxxxxx0001xxxx'], # v6
# ['usat',     '____0110111xxxxxxxxxxxxxxx01xxxx'], # v6
# ['usat16',   '____01101110xxxxxxxxxxxx0011xxxx'], # v6
# ['usub16',   '____01100101xxxxxxxxxxxx0111xxxx'], # v6
# ['usub8',    '____01100101xxxxxxxxxxxx1111xxxx'], # v6
# ['usubaddx', '____01100101xxxxxxxxxxxx0101xxxx'], # v6
# ['uxtb',     '____011011101111xxxxxxxx0111xxxx'], # v6
# ['uxtb16',   '____011011001111xxxxxxxx0111xxxx'], # v6
# ['uxtab',    '____01101110xxxxxxxxxxxx0111xxxx'], # v6
# ['uxtab16',  '____01101100xxxxxxxxxxxx0111xxxx'], # v6
# ['uxtah',    '____01101111xxxxxxxxxxxx0111xxxx'], # v6
]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_nop( s, inst ):
  s.pc += 4

#-----------------------------------------------------------------------
# adc
#-----------------------------------------------------------------------
def execute_adc( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, _ = s.rf[ rn( inst ) ], shifter_operand( inst )
    result  = a + b + s.C
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = carry_from( result )
      s.V = overflow_from_add( a, b, result )
  s.pc += 4

#-----------------------------------------------------------------------
# add
#-----------------------------------------------------------------------
def execute_add( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, _  = s.rf[ rn( inst ) ], shifter_operand( inst )
    result   = a + b
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = carry_from( result )
      s.V = overflow_from_add( a, b, result )
  s.pc += 4

#-----------------------------------------------------------------------
# and
#-----------------------------------------------------------------------
def execute_and( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, cout = s.rf[ rn( inst ) ], shifter_operand( inst )
    result     = a & b
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V
  s.pc += 4

#-----------------------------------------------------------------------
# b
#-----------------------------------------------------------------------
def execute_b( s, inst ):
  raise Exception('"b" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    s.pc += sign_extend_30( offset_24( isnt ) << 2 )
    return
  s.pc += 4

#-----------------------------------------------------------------------
# bl
#-----------------------------------------------------------------------
def execute_bl( s, inst ):
  raise Exception('"bl" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    s.rf[ reg_map['lr'] ] = s.pc + 4
    s.pc += sign_extend_30( offset_24( isnt ) << 2 )
    return
  s.pc += 4

#-----------------------------------------------------------------------
# bic
#-----------------------------------------------------------------------
def execute_bic( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, cout = s.rf[ rn( inst ) ], shifter_operand( inst )
    result     = a & trim_32(~b)
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V
  s.pc += 4

#-----------------------------------------------------------------------
# bkpt
#-----------------------------------------------------------------------
def execute_bkpt( s, inst ):
  raise Exception('"bkpt" instruction unimplemented!')
  s.pc += 4

#-----------------------------------------------------------------------
# blx1
#-----------------------------------------------------------------------
def execute_blx1( s, inst ):
  raise Exception('"blx" instruction unimplemented!')
  s.pc += 4

#-----------------------------------------------------------------------
# blx2
#-----------------------------------------------------------------------
def execute_blx2( s, inst ):
  raise Exception('"blx2" instruction unimplemented!')
  s.pc += 4

#-----------------------------------------------------------------------
# bx
#-----------------------------------------------------------------------
def execute_bx( s, inst ):
  if condition_passed( s, cond(inst) ):
    s.T  = s.rf[ rm(inst) ] & 0x00000001
    s.pc = s.rf[ rm(inst) ] & 0xFFFFFFFE
    if s.T:
      raise Exception( "Entering THUMB mode! Unsupported!")
  s.pc += 4

#-----------------------------------------------------------------------
# cdp
#-----------------------------------------------------------------------
def execute_cdp( s, inst ):
  raise Exception('"cdp" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# clz
#-----------------------------------------------------------------------
def execute_clz( s, inst ):
  raise Exception('"clz" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# cmn
#-----------------------------------------------------------------------
def execute_cmn( s, inst ):
  raise Exception('"cmn" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    a, b = s.rf[ rn(inst) ], shifter_operand( inst )
    result = a + b

    s.N = (result >> 31)&1
    s.Z = trim_32( result ) == 0
    s.C = carry_from( result )
    s.V = overflow_from_add( a, b, result )
  s.pc += 4

#-----------------------------------------------------------------------
# cmp
#-----------------------------------------------------------------------
def execute_cmp( s, inst ):
  raise Exception('"cmp" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    a, b = s.rf[ rn(inst) ], shifter_operand( inst )
    result = a - b

    s.N = (result >> 31)&1
    s.Z = trim_32( result ) == 0
    s.C = not borrow_from( result )
    s.V = overflow_from_sub( b, a, result )
  s.pc += 4

#-----------------------------------------------------------------------
# eor
#-----------------------------------------------------------------------
def execute_eor( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, cout = s.rf[ rn( inst ) ], shifter_operand( inst )
    result     = a ^ b
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V
  s.pc += 4

#-----------------------------------------------------------------------
# ldc
#-----------------------------------------------------------------------
def execute_ldc( s, inst ):
  raise Exception('"ldc" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# ldc2
#-----------------------------------------------------------------------
def execute_ldc2( s, inst ):
  raise Exception('"ldc2" instruction unimplemented!')
  s.pc += 4

#-----------------------------------------------------------------------
# ldm1
#-----------------------------------------------------------------------
def execute_ldm1( s, inst ):
  if condition_passed( s, cond(inst) ):

    addr, end_addr = addressing_mode_4( s, inst )
    register_list   = inst & 0xFF

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    for i in range(15):
      if register_list & 0b1:
        s.rf[ i ] = s.read( addr, 4 )
        addr += 4
      register_list >>= 1

    if register_list & 0b1:  # reg 15
      s.pc = s.read( addr, 4 ) & 0xFFFFFFFE
      s.T  = s.pc & 0b1
      if s.T: raise Exception( "Entering THUMB mode! Unsupported!")

    assert end_addr == addr - 4

  s.pc += 4

#-----------------------------------------------------------------------
# ldm2
#-----------------------------------------------------------------------
def execute_ldm2( s, inst ):
  raise Exception('"ldm2" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# ldm3
#-----------------------------------------------------------------------
def execute_ldm3( s, inst ):
  raise Exception('"ldm3" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# ldr
#-----------------------------------------------------------------------
def execute_ldr( s, inst ):
  if condition_passed( s, cond(inst) ):

    addr, end_addr = addressing_mode_2( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    # TODO: handle memory alignment?
    # CP15_reg1_Ubit checks if the MMU is enabled
    # if (CP15_reg1_Ubit == 0):
    #   data = Memory[address,4] Rotate_Right (8 * address[1:0])
    # else
    #   data = Memory[address,4]

    data = s.mem.read( addr, 4 )

    if rd(inst) == 15:
      s.pc = data & 0xFFFFFFFE
      s.T  = s.pc & 0b1
    else:
      s.rf[ rd(inst) ] = data

  s.pc += 4

#-----------------------------------------------------------------------
# ldrb
#-----------------------------------------------------------------------
def execute_ldrb( s, inst ):
  if condition_passed( s, cond(inst) ):
    if rd(inst) == 15: raise Exception('UNPREDICTABLE')

    addr, end_addr = addressing_mode_2( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    s.rf[ rd(inst) ] = s.mem.read( addr, 1 )

  s.pc += 4

#-----------------------------------------------------------------------
# ldrbt
#-----------------------------------------------------------------------
def execute_ldrbt( s, inst ):
  raise Exception('"ldrbt" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# ldrh
#-----------------------------------------------------------------------
def execute_ldrh( s, inst ):
  if condition_passed( s, cond(inst) ):
    if rd(inst) == 15: raise Exception('UNPREDICTABLE')

    addr, end_addr = addressing_mode_2( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    # TODO: handle memory alignment?
    # CP15_reg1_Ubit checks if the MMU is enabled
    # if (CP15_reg1_Ubit == 0):
    #   data = Memory[address,4] Rotate_Right (8 * address[1:0])
    # else
    #   data = Memory[address,4]

    s.rf[ rd(inst) ] = s.mem.read( addr, 2 )

  s.pc += 4

#-----------------------------------------------------------------------
# ldrsb
#-----------------------------------------------------------------------
def execute_ldrsb( s, inst ):
  raise Exception('"ldsb" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# ldrsh
#-----------------------------------------------------------------------
def execute_ldsh( s, inst ):
  raise Exception('"ldrsh" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# ldrt
#-----------------------------------------------------------------------
def execute_ldrt( s, inst ):
  raise Exception('"ldrt" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# mcr
#-----------------------------------------------------------------------
def execute_mcr( s, inst ):
  raise Exception('"mcr" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# mcr2
#-----------------------------------------------------------------------
def execute_mcr2( s, inst ):
  raise Exception('"mcr2" instruction unimplemented!')
  s.pc += 4

#-----------------------------------------------------------------------
# mcrr
#-----------------------------------------------------------------------
def execute_mcrr( s, inst ):
  raise Exception('"mcrr" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# mcrr2
#-----------------------------------------------------------------------
def execute_mcrr2( s, inst ):
  raise Exception('"mcrr2" instruction unimplemented!')
  s.pc += 4

#-----------------------------------------------------------------------
# mla
#-----------------------------------------------------------------------
def execute_mla( s, inst ):
  if condition_passed( s, cond(inst) ):
    if rd(inst) == 15: raise Exception('UNPREDICTABLE')
    if rm(inst) == 15: raise Exception('UNPREDICTABLE')
    if rs(inst) == 15: raise Exception('UNPREDICTABLE')
    if rn(inst) == 15: raise Exception('UNPREDICTABLE')

    Rm, Rf, Rn  = s.rf[ rm(inst) ], s.rf[ rs(inst) ], s.rf[ rn(inst) ]
    result      = trim_32(Rm * Rs + Rn)
    s.rf[ rd( inst ) ] = result

    if s.S:
      s.N = (result >> 31)&1
      s.Z = result == 0

  s.pc += 4

#-----------------------------------------------------------------------
# mov
#-----------------------------------------------------------------------
def execute_mov( s, inst ):
  if condition_passed( s, cond(inst) ):
    if rd(inst) == 15: raise Exception('UNPREDICTABLE')
    if rm(inst) == 15: raise Exception('UNPREDICTABLE')
    if rs(inst) == 15: raise Exception('UNPREDICTABLE')

    result, cout = shifter_operand( inst )
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V
  s.pc += 4

#-----------------------------------------------------------------------
# mrc
#-----------------------------------------------------------------------
def execute_mrc( s, inst ):
  raise Exception('"mrc" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# mrc2
#-----------------------------------------------------------------------
def execute_mrc2( s, inst ):
  raise Exception('"mrc2" instruction unimplemented!')
  s.pc += 4

#-----------------------------------------------------------------------
# mrs
#-----------------------------------------------------------------------
def execute_mrs( s, inst ):
  raise Exception('"mrs" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# msr
#-----------------------------------------------------------------------
def execute_msr( s, inst ):
  raise Exception('"msr" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# mul
#-----------------------------------------------------------------------
def execute_mul( s, inst ):
  raise Exception('"mul" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    Rm, Rs = s.rf[ rm(inst) ], s.rf[ rs(inst) ]
    result = trim_32(Rm * Rs)
    s.rf[ rd( inst ) ] = result

    if s.S:
      if rd(inst) == 15: raise Exception('UNPREDICTABLE')
      if rm(inst) == 15: raise Exception('UNPREDICTABLE')
      if rs(inst) == 15: raise Exception('UNPREDICTABLE')
      s.N = (result >> 31)&1
      s.Z = result == 0
  s.pc += 4

#-----------------------------------------------------------------------
# mvn
#-----------------------------------------------------------------------
def execute_mvn( s, inst ):
  if condition_passed( s, cond(inst) ):
    result = trim_32( ~shifter_operand( inst )[0] )
    s.rf[ rd( inst ) ] = result

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V
  s.pc += 4

#-----------------------------------------------------------------------
# orr
#-----------------------------------------------------------------------
def execute_orr( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, cout = s.rf[ rn( inst ) ], shifter_operand( inst )
    result     = a | b
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V
  s.pc += 4

#-----------------------------------------------------------------------
# rsb
#-----------------------------------------------------------------------
def execute_rsb( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, _ = s.rf[ rn( inst ) ], shifter_operand( inst )
    result  = b - a
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( b, a, result )
  s.pc += 4

#-----------------------------------------------------------------------
# rsc
#-----------------------------------------------------------------------
def execute_rsc( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, _ = s.rf[ rn( inst ) ], shifter_operand( inst )
    result  = b - a - (not s.C)
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( b, a, result )
  s.pc += 4

#-----------------------------------------------------------------------
# sbc
#-----------------------------------------------------------------------
def execute_sbc( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, _ = s.rf[ rn( inst ) ], shifter_operand( inst )
    result  = a - b - (not s.C)
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( a, b, result )
  s.pc += 4

#-----------------------------------------------------------------------
# smlal
#-----------------------------------------------------------------------
def execute_smlal( s, inst ):
  raise Exception('"smlal" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# smull
#-----------------------------------------------------------------------
def execute_smull( s, inst ):
  raise Exception('"smull" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# stc
#-----------------------------------------------------------------------
def execute_stc( s, inst ):
  raise Exception('"stc" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# stm1
#-----------------------------------------------------------------------
def execute_stm1( s, inst ):
  if condition_passed( s, cond(inst) ):
    addr, end_addr = addressing_mode_4( s, inst )
    register_list   = inst & 0xFF

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    for i in range(15):
      if register_list & 0b1:
        s.write( addr, 4, s.rf[i] )
        addr += 4
      register_list >>= 1

    if register_list & 0b1:  # reg 15
      s.pc = s.read( addr, 4 ) & 0xFFFFFFFE
      s.T  = s.pc & 0b1
      if s.T: raise Exception( "Entering THUMB mode! Unsupported!")

    assert end_addr == addr - 4
  s.pc += 4

#-----------------------------------------------------------------------
# stm2
#-----------------------------------------------------------------------
def execute_stm2( s, inst ):
  raise Exception('"stm2" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# str
#-----------------------------------------------------------------------
def execute_str( s, inst ):
  raise Exception('"str" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# strb
#-----------------------------------------------------------------------
def execute_strb( s, inst ):
  raise Exception('"strb" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# strbt
#-----------------------------------------------------------------------
def execute_strbt( s, inst ):
  raise Exception('"strbt" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# strh
#-----------------------------------------------------------------------
def execute_strh( s, inst ):
  raise Exception('"strh" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# strt
#-----------------------------------------------------------------------
def execute_strt( s, inst ):
  raise Exception('"strt" instruction unimplemented!')
  s.pc += 4

#-----------------------------------------------------------------------
# sub
#-----------------------------------------------------------------------
def execute_sub( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b, _ = s.rf[ rn( inst ) ], shifter_operand( inst )
    result  = a - b
    s.rf[ rd( inst ) ] = trim_32( result )

    if s.S:
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( a, b, result )
  s.pc += 4

#-----------------------------------------------------------------------
# swi
#-----------------------------------------------------------------------
def execute_swi( s, inst ):
  raise Exception('"swi" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# swp
#-----------------------------------------------------------------------
def execute_swp( s, inst ):
  raise Exception('"swp" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# swpb
#-----------------------------------------------------------------------
def execute_swpb( s, inst ):
  raise Exception('"swpb" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# teq
#-----------------------------------------------------------------------
def execute_teq( s, inst ):
  raise Exception('"teq" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# tst
#-----------------------------------------------------------------------
def execute_tst( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, b   = s.rf[ rn( inst ) ], shifter_operand( inst )
    result = a & b
    raise Exception('Implement tst')

    if s.S:
      s.N = result &  0x80000000
      s.Z = trim_32( result ) == 0
      s.C = carry_from( a, b, result )
      # TODO: handle rd(inst) == 15
  s.pc += 4

#-----------------------------------------------------------------------
# umlal
#-----------------------------------------------------------------------
def execute_umlal( s, inst ):
  raise Exception('"umlal" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# umull
#-----------------------------------------------------------------------
def execute_umull( s, inst ):
  raise Exception('"umull" instruction unimplemented!')
  if condition_passed( s, cond(inst) ):
    pass
  s.pc += 4

#-----------------------------------------------------------------------
# Create Decode Table
#-----------------------------------------------------------------------

inst_nbits = len( encodings[0][1] )

def split_encodings( enc ):
  return [x for x in re.split( '(x*)', enc ) if x]

bit_fields = [ split_encodings( enc ) for inst, enc in encodings ]

decoder = ''
for i, inst in enumerate( bit_fields ):
  #print i, encodings[i][0], inst
  bit = 0
  conditions = []
  for field in reversed( inst ):
    nbits = len( field )
    if field[0] != 'x':
      mask = (1 << nbits) - 1
      cond = '(inst >> {}) & 0x{:X} == 0b{}'.format( bit, mask, field )
      conditions.append( cond )
    bit += nbits
  decoder += 'if   ' if i == 0 else '  elif '
  decoder += ' and '.join( reversed(conditions) ) + ':\n'
  decoder += '    return execute_{}\n'.format( encodings[i][0] )

source = py.code.Source('''
@elidable
def decode( inst ):
  {decoder_tree}
  else:
    raise Exception('Invalid instruction 0x%x!' % inst )
'''.format( decoder_tree = decoder ))
#print source
exec source.compile() in globals()


