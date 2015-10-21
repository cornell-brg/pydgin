#=======================================================================
# isa.py
#=======================================================================

# common bitwise utils
from pydgin.utils import (
  trim_32,
  trim_16,
  trim_8,
  sext_16,
  sext_8,
  signed,
)
# arm-specific utils
from utils import (
  shifter_operand,
  condition_passed,
  carry_from,
  borrow_from,
  overflow_from_add,
  overflow_from_sub,
  sext_30,
  addressing_mode_2,
  addressing_mode_3,
  addressing_mode_4,
)

from instruction import *
from pydgin.misc import create_risc_decoder, FatalError

from pydgin.jit import unroll_safe

#=======================================================================
# Register Definitions
#=======================================================================

reg_map = {

  'r0'   :  0,   'r1'   :  1,   'r2'   :  2,   'r3'   :  3,
  'r4'   :  4,   'r5'   :  5,   'r6'   :  6,   'r7'   :  7,
  'r8'   :  8,   'r9'   :  9,   'r10'  : 10,   'r11'  : 11,
  'r12'  : 12,   'r13'  : 13,   'r14'  : 14,   'r15'  : 15,

  # http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0473c/CJAJBFHC.html
  # http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0041c/ch09s02s02.html
  # http://msdn.microsoft.com/en-us/library/aa448762.aspx

  'a1'   :  0,   'a2'   :  1,   'a3'   :  2,   'a4'   :  3, # scratch  registers
  'v1'   :  4,   'v2'   :  5,   'v3'   :  6,   'v4'   :  7, # variable registers
  'v5'   :  8,   'v6'   :  9,   'v7'   : 10,   'v8'   : 11, # variable registers

  'sb'   :  9,  # stack base
  'sl'   : 10,  # stack limit
  'fp'   : 11,  # frame pointer
  'ip'   : 12,  # intra-procedure call scratch
  'sp'   : 13,  # stack pointer
  'lr'   : 14,  # link register
  'pc'   : 15,  # pc
  # NOTE: in ARM the PC is address of the current instruction being
  #       executed + 8!! That means for a given cycle in our simulator,
  #       PC read by fetch and PC read by execute need different values.
  #       Best way to do this?

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
# NOTE: PUSH and POP are synonyms for STMDB and LDM (or LDMIA), with the
# base register sp (r13), and the adjusted address written back to the
# base register. PUSH and POP are the preferred mnemonic in these cases.
# Registers are stored on the stack in numerical order, with the lowest
# numbered register at the lowest address.
#
# http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0204j/Babefbce.html
#
# NOTE: LDM/STM have alternative names depending on addressing mode
# (including LDMIA and STMDB).  See: ARM DDI 0100I, pg. A5-48
#
encodings = [
  ['nop',      '00000000000000000000000000000000'],

  # TODO: These instructions have manually been moved to avoid incorrect
  # decodings caused by encoding ambiguity. Ideally our decoder generator
  # would be able to handle this automatically!
  ['mul',      'xxxx0000000xxxxx0000xxxx1001xxxx'], # ambiguous with and
  ['strh',     'xxxx000xxxx0xxxxxxxxxxxx1011xxxx'], # ambiguous with orr
  ['ldrh',     'xxxx000xxxx1xxxxxxxxxxxx1011xxxx'], # ambiguous with bic
  ['ldrsb',    'xxxx000xxxx1xxxxxxxxxxxx1101xxxx'], # ambiguous with bic
  ['ldrsh',    'xxxx000xxxx1xxxxxxxxxxxx1111xxxx'], # ambiguous with bic
  ['mla',      'xxxx0000001xxxxxxxxxxxxx1001xxxx'], # ambiguous with eor
  ['umull',    'xxxx0000100xxxxxxxxxxxxx1001xxxx'], # ambiguous with add
  ['umlal',    'xxxx0000101xxxxxxxxxxxxx1001xxxx'], # ambiguous with adc
  ['smlal',    'xxxx0000111xxxxxxxxxxxxx1001xxxx'], # ambiguous with rsc
  ['smull',    'xxxx0000110xxxxxxxxxxxxx1001xxxx'], # ambiguous with sbc

  ['adc',      'xxxx00x0101xxxxxxxxxxxxxxxxxxxxx'], # v4
  ['add',      'xxxx00x0100xxxxxxxxxxxxxxxxxxxxx'], # v4
  ['and',      'xxxx00x0000xxxxxxxxxxxxxxxxxxxxx'], # v4
  ['b',        'xxxx1010xxxxxxxxxxxxxxxxxxxxxxxx'], # v4
  ['bl',       'xxxx1011xxxxxxxxxxxxxxxxxxxxxxxx'], # v4
  ['bic',      'xxxx00x1110xxxxxxxxxxxxxxxxxxxxx'], # v4
  ['bkpt',     '111000010010xxxxxxxxxxxx0111xxxx'], # v5T
  ['blx1',     '1111101xxxxxxxxxxxxxxxxxxxxxxxxx'], # v5T
  ['blx2',     'xxxx000100101111111111110011xxxx'], # v5T
  ['bx',       'xxxx000100101111111111110001xxxx'], # v4T
#?['bxj',      'xxxx000100101111111111110010xxxx'], # v5TEJ
  ['cdp',      'xxxx1110xxxxxxxxxxxxxxxxxxx0xxxx'], # v4
  ['clz',      'xxxx000101101111xxxx11110001xxxx'], # v5T
  ['cmn',      'xxxx00x10111xxxx0000xxxxxxxxxxxx'], # v4
  ['cmp',      'xxxx00x10101xxxx0000xxxxxxxxxxxx'], # v4
# ['cps',      '111100010000xxx00000000xxxx0xxxx'], # v6
# ['cpy',      'xxxx000110100000xxxx00000000xxxx'], # v6
  ['eor',      'xxxx00x0001xxxxxxxxxxxxxxxxxxxxx'], # v4
  ['ldc',      'xxxx110xxxx1xxxxxxxxxxxxxxxxxxxx'], # v4
  ['ldc2',     '1111110xxxx1xxxxxxxxxxxxxxxxxxxx'], # v5T
  ['ldm1',     'xxxx100xx0x1xxxxxxxxxxxxxxxxxxxx'], # v4
  ['ldm2',     'xxxx100xx101xxxx0xxxxxxxxxxxxxxx'], # v4
  ['ldm3',     'xxxx100xx1x1xxxx1xxxxxxxxxxxxxxx'], # v4
  ['ldr',      'xxxx01xxx0x1xxxxxxxxxxxxxxxxxxxx'], # v4

  ['ldrb',     'xxxx01xxx1x1xxxxxxxxxxxxxxxxxxxx'], # v4
  ['ldrbt',    'xxxx01x0x111xxxxxxxxxxxxxxxxxxxx'], # v4
#?['ldrd',     'xxxx000puiw0xxxxxxxxxxxx1101xxxx'], # v5TE
# ['ldrex',    'xxxx000110001xxxxxxx111110011111'], # v6
# ['ldrh',     'xxxx000xxxx1xxxxxxxxxxxx1011xxxx'], # v4, SEE ABOVE
# ['ldrsb',    'xxxx000xxxx1xxxxxxxxxxxx1101xxxx'], # v4, SEE ABOVE
# ['ldrsh',    'xxxx000xxxx1xxxxxxxxxxxx1111xxxx'], # v4, SEE ABOVE
  ['ldrt',     'xxxx01x0x011xxxxxxxxxxxxxxxxxxxx'], # v4
  ['mcr',      'xxxx1110xxx0xxxxxxxxxxxxxxx1xxxx'], # v4
  ['mcr2',     '11111110xxx0xxxxxxxxxxxxxxx1xxxx'], # v5T
  ['mcrr',     'xxxx11000100xxxxxxxxxxxxxxxxxxxx'], # v5TE
  ['mcrr2',    '111111000100xxxxxxxxxxxxxxxxxxxx'], # v6
# ['mla',      'xxxx0000001xxxxxxxxxxxxx1001xxxx'], # v4, SEE ABOVE
  ['mov',      'xxxx00x1101x0000xxxxxxxxxxxxxxxx'], # v4
  ['mrc',      'xxxx1110xxx1xxxxxxxxxxxxxxx1xxxx'], # v4
  ['mrc2',     '11111110xxx1xxxxxxxxxxxxxxx1xxxx'], # v5T
#?['mrrc',     'xxxx11000101xxxxxxxxxxxxxxxxxxxx'], # v5TE
# ['mrrc2',    '111111000101xxxxxxxxxxxxxxxxxxxx'], # v6
  ['mrs',      'xxxx00010x001111xxxx000000000000'], # v4
  ['msr',      'xxxx00x10x10xxxx1111xxxxxxxxxxxx'], # v4, TODO
# ['mul',      'xxxx0000000xxxxx0000xxxx1001xxxx'], # v4, SEE ABOVE
  ['mvn',      'xxxx00x1111x0000xxxxxxxxxxxxxxxx'], # v4
  ['orr',      'xxxx00x1100xxxxxxxxxxxxxxxxxxxxx'], # v4
# ['pkhbt',    'xxxx01101000xxxxxxxxxxxxx001xxxx'], # v6
# ['pkhtb',    'xxxx01101000xxxxxxxxxxxxx101xxxx'], # v6

#?['pld',      '111101x1x101xxxx1111xxxxxxxxxxxx'], # v5TE
#?['qadd',     'xxxx00010000xxxxxxxx00000101xxxx'], # v5TE
# ['qadd16',   'xxxx01100010xxxxxxxx11110001xxxx'], # v6
# ['qadd8',    'xxxx01100010xxxxxxxx11111001xxxx'], # v6
# ['qaddsubx', 'xxxx01100010xxxxxxxx11110011xxxx'], # v6
#?['qdadd',    'xxxx00010100xxxxxxxx00000101xxxx'], # v5TE
#?['qdsub',    'xxxx00010110xxxxxxxx00000101xxxx'], # v5TE
#?['qsub',     'xxxx00010010xxxxxxxx00000101xxxx'], # v5TE
# ['qsub16',   'xxxx01100010xxxxxxxx11110111xxxx'], # v6
# ['qsub8',    'xxxx01100010xxxxxxxx11111111xxxx'], # v6
# ['qsubaddx', 'xxxx01100010xxxxxxxx11110101xxxx'], # v6
# ['rev',      'xxxx011010111111xxxx11110011xxxx'], # v6
# ['rev16',    'xxxx011010111111xxxx11111011xxxx'], # v6
# ['revsh',    'xxxx011011111111xxxx11111011xxxx'], # v6
# ['rfe',      '1111100xx0x1xxxx0000101000000000'], # v6
  ['rsb',      'xxxx00x0011xxxxxxxxxxxxxxxxxxxxx'], # v4
  ['rsc',      'xxxx00x0111xxxxxxxxxxxxxxxxxxxxx'], # v4
# ['sadd16',   'xxxx01100001xxxxxxxx11110001xxxx'], # v6
# ['sadd8',    'xxxx01100001xxxxxxxx11111001xxxx'], # v6
# ['saddsubx', 'xxxx01100001xxxxxxxx11110011xxxx'], # v6
  ['sbc',      'xxxx00x0110xxxxxxxxxxxxxxxxxxxxx'], # v4
# ['sel',      'xxxx01101000xxxxxxxx11111011xxxx'], # v6
# ['setend',   '1111000100000001000000x000000000'], # v6
# ['shadd16',  'xxxx01100011xxxxxxxx11110001xxxx'], # v6
# ['shadd8',   'xxxx01100011xxxxxxxx11111001xxxx'], # v6
# ['shaddsubx','xxxx01100011xxxxxxxx11110011xxxx'], # v6
# ['shsub16',  'xxxx01100011xxxxxxxx11110111xxxx'], # v6
# ['shsub8',   'xxxx01100011xxxxxxxx11111111xxxx'], # v6
# ['shsubaddx','xxxx01100011xxxxxxxx11110101xxxx'], # v6
# ['smlad',    'xxxx01110000xxxxxxxxxxxx00x1xxxx'], # v6
# ['smlal',    'xxxx0000111xxxxxxxxxxxxx1001xxxx'], # v4, SEE ABOVE
# ['smlald',   'xxxx01110100xxxxxxxxxxxx00x1xxxx'], # v6

#?['smla_xy',  'xxxx00010000xxxxxxxxxxxx1xx0xxxx'], # v5TE
#?['smlal_xy', 'xxxx00010100xxxxxxxxxxxx1xx0xxxx'], # v5TE
#?['smlaw_y',  'xxxx00010010xxxxxxxxxxxx1x00xxxx'], # v5TE
# ['smlsd',    'xxxx01110000xxxxxxxxxxxx01x1xxxx'], # v6
# ['smlsld',   'xxxx01110100xxxxxxxxxxxx01x1xxxx'], # v6
# ['smmla',    'xxxx01110101xxxxxxxxxxxx00x1xxxx'], # v6
# ['smmls',    'xxxx01110101xxxxxxxxxxxx11x1xxxx'], # v6
# ['smmul',    'xxxx01110101xxxx1111xxxx00x1xxxx'], # v6
# ['smuad',    'xxxx01110000xxxx1111xxxx00x1xxxx'], # v6
# ['smull',    'xxxx0000110xxxxxxxxxxxxx1001xxxx'], # v4, SEE ABOVE
#?['smul_xy',  'xxxx00010110xxxx0000xxxx1xx0xxxx'], # v5TE
#?['smulw',    'xxxx00010010xxxx0000xxxx1x10xxxx'], # v5TE
# ['smusd',    'xxxx01110000xxxx1111xxxx01x1xxxx'], # v6
# ['srs',      '1111100xx1x0110100000101000xxxxx'], # v6
# ['ssat',     'xxxx0110101xxxxxxxxxxxxxxx01xxxx'], # v6
# ['ssat16',   'xxxx01101010xxxxxxxx11110011xxxx'], # v6
# ['ssub16',   'xxxx01100001xxxxxxxx11110111xxxx'], # v6
# ['ssub8',    'xxxx01100001xxxxxxxx11111111xxxx'], # v6
# ['ssubaddx', 'xxxx01100001xxxxxxxx11110101xxxx'], # v6
  ['stc',      'xxxx110xxxx0xxxxxxxxxxxxxxxxxxxx'], # v4
# ['stc2',     '1111110xxxx0xxxxxxxxxxxxxxxxxxxx'], # v5T
  ['stm1',     'xxxx100xx0x0xxxxxxxxxxxxxxxxxxxx'], # v4
  ['stm2',     'xxxx100xx100xxxxxxxxxxxxxxxxxxxx'], # v4
  ['str',      'xxxx01xxx0x0xxxxxxxxxxxxxxxxxxxx'], # v4
  ['strb',     'xxxx01xxx1x0xxxxxxxxxxxxxxxxxxxx'], # v4
  ['strbt',    'xxxx01x0x110xxxxxxxxxxxxxxxxxxxx'], # v4
#?['strd',     'xxxx000xxxx0xxxxxxxxxxxx1111xxxx'], # v5TE
# ['strex',    'xxxx00011000xxxxxxxx11111001xxxx'], # v6

# ['strh',     'xxxx000xxxx0xxxxxxxxxxxx1011xxxx'], # v4, SEE ABOVE
  ['strt',     'xxxx01x0x010xxxxxxxxxxxxxxxxxxxx'], # v4
  ['sub',      'xxxx00x0010xxxxxxxxxxxxxxxxxxxxx'], # v4
  ['swi',      'xxxx1111xxxxxxxxxxxxxxxxxxxxxxxx'], # v4
  ['swp',      'xxxx00010000xxxxxxxx00001001xxxx'], # v4, Deprecated in v6
  ['swpb',     'xxxx00010100xxxxxxxx00001001xxxx'], # v4, Deprecated in v6
# ['sxtab',    'xxxx01101010xxxxxxxxxx000111xxxx'], # v6
# ['sxtab16',  'xxxx01101000xxxxxxxxxx000111xxxx'], # v6
# ['sxtah',    'xxxx01101011xxxxxxxxxx000111xxxx'], # v6
# ['sxtb',     'xxxx011010101111xxxxxx000111xxxx'], # v6
# ['sxtb16',   'xxxx011010001111xxxxxx000111xxxx'], # v6
# ['sxth',     'xxxx011010111111xxxxxx000111xxxx'], # v6
  ['teq',      'xxxx00x10011xxxx0000xxxxxxxxxxxx'], # v4
  ['tst',      'xxxx00x10001xxxx0000xxxxxxxxxxxx'], # v4
# ['uadd16',   'xxxx01100101xxxxxxxx11110001xxxx'], # v6
# ['uadd8',    'xxxx01100101xxxxxxxx11111001xxxx'], # v6
# ['uadd8subx','xxxx01100101xxxxxxxx11110011xxxx'], # v6
# ['uhadd16',  'xxxx01100111xxxxxxxx11110001xxxx'], # v6
# ['uhadd8',   'xxxx01100111xxxxxxxx11111001xxxx'], # v6
# ['uhaddsubx','xxxx01100111xxxxxxxx11110011xxxx'], # v6
# ['uhsub16',  'xxxx01100111xxxxxxxx11110111xxxx'], # v6
# ['uhsub8',   'xxxx01100111xxxxxxxx11111111xxxx'], # v6
# ['uhsubaddx','xxxx01100111xxxxxxxx11110101xxxx'], # v6
# ['umaal',    'xxxx00000100xxxxxxxxxxxx1001xxxx'], # v6
# ['umlal',    'xxxx0000101xxxxxxxxxxxxx1001xxxx'], # v4, SEE ABOVE
# ['umull',    'xxxx0000100xxxxxxxxxxxxx1001xxxx'], # v4, SEE ABOVE
# ['uqadd16',  'xxxx01100110xxxxxxxx11110001xxxx'], # v6
# ['uqadd8',   'xxxx01100110xxxxxxxx11111001xxxx'], # v6
# ['uqaddsubx','xxxx01100110xxxxxxxx11110011xxxx'], # v6
# ['uqsub16',  'xxxx01100110xxxxxxxx11110111xxxx'], # v6
# ['uqsub8',   'xxxx01100110xxxxxxxx11111111xxxx'], # v6
# ['uqsubaddx','xxxx01100110xxxxxxxx11110101xxxx'], # v6
# ['usad8',    'xxxx01111000xxxx1111xxxx0001xxxx'], # v6
# ['usada8',   'xxxx01111000xxxxxxxxxxxx0001xxxx'], # v6
# ['usat',     'xxxx0110111xxxxxxxxxxxxxxx01xxxx'], # v6
# ['usat16',   'xxxx01101110xxxxxxxx11110011xxxx'], # v6
# ['usub16',   'xxxx01100101xxxxxxxx11110111xxxx'], # v6
# ['usub8',    'xxxx01100101xxxxxxxx11111111xxxx'], # v6
# ['usubaddx', 'xxxx01100101xxxxxxxx11110101xxxx'], # v6
# ['uxtab',    'xxxx01101110xxxxxxxxxx000111xxxx'], # v6
# ['uxtab16',  'xxxx01101100xxxxxxxxxx000111xxxx'], # v6
# ['uxtah',    'xxxx01101111xxxxxxxxxx000111xxxx'], # v6
# ['uxtb',     'xxxx011011101111xxxxxx000111xxxx'], # v6
# ['uxtb16',   'xxxx011011001111xxxxxx000111xxxx'], # v6
# ['uxth',     'xxxx011011111111xxxxxx000111xxxx'], # v6

# the definitions below are the limited subset of v7 to run PyPy JIT
# region
  ['dmb',      '1111010101111111111100000101xxxx'],
  ['movw',     'xxxx00110000xxxxxxxxxxxxxxxxxxxx'],
  ['movt',     'xxxx00110100xxxxxxxxxxxxxxxxxxxx'],
]

PC = reg_map['pc']
LR = reg_map['lr']

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_nop( s, inst ):
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# adc
#-----------------------------------------------------------------------
def execute_adc( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, _) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result  = a + b + s.C
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = carry_from( result )
      s.V = overflow_from_add( a, b, result )

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# add
#-----------------------------------------------------------------------
def execute_add( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, _)  = s.rf[ inst.rn ], shifter_operand( s, inst )
    result   = a + b
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = carry_from( result )
      s.V = overflow_from_add( a, b, result )

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# and
#-----------------------------------------------------------------------
def execute_and( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, cout) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result       = a & b
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# b
#-----------------------------------------------------------------------
def execute_b( s, inst ):
  if condition_passed( s, inst.cond ):
    offset   = signed( sext_30( inst.imm_24 ) << 2 )
    s.rf[PC] = trim_32( s.rf[PC] + offset )
    return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# bl
#-----------------------------------------------------------------------
def execute_bl( s, inst ):
  if condition_passed( s, inst.cond ):
    s.rf[LR] = trim_32( s.fetch_pc() + 4 )
    offset   = signed( sext_30( inst.imm_24 ) << 2 )
    s.rf[PC] = trim_32( s.rf[PC] + offset )
    return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# bic
#-----------------------------------------------------------------------
def execute_bic( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, cout) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result       = a & trim_32(~b)
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# bkpt
#-----------------------------------------------------------------------
def execute_bkpt( s, inst ):
  raise FatalError('"bkpt" instruction unimplemented!')
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# blx1
#-----------------------------------------------------------------------
def execute_blx1( s, inst ):
  raise FatalError('Called blx1: Entering THUMB mode! Unsupported')
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# blx2
#-----------------------------------------------------------------------
def execute_blx2( s, inst ):
  if condition_passed( s, inst.cond ):
    s.rf[LR] = trim_32( s.fetch_pc() + 4 )
    s.T      = s.rf[ inst.rm ] & 0x00000001
    s.rf[PC] = s.rf[ inst.rm ] & 0xFFFFFFFE
    if s.T:
      raise FatalError( "Entering THUMB mode! Unsupported!")

  # no pc + 4 on success
  else:
    s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# bx
#-----------------------------------------------------------------------
def execute_bx( s, inst ):
  if condition_passed( s, inst.cond ):
    s.T      = s.rf[ inst.rm ] & 0x00000001
    s.rf[PC] = s.rf[ inst.rm ] & 0xFFFFFFFE
    if s.T:
      raise FatalError( "Entering THUMB mode! Unsupported!")

  # no pc + 4 on success
  else:
    s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# cdp
#-----------------------------------------------------------------------
def execute_cdp( s, inst ):
  raise FatalError('"cdp" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# clz
#-----------------------------------------------------------------------
@unroll_safe
def execute_clz( s, inst ):
  if condition_passed( s, inst.cond ):
    Rm = s.rf[ inst.rm ]

    if Rm == 0:
      s.rf[ inst.rd ] = 32
    else:
      mask = 0x80000000
      leading_zeros = 32
      for x in range(32):
        if mask & Rm:
          leading_zeros = x
          break
        mask >>= 1

      assert leading_zeros != 32
      s.rf[ inst.rd ] = leading_zeros

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# cmn
#-----------------------------------------------------------------------
def execute_cmn( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, _) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result = a + b

    s.N = (result >> 31)&1
    s.Z = trim_32( result ) == 0
    s.C = carry_from( result )
    s.V = overflow_from_add( a, b, result )

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# cmp
#-----------------------------------------------------------------------
def execute_cmp( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, _) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result = a - b

    s.N = (result >> 31)&1
    s.Z = trim_32( result ) == 0
    s.C = not borrow_from( result )
    s.V = overflow_from_sub( a, b, result )

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# dmb
#-----------------------------------------------------------------------
# memory barrier -- implemented as a nop
def execute_dmb( s, inst ):
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# eor
#-----------------------------------------------------------------------
def execute_eor( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, cout) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result       = a ^ b
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldc
#-----------------------------------------------------------------------
def execute_ldc( s, inst ):
  raise FatalError('"ldc" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldc2
#-----------------------------------------------------------------------
def execute_ldc2( s, inst ):
  raise FatalError('"ldc2" instruction unimplemented!')
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldm1
#-----------------------------------------------------------------------
@unroll_safe
def execute_ldm1( s, inst ):
  if condition_passed( s, inst.cond ):
    addr, end_addr = addressing_mode_4( s, inst )
    register_mask  = inst.register_list

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    for i in range(15):
      if register_mask & 0b1:
        s.rf[ i ] = s.mem.read( addr, 4 )
        addr += 4
      register_mask >>= 1

    if register_mask & 0b1:  # reg 15
      s.rf[PC] = s.mem.read( addr, 4 ) & 0xFFFFFFFE
      s.T  = s.rf[PC] & 0b1
      if s.T: raise FatalError( "Entering THUMB mode! Unsupported!")
      assert end_addr == addr
      return

    assert end_addr == addr - 4

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldm2
#-----------------------------------------------------------------------
def execute_ldm2( s, inst ):
  raise FatalError('"ldm2" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldm3
#-----------------------------------------------------------------------
def execute_ldm3( s, inst ):
  raise FatalError('"ldm3" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldr
#-----------------------------------------------------------------------
def execute_ldr( s, inst ):
  if condition_passed( s, inst.cond ):

    addr = addressing_mode_2( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    # TODO: handle memory alignment?
    # CP15_reg1_Ubit checks if the MMU is enabled
    # if (CP15_reg1_Ubit == 0):
    #   data = Memory[address,4] Rotate_Right (8 * address[1:0])
    # else
    #   data = Memory[address,4]

    data = s.mem.read( addr, 4 )

    if inst.rd == 15:
      s.rf[PC] = data & 0xFFFFFFFE
      s.T      = data & 0b1
      return
    else:
      s.rf[ inst.rd ] = data

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldrb
#-----------------------------------------------------------------------
def execute_ldrb( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')

    addr = addressing_mode_2( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    s.rf[ inst.rd ] = s.mem.read( addr, 1 )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldrbt
#-----------------------------------------------------------------------
def execute_ldrbt( s, inst ):
  raise FatalError('"ldrbt" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldrh
#-----------------------------------------------------------------------
def execute_ldrh( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')

    addr = addressing_mode_3( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )
    # TODO: alignment fault checking?
    # if (CP15_reg1_Ubit == 0) and address[0] == 0b1:
    #   UNPREDICTABLE

    s.rf[ inst.rd ] = s.mem.read( addr, 2 )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldrsb
#-----------------------------------------------------------------------
def execute_ldrsb( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')

    addr = addressing_mode_3( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )
    # TODO: alignment fault checking?
    # if (CP15_reg1_Ubit == 0) and address[0] == 0b1:
    #   UNPREDICTABLE

    s.rf[ inst.rd ] = sext_8( s.mem.read( addr, 1 ) )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldrsh
#-----------------------------------------------------------------------
def execute_ldrsh( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')

    addr = addressing_mode_3( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )
    # TODO: alignment fault checking?
    # if (CP15_reg1_Ubit == 0) and address[0] == 0b1:
    #   UNPREDICTABLE

    s.rf[ inst.rd ] = sext_16( s.mem.read( addr, 2 ) )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# ldrt
#-----------------------------------------------------------------------
def execute_ldrt( s, inst ):
  raise FatalError('"ldrt" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mcr
#-----------------------------------------------------------------------
def execute_mcr( s, inst ):
  raise FatalError('"mcr" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mcr2
#-----------------------------------------------------------------------
def execute_mcr2( s, inst ):
  raise FatalError('"mcr2" instruction unimplemented!')
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mcrr
#-----------------------------------------------------------------------
def execute_mcrr( s, inst ):
  raise FatalError('"mcrr" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mcrr2
#-----------------------------------------------------------------------
def execute_mcrr2( s, inst ):
  raise FatalError('"mcrr2" instruction unimplemented!')
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mla
#-----------------------------------------------------------------------
def execute_mla( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')
    if inst.rm == 15: raise FatalError('UNPREDICTABLE')
    if inst.rs == 15: raise FatalError('UNPREDICTABLE')
    if inst.rn == 15: raise FatalError('UNPREDICTABLE')

    Rm, Rs, Rd  = s.rf[ inst.rm ], s.rf[ inst.rs ], s.rf[ inst.rd ]
    result      = trim_32(Rm * Rs + Rd)
    s.rf[ inst.rn ] = result

    if inst.S:
      s.N = (result >> 31)&1
      s.Z = result == 0

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mov
#-----------------------------------------------------------------------
def execute_mov( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15 and inst.S:
    # if not CurrentModeHasSPSR(): CPSR = SPSR
    # else:                        UNPREDICTABLE
      raise FatalError('UNPREDICTABLE in user and system mode!')

    result, cout = shifter_operand( s, inst )
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# movt
#-----------------------------------------------------------------------
def execute_movt( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15:
      raise FatalError('UNPREDICTABLE')

    result = ( inst.imm_16 << 16 ) | trim_16( s.rf[ inst.rd ] )
    s.rf[ inst.rd ] = trim_32( result )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# movw
#-----------------------------------------------------------------------
def execute_movw( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15:
      raise FatalError('UNPREDICTABLE')

    result = inst.imm_16
    s.rf[ inst.rd ] = trim_32( result )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mrc
#-----------------------------------------------------------------------
def execute_mrc( s, inst ):
  raise FatalError('"mrc" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mrc2
#-----------------------------------------------------------------------
def execute_mrc2( s, inst ):
  raise FatalError('"mrc2" instruction unimplemented!')
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mrs
#-----------------------------------------------------------------------
def execute_mrs( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.R:
      raise FatalError('Cannot read SPSR in "mrs"')
    else:
      s.rf[ inst.rd ] = s.cpsr()
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# msr
#-----------------------------------------------------------------------
def execute_msr( s, inst ):
  raise FatalError('"msr" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mul
#-----------------------------------------------------------------------
def execute_mul( s, inst ):
  if condition_passed( s, inst.cond ):
    Rm, Rs = s.rf[ inst.rm ], s.rf[ inst.rs ]
    result = trim_32(Rm * Rs)
    s.rf[ inst.rn ] = result

    if inst.S:
      if inst.rn == 15: raise FatalError('UNPREDICTABLE')
      if inst.rm == 15: raise FatalError('UNPREDICTABLE')
      if inst.rs == 15: raise FatalError('UNPREDICTABLE')
      s.N = (result >> 31)&1
      s.Z = result == 0

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# mvn
#-----------------------------------------------------------------------
def execute_mvn( s, inst ):
  if condition_passed( s, inst.cond ):
    a, cout = shifter_operand( s, inst )
    result  = trim_32( ~a )
    s.rf[ inst.rd ] = result

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# orr
#-----------------------------------------------------------------------
def execute_orr( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, cout) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result     = a | b
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# rsb
#-----------------------------------------------------------------------
def execute_rsb( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, _) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result  = b - a
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( b, a, result )

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# rsc
#-----------------------------------------------------------------------
def execute_rsc( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, _) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result  = b - a - (not s.C)
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( b, a, result )

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# sbc
#-----------------------------------------------------------------------
def execute_sbc( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, _) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result  = a - b - (not s.C)
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( a, b, result )

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# smlal
#-----------------------------------------------------------------------
def execute_smlal( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')
    if inst.rm == 15: raise FatalError('UNPREDICTABLE')
    if inst.rs == 15: raise FatalError('UNPREDICTABLE')
    if inst.rn == 15: raise FatalError('UNPREDICTABLE')

    RdHi, RdLo  = inst.rn, inst.rd
    Rm,   Rs    = signed(s.rf[ inst.rm ]), signed(s.rf[ inst.rs ])
    accumulate  = (s.rf[ RdHi ] << 32) | s.rf[ RdLo ]
    result      = (Rm * Rs) + accumulate

    if RdHi == RdLo: raise FatalError('UNPREDICTABLE')

    s.rf[ RdHi ] = trim_32( result >> 32 )
    s.rf[ RdLo ] = trim_32( result )

    if inst.S:
      s.N = (result >> 63)&1
      s.Z = (s.rf[RdHi] == s.rf[RdLo] == 0)
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# smull
#-----------------------------------------------------------------------
def execute_smull( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')
    if inst.rm == 15: raise FatalError('UNPREDICTABLE')
    if inst.rs == 15: raise FatalError('UNPREDICTABLE')
    if inst.rn == 15: raise FatalError('UNPREDICTABLE')

    RdHi, RdLo  = inst.rn, inst.rd
    Rm,   Rs    = signed(s.rf[ inst.rm ]), signed(s.rf[ inst.rs ])
    result      = Rm * Rs

    if RdHi == RdLo: raise FatalError('UNPREDICTABLE')

    s.rf[ RdHi ] = trim_32( result >> 32 )
    s.rf[ RdLo ] = trim_32( result )

    if inst.S:
      s.N = (result >> 63)&1
      s.Z = result == 0
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# stc
#-----------------------------------------------------------------------
def execute_stc( s, inst ):
  raise FatalError('"stc" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# stm1
#-----------------------------------------------------------------------
@unroll_safe
def execute_stm1( s, inst ):
  if condition_passed( s, inst.cond ):
    orig_Rn = s.rf[ inst.rn ]
    addr, end_addr = addressing_mode_4( s, inst )
    register_mask  = inst.register_list

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    for i in range(16):
      if register_mask & 0b1:
        # Note from ISA document page A4-190:
        # If <Rn> is specified in <registers> and base register write-back
        # is specified:
        # - If <Rn> is the lowest-numbered register specified in
        #   <registers>, the original value of <Rn> is stored.
        # - Otherwise, the stored value of <Rn> is UNPREDICTABLE.
        #
        # We check if i is Rn, and if so, we use the original value
        if i == inst.rn:
          s.mem.write( addr, 4, orig_Rn )
        else:
          s.mem.write( addr, 4, s.rf[i] )
        addr += 4
      register_mask >>= 1

    assert end_addr == addr - 4
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# stm2
#-----------------------------------------------------------------------
def execute_stm2( s, inst ):
  raise FatalError('"stm2" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# str
#-----------------------------------------------------------------------
def execute_str( s, inst ):
  if condition_passed( s, inst.cond ):

    addr = addressing_mode_2( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    s.mem.write( addr, 4, s.rf[ inst.rd ] )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# strb
#-----------------------------------------------------------------------
def execute_strb( s, inst ):
  if condition_passed( s, inst.cond ):

    addr = addressing_mode_2( s, inst )

    s.mem.write( addr, 1, trim_8( s.rf[ inst.rd ] ) )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# strbt
#-----------------------------------------------------------------------
def execute_strbt( s, inst ):
  raise FatalError('"strbt" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# strh
#-----------------------------------------------------------------------
def execute_strh( s, inst ):
  if condition_passed( s, inst.cond ):

    addr = addressing_mode_3( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )
    # TODO: alignment fault checking?
    # if (CP15_reg1_Ubit == 0) and address[0] == 0b1:
    #   UNPREDICTABLE

    s.mem.write( addr, 2, s.rf[ inst.rd ] & 0xFFFF )

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# strt
#-----------------------------------------------------------------------
def execute_strt( s, inst ):
  raise FatalError('"strt" instruction unimplemented!')
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# sub
#-----------------------------------------------------------------------
def execute_sub( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, _) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result  = a - b
    s.rf[ inst.rd ] = trim_32( result )

    if inst.S:
      if inst.rd == 15: raise FatalError('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( a, b, result )

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# swi
#-----------------------------------------------------------------------
from syscalls import do_syscall
def execute_swi( s, inst ):
  if condition_passed( s, inst.cond ):
    do_syscall( s )
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# swp
#-----------------------------------------------------------------------
def execute_swp( s, inst ):
  if condition_passed( s, inst.cond ):
    addr = s.rf[ inst.rn ]
    temp = s.mem.read( addr, 4 )
    s.mem.write( addr, 4, s.rf[ inst.rm ] )
    s.rf[ inst.rd ] = temp

  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# swpb
#-----------------------------------------------------------------------
def execute_swpb( s, inst ):
  raise FatalError('"swpb" instruction unimplemented!')
  if condition_passed( s, inst.cond ):
    pass
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# teq
#-----------------------------------------------------------------------
def execute_teq( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, cout) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result = trim_32( a ^ b )

    if inst.S:
      s.N = (result >> 31)&1
      s.Z = result == 0
      s.C = cout

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# tst
#-----------------------------------------------------------------------
def execute_tst( s, inst ):
  if condition_passed( s, inst.cond ):
    a, (b, cout) = s.rf[ inst.rn ], shifter_operand( s, inst )
    result = trim_32( a & b )

    if inst.S:
      s.N = (result >> 31)&1
      s.Z = result == 0
      s.C = cout

    if inst.rd == 15:
      return
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# umlal
#-----------------------------------------------------------------------
def execute_umlal( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')
    if inst.rm == 15: raise FatalError('UNPREDICTABLE')
    if inst.rs == 15: raise FatalError('UNPREDICTABLE')
    if inst.rn == 15: raise FatalError('UNPREDICTABLE')

    RdHi, RdLo  = inst.rn, inst.rd
    Rm,   Rs    = s.rf[ inst.rm ], s.rf[ inst.rs ]
    accumulate  = (s.rf[ RdHi ] << 32) | s.rf[ RdLo ]
    result      = (Rm * Rs) + accumulate

    if RdHi == RdLo: raise FatalError('UNPREDICTABLE')

    s.rf[ RdHi ] = trim_32( result >> 32 )
    s.rf[ RdLo ] = trim_32( result )

    if inst.S:
      s.N = (result >> 63)&1
      s.Z = (s.rf[RdHi] == s.rf[RdLo] == 0)
  s.rf[PC] = s.fetch_pc() + 4

#-----------------------------------------------------------------------
# umull
#-----------------------------------------------------------------------
def execute_umull( s, inst ):
  if condition_passed( s, inst.cond ):
    if inst.rd == 15: raise FatalError('UNPREDICTABLE')
    if inst.rm == 15: raise FatalError('UNPREDICTABLE')
    if inst.rs == 15: raise FatalError('UNPREDICTABLE')
    if inst.rn == 15: raise FatalError('UNPREDICTABLE')

    RdHi, RdLo  = inst.rn, inst.rd
    Rm,   Rs    = s.rf[ inst.rm ], s.rf[ inst.rs ]
    result      = Rm * Rs

    if RdHi == RdLo: raise FatalError('UNPREDICTABLE')

    s.rf[ RdHi ] = trim_32( result >> 32 )
    s.rf[ RdLo ] = trim_32( result )

    if inst.S:
      s.N = (result >> 63)&1
      s.Z = (s.rf[RdHi] == s.rf[RdLo] == 0)
  s.rf[PC] = s.fetch_pc() + 4

#=======================================================================
# Create Decoder
#=======================================================================

decode = create_risc_decoder( encodings, globals(), debug=True )

