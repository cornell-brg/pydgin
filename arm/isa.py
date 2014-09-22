#=======================================================================
# isa.py
#=======================================================================

from utils import (
  shifter_operand,
  trim_32,
  trim_16,
  trim_8,
  condition_passed,
  carry_from,
  borrow_from,
  overflow_from_add,
  overflow_from_sub,
  sign_extend_30,
  sign_extend_half,
  sign_extend_byte,
  signed,
  addressing_mode_2,
  addressing_mode_3,
  addressing_mode_4,
)

from instruction import *
from pydgin.misc import create_risc_decoder

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
  ['mul',      'xxxx0000000xxxxxxxxxxxxx1001xxxx'], # ambiguous with and
  ['strh',     'xxxx000xxxx0xxxxxxxxxxxx1011xxxx'], # ambiguous with orr
  ['ldrh',     'xxxx000xxxx1xxxxxxxxxxxx1011xxxx'], # ambiguous with bic
  ['ldrsh',    'xxxx000xxxx1xxxxxxxxxxxx1111xxxx'], # ambiguous with bic
  ['mla',      'xxxx0000001xxxxxxxxxxxxx1001xxxx'], # ambiguous with eor
  ['umull',    'xxxx0000100xxxxxxxxxxxxx1001xxxx'], # ambiguous with add

  ['adc',      'xxxx00x0101xxxxxxxxxxxxxxxxxxxxx'],
  ['add',      'xxxx00x0100xxxxxxxxxxxxxxxxxxxxx'],
  ['and',      'xxxx00x0000xxxxxxxxxxxxxxxxxxxxx'],
  ['b',        'xxxx1010xxxxxxxxxxxxxxxxxxxxxxxx'],
  ['bl',       'xxxx1011xxxxxxxxxxxxxxxxxxxxxxxx'],
  ['bic',      'xxxx00x1110xxxxxxxxxxxxxxxxxxxxx'],
  ['bkpt',     '111000010010xxxxxxxxxxxx0111xxxx'],
  ['blx1',     '1111101xxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['blx2',     'xxxx00010010xxxxxxxxxxxx0011xxxx'],
  ['bx',       'xxxx00010010xxxxxxxxxxxx0001xxxx'],
#?['bxj',      'xxxx00010010xxxxxxxxxxxx0010xxxx'],
  ['cdp',      'xxxx1110xxxxxxxxxxxxxxxxxxx0xxxx'],
  ['clz',      'xxxx00010110xxxxxxxxxxxx0001xxxx'],
  ['cmn',      'xxxx00x10111xxxxxxxxxxxxxxxxxxxx'],
  ['cmp',      'xxxx00x10101xxxxxxxxxxxxxxxxxxxx'],
# ['cps',      '111100010000xxx0xxxxxxxxxxx0xxxx'], # v6
# ['cpy',      'xxxx00011010xxxxxxxx00000000xxxx'], # v6
  ['eor',      'xxxx00x0001xxxxxxxxxxxxxxxxxxxxx'],
  ['ldc',      'xxxx110xxxx1xxxxxxxxxxxxxxxxxxxx'],
  ['ldc2',     '1111110xxxx1xxxxxxxxxxxxxxxxxxxx'],
  ['ldm1',     'xxxx100xx0x1xxxxxxxxxxxxxxxxxxxx'],
  ['ldm2',     'xxxx100xx101xxxx0xxxxxxxxxxxxxxx'],
  ['ldm3',     'xxxx100xx1x1xxxx1xxxxxxxxxxxxxxx'],
  ['ldr',      'xxxx01xxx0x1xxxxxxxxxxxxxxxxxxxx'],

  ['ldrb',     'xxxx01xxx1x1xxxxxxxxxxxxxxxxxxxx'],
  ['ldrbt',    'xxxx01x0x111xxxxxxxxxxxxxxxxxxxx'],
#?['ldrd',     'xxxx000puiw0xxxxxxxxxxxx1101xxxx'],
# ['ldrex',    'xxxx000110001xxxxxxxxxxx1001xxxx'], # v6
# ['ldrh',     'xxxx000xxxx1xxxxxxxxxxxx1011xxxx'], # SEE ABOVE
  ['ldrsb',    'xxxx000xxxx1xxxxxxxxxxxx1101xxxx'],
#  ['ldrsh',    'xxxx000xxxx1xxxxxxxxxxxx1111xxxx'], # SEE ABOVE
  ['ldrt',     'xxxx01x0x011xxxxxxxxxxxxxxxxxxxx'],
  ['mcr',      'xxxx1110xxx0xxxxxxxxxxxxxxx1xxxx'],
  ['mcr2',     '11111110xxx0xxxxxxxxxxxxxxx1xxxx'],
  ['mcrr',     'xxxx11000100xxxxxxxxxxxxxxxxxxxx'],
  ['mcrr2',    '111111000100xxxxxxxxxxxxxxxxxxxx'],
# ['mla',      'xxxx0000001xxxxxxxxxxxxx1001xxxx'], # SEE ABOVE
  ['mov',      'xxxx00x1101xxxxxxxxxxxxxxxxxxxxx'],
  ['mrc',      'xxxx1110xxx1xxxxxxxxxxxxxxx1xxxx'],
  ['mrc2',     '11111110xxx1xxxxxxxxxxxxxxx1xxxx'],
#?['mrrc',     'xxxx11000101xxxxxxxxxxxxxxxxxxxx'],
# ['mrrc2',    '111111000101xxxxxxxxxxxxxxxxxxxx'], # v6
  ['mrs',      'xxxx00010x00xxxxxxxxxxxxxxxxxxxx'],
  ['msr',      'xxxx00x10x10xxxxxxxxxxxxxxxxxxxx'], # TODO
# ['mul',      'xxxx0000000xxxxxxxxxxxxx1001xxxx'], # SEE ABOVE
  ['mvn',      'xxxx00x1111xxxxxxxxxxxxxxxxxxxxx'],
  ['orr',      'xxxx00x1100xxxxxxxxxxxxxxxxxxxxx'],
# ['pkhbt',    'xxxx01101000xxxxxxxxxxxxx001xxxx'], # v6
# ['pkhtb',    'xxxx01101000xxxxxxxxxxxxx101xxxx'], # v6

#?['pld',      '111101x1x101xxxx1111xxxxxxxxxxxx'],
#?['qadd',     'xxxx00010000xxxxxxxxxxxx0101xxxx'],
# ['qadd16',   'xxxx01100010xxxxxxxxxxxx0001xxxx'], # v6
# ['qadd8',    'xxxx01100010xxxxxxxxxxxx1001xxxx'], # v6
# ['qaddsubx', 'xxxx01100010xxxxxxxxxxxx0011xxxx'], # v6
#?['qdadd',    'xxxx00010100xxxxxxxxxxxx0101xxxx'],
#?['qdsub',    'xxxx00010110xxxxxxxxxxxx0101xxxx'],
#?['qsub',     'xxxx00010010xxxxxxxxxxxx0101xxxx'],
# ['qsub16',   'xxxx01100010xxxxxxxxxxxx0111xxxx'], # v6
# ['qsub8',    'xxxx01100010xxxxxxxxxxxx1111xxxx'], # v6
# ['qsubaddx', 'xxxx01100010xxxxxxxxxxxx0101xxxx'], # v6
# ['rev',      'xxxx01101011xxxxxxxxxxxx0011xxxx'], # v6
# ['rev16',    'xxxx01101011xxxxxxxxxxxx1011xxxx'], # v6
# ['revsh',    'xxxx01101111xxxxxxxxxxxx1011xxxx'], # v6
# ['rfe',      '1111100xx0x1xxxxxxxx1010xxxxxxxx'], # v6
  ['rsb',      'xxxx00x0011xxxxxxxxxxxxxxxxxxxxx'],
  ['rsc',      'xxxx00x0111xxxxxxxxxxxxxxxxxxxxx'],
# ['sadd16',   'xxxx01100001xxxxxxxxxxxx0001xxxx'], # v6
# ['sadd8',    'xxxx01100001xxxxxxxxxxxx1001xxxx'], # v6
# ['saddsubx', 'xxxx01100001xxxxxxxxxxxx0011xxxx'], # v6
  ['sbc',      'xxxx00x0110xxxxxxxxxxxxxxxxxxxxx'],
# ['sel',      'xxxx01101000xxxxxxxxxxxx1011xxxx'], # v6
# ['setend',   '1111000100000001xxxxxxxx0000xxxx'], # v6
# ['shadd16',  'xxxx01100011xxxxxxxxxxxx0001xxxx'], # v6
# ['shadd8',   'xxxx01100011xxxxxxxxxxxx1001xxxx'], # v6
# ['shaddsubx','xxxx01100011xxxxxxxxxxxx0011xxxx'], # v6
# ['shsub16',  'xxxx01100011xxxxxxxxxxxx0111xxxx'], # v6
# ['shsub8',   'xxxx01100011xxxxxxxxxxxx1111xxxx'], # v6
# ['shsubaddx','xxxx01100011xxxxxxxxxxxx0101xxxx'], # v6
# ['smlad',    'xxxx01110000xxxxxxxxxxxx00x1xxxx'], # v6
  ['smlal',    'xxxx0000111xxxxxxxxxxxxx1001xxxx'],
# ['smlald',   'xxxx01110100xxxxxxxxxxxx00x1xxxx'], # v6

#?['smla_xy',  'xxxx00010000xxxxxxxxxxxx1xx0xxxx'],
#?['smlal_xy', 'xxxx00010100xxxxxxxxxxxx1xx0xxxx'],
#?['smlaw_y',  'xxxx00010010xxxxxxxxxxxx1x00xxxx'],
# ['smlsd',    'xxxx01110000xxxxxxxxxxxx01x1xxxx'], # v6
# ['smlsld',   'xxxx01110100xxxxxxxxxxxx01x1xxxx'], # v6
# ['smmla',    'xxxx01110101xxxxxxxxxxxx00x1xxxx'], # v6
# ['smmls',    'xxxx01110101xxxxxxxxxxxx11x1xxxx'], # v6
# ['smmul',    'xxxx01110101xxxx1111xxxx00x1xxxx'], # v6
# ['smuad',    'xxxx01110000xxxx1111xxxx00x1xxxx'], # v6
  ['smull',    'xxxx0000110xxxxxxxxxxxxx1001xxxx'],
#?['smul_xy',  'xxxx00010110xxxxxxxxxxxx1xx0xxxx'],
#?['smulw',    'xxxx00010010xxxxxxxxxxxx1x10xxxx'],
# ['smusd',    'xxxx01110000xxxx1111xxxx01x1xxxx'], # v6
# ['srs',      '1111100xx1x01101xxxx0101xxxxxxxx'], # v6
# ['ssat',     'xxxx0110101xxxxxxxxxxxxxxx01xxxx'], # v6
# ['ssat16',   'xxxx01101010xxxxxxxxxxxx0011xxxx'], # v6
# ['ssub16',   'xxxx01100001xxxxxxxxxxxx0111xxxx'], # v6
# ['ssub8',    'xxxx01100001xxxxxxxxxxxx1111xxxx'], # v6
# ['ssubaddx', 'xxxx01100001xxxxxxxxxxxx0101xxxx'], # v6
  ['stc',      'xxxx110xxxx0xxxxxxxxxxxxxxxxxxxx'],
# ['stc2',     '1111110xxxx0xxxxxxxxxxxxxxxxxxxx'], # v6
  ['stm1',     'xxxx100xx0x0xxxxxxxxxxxxxxxxxxxx'],
  ['stm2',     'xxxx100xx100xxxxxxxxxxxxxxxxxxxx'],
  ['str',      'xxxx01xxx0x0xxxxxxxxxxxxxxxxxxxx'],
  ['strb',     'xxxx01xxx1x0xxxxxxxxxxxxxxxxxxxx'],
  ['strbt',    'xxxx01x0x110xxxxxxxxxxxxxxxxxxxx'],
#?['strd',     'xxxx000xxxx0xxxxxxxxxxxx1111xxxx'],
# ['strex',    'xxxx00011000xxxxxxxxxxxx1001xxxx'], # v6

# ['strh',     'xxxx000xxxx0xxxxxxxxxxxx1011xxxx'], # SEE ABOVE
  ['strt',     'xxxx01x0x010xxxxxxxxxxxxxxxxxxxx'],
  ['sub',      'xxxx00x0010xxxxxxxxxxxxxxxxxxxxx'],
  ['swi',      'xxxx1111xxxxxxxxxxxxxxxxxxxxxxxx'],
  ['swp',      'xxxx00010000xxxxxxxxxxxx1001xxxx'],
  ['swpb',     'xxxx00010100xxxxxxxxxxxx1001xxxx'],
# ['sxtb',     'xxxx011010101111xxxxxxxx0111xxxx'], # v6
# ['sxtb16',   'xxxx011010001111xxxxxxxx0111xxxx'], # v6
# ['sxth',     'xxxx011010111111xxxxxxxx0111xxxx'], # v6
# ['sxtab',    'xxxx01101010xxxxxxxxxxxx0111xxxx'], # v6
# ['sxtab16',  'xxxx01101000xxxxxxxxxxxx0111xxxx'], # v6
# ['sxtah',    'xxxx01101011xxxxxxxxxxxx0111xxxx'], # v6
  ['teq',      'xxxx00x10011xxxxxxxxxxxxxxxxxxxx'],
  ['tst',      'xxxx00x10001xxxxxxxxxxxxxxxxxxxx'],
# ['uadd16',   'xxxx01100101xxxxxxxxxxxx0001xxxx'], # v6
# ['uadd8',    'xxxx01100101xxxxxxxxxxxx1001xxxx'], # v6
# ['uadd8subx','xxxx01100101xxxxxxxxxxxx0011xxxx'], # v6
# ['uhadd16',  'xxxx01100111xxxxxxxxxxxx0001xxxx'], # v6
# ['uhadd8',   'xxxx01100111xxxxxxxxxxxx1001xxxx'], # v6
# ['uhaddsubx','xxxx01100111xxxxxxxxxxxx0011xxxx'], # v6
# ['uhsub16',  'xxxx01100111xxxxxxxxxxxx0111xxxx'], # v6
# ['uhsub8',   'xxxx01100111xxxxxxxxxxxx1111xxxx'], # v6
# ['uhsubaddx','xxxx01100111xxxxxxxxxxxx0101xxxx'], # v6
# ['umaal',    'xxxx00000100xxxxxxxxxxxx1001xxxx'], # v6
  ['umlal',    'xxxx0000101xxxxxxxxxxxxx1001xxxx'],
# ['umull',    'xxxx0000100xxxxxxxxxxxxx1001xxxx'], # SEE ABOVE
# ['uqadd16',  'xxxx01100110xxxxxxxxxxxx0001xxxx'], # v6
# ['uqadd8',   'xxxx01100110xxxxxxxxxxxx1001xxxx'], # v6
# ['uqaddsubx','xxxx01100110xxxxxxxxxxxx0011xxxx'], # v6
# ['uqsub16',  'xxxx01100110xxxxxxxxxxxx0111xxxx'], # v6
# ['uqsub8',   'xxxx01100110xxxxxxxxxxxx1111xxxx'], # v6
# ['uqsubaddx','xxxx01100110xxxxxxxxxxxx0101xxxx'], # v6
# ['usad8',    'xxxx01111000xxxx1111xxxx0001xxxx'], # v6
# ['usada8',   'xxxx01111000xxxxxxxxxxxx0001xxxx'], # v6
# ['usat',     'xxxx0110111xxxxxxxxxxxxxxx01xxxx'], # v6
# ['usat16',   'xxxx01101110xxxxxxxxxxxx0011xxxx'], # v6
# ['usub16',   'xxxx01100101xxxxxxxxxxxx0111xxxx'], # v6
# ['usub8',    'xxxx01100101xxxxxxxxxxxx1111xxxx'], # v6
# ['usubaddx', 'xxxx01100101xxxxxxxxxxxx0101xxxx'], # v6
# ['uxtb',     'xxxx011011101111xxxxxxxx0111xxxx'], # v6
# ['uxtb16',   'xxxx011011001111xxxxxxxx0111xxxx'], # v6
# ['uxtab',    'xxxx01101110xxxxxxxxxxxx0111xxxx'], # v6
# ['uxtab16',  'xxxx01101100xxxxxxxxxxxx0111xxxx'], # v6
# ['uxtah',    'xxxx01101111xxxxxxxxxxxx0111xxxx'], # v6
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
    a, (b, _) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result  = a + b + s.C
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
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
    a, (b, _)  = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result   = a + b
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
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
    a, (b, cout) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result       = a & b
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
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
  if condition_passed( s, cond(inst) ):
    # TODO: s.pc and the pc value in the register file are currently
    #       not the same!
    #   s.pc == s.rf[pc]-8, s.pc used by fetch, s.rf[pc] used by execute
    #
    offset = signed( sign_extend_30( imm_24( inst ) ) << 2 )
    s.pc   = trim_32( s.rf[reg_map['pc']] + offset )
    return
  s.pc += 4

#-----------------------------------------------------------------------
# bl
#-----------------------------------------------------------------------
def execute_bl( s, inst ):
  if condition_passed( s, cond(inst) ):
    s.rf[ reg_map['lr'] ] = s.pc + 4

    # TODO: s.pc and the pc value in the register file are currently
    #       not the same!
    #   s.pc == s.rf[pc]-8, s.pc used by fetch, s.rf[pc] used by execute
    #
    offset = signed( sign_extend_30( imm_24( inst ) ) << 2 )
    s.pc   = trim_32( s.rf[reg_map['pc']] + offset )
    return
  s.pc += 4

#-----------------------------------------------------------------------
# bic
#-----------------------------------------------------------------------
def execute_bic( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, (b, cout) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result       = a & trim_32(~b)
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
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
  raise Exception('Called blx1: Entering THUMB mode! Unsupported')
  s.pc += 4

#-----------------------------------------------------------------------
# blx2
#-----------------------------------------------------------------------
def execute_blx2( s, inst ):
  if condition_passed( s, cond(inst) ):
    LR       = reg_map['lr']
    s.rf[LR] = trim_32( s.pc + 4 )
    s.T      = s.rf[ rm(inst) ] & 0x00000001
    s.pc     = s.rf[ rm(inst) ] & 0xFFFFFFFE
    if s.T:
      raise Exception( "Entering THUMB mode! Unsupported!")

  # no pc + 4 on success
  else: s.pc += 4

#-----------------------------------------------------------------------
# bx
#-----------------------------------------------------------------------
def execute_bx( s, inst ):
  if condition_passed( s, cond(inst) ):
    s.T  = s.rf[ rm(inst) ] & 0x00000001
    s.pc = s.rf[ rm(inst) ] & 0xFFFFFFFE
    if s.T:
      raise Exception( "Entering THUMB mode! Unsupported!")

  # no pc + 4 on success
  else: s.pc += 4

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
  if condition_passed( s, cond(inst) ):
    Rm = s.rf[ rm(inst) ]

    if Rm == 0:
      s.rf[ rd(inst) ] = 32
    else:
      mask = 0x80000000
      leading_zeros = 32
      for x in range(31):
        if mask & Rm:
          leading_zeros = x
          break
        mask >>= 1

      assert leading_zeros != 32
      s.rf[ rd(inst) ] = leading_zeros

  s.pc += 4

#-----------------------------------------------------------------------
# cmn
#-----------------------------------------------------------------------
def execute_cmn( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, (b, _) = s.rf[ rn(inst) ], shifter_operand( s, inst )
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
  if condition_passed( s, cond(inst) ):
    a, (b, _) = s.rf[ rn(inst) ], shifter_operand( s, inst )
    result = a - b

    s.N = (result >> 31)&1
    s.Z = trim_32( result ) == 0
    s.C = not borrow_from( result )
    s.V = overflow_from_sub( a, b, result )
  s.pc += 4

#-----------------------------------------------------------------------
# eor
#-----------------------------------------------------------------------
def execute_eor( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, (b, cout) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result       = a ^ b
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
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
    register_mask  = register_list( inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    for i in range(15):
      if register_mask & 0b1:
        s.rf[ i ] = s.mem.read( addr, 4 )
        addr += 4
      register_mask >>= 1

    if register_mask & 0b1:  # reg 15
      s.pc = s.mem.read( addr, 4 ) & 0xFFFFFFFE
      s.T  = s.pc & 0b1
      if s.T: raise Exception( "Entering THUMB mode! Unsupported!")
      assert end_addr == addr
      return

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

    if rd(inst) == 15:
      s.pc = data & 0xFFFFFFFE
      s.T  = data & 0b1
      return
    else:
      s.rf[ rd(inst) ] = data

  s.pc += 4

#-----------------------------------------------------------------------
# ldrb
#-----------------------------------------------------------------------
def execute_ldrb( s, inst ):
  if condition_passed( s, cond(inst) ):
    if rd(inst) == 15: raise Exception('UNPREDICTABLE')

    addr = addressing_mode_2( s, inst )

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

    addr = addressing_mode_3( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )
    # TODO: alignment fault checking?
    # if (CP15_reg1_Ubit == 0) and address[0] == 0b1:
    #   UNPREDICTABLE

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
def execute_ldrsh( s, inst ):
  if condition_passed( s, cond(inst) ):
    if rd(inst) == 15: raise Exception('UNPREDICTABLE')

    addr = addressing_mode_3( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )
    # TODO: alignment fault checking?
    # if (CP15_reg1_Ubit == 0) and address[0] == 0b1:
    #   UNPREDICTABLE

    s.rf[ rd(inst) ] = sign_extend_half( s.mem.read( addr, 2 ) )

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

    Rm, Rs, Rd  = s.rf[ rm(inst) ], s.rf[ rs(inst) ], s.rf[ rd(inst) ]
    result      = trim_32(Rm * Rs + Rd)
    s.rf[ rn( inst ) ] = result

    if S(inst):
      s.N = (result >> 31)&1
      s.Z = result == 0

  s.pc += 4

#-----------------------------------------------------------------------
# mov
#-----------------------------------------------------------------------
def execute_mov( s, inst ):
  if condition_passed( s, cond(inst) ):
    if rd(inst) == 15 and S(inst):
    # if not CurrentModeHasSPSR(): CPSR = SPSR
    # else:                        UNPREDICTABLE
      raise Exception('UNPREDICTABLE in user and system mode!')

    result, cout = shifter_operand( s, inst )
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = cout
      s.V = s.V

    # FIXME: hacky handling of writing to PC
    if rd(inst) == 15:
      s.pc = trim_32( result)
      return

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
  if condition_passed( s, cond(inst) ):
    Rm, Rs = s.rf[ rm(inst) ], s.rf[ rs(inst) ]
    result = trim_32(Rm * Rs)
    s.rf[ rn( inst ) ] = result

    if S(inst):
      if rn(inst) == 15: raise Exception('UNPREDICTABLE')
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
    a, cout = shifter_operand( s, inst )
    result  = trim_32( ~a )
    s.rf[ rd( inst ) ] = result

    if S(inst):
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
    a, (b, cout) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result     = a | b
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
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
    a, (b, _) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result  = b - a
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
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
    a, (b, _) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result  = b - a - (not s.C)
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
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
    a, (b, _) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result  = a - b - (not s.C)
    s.rf[ rd( inst ) ] = trim_32( result )

    if S(inst):
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
    register_mask  = register_list( inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    for i in range(16):
      if register_mask & 0b1:
        s.mem.write( addr, 4, s.rf[i] )
        addr += 4
      register_mask >>= 1

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
  if condition_passed( s, cond(inst) ):

    addr = addressing_mode_2( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )

    s.mem.write( addr, 4, s.rf[ rd(inst) ] )

  s.pc += 4

#-----------------------------------------------------------------------
# strb
#-----------------------------------------------------------------------
def execute_strb( s, inst ):
  if condition_passed( s, cond(inst) ):

    addr = addressing_mode_2( s, inst )

    s.mem.write( addr, 1, trim_8( s.rf[ rd(inst) ] ) )

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
  if condition_passed( s, cond(inst) ):

    addr = addressing_mode_3( s, inst )

    # TODO: support multiple memory accessing modes?
    # MemoryAccess( s.B, s.E )
    # TODO: alignment fault checking?
    # if (CP15_reg1_Ubit == 0) and address[0] == 0b1:
    #   UNPREDICTABLE

    s.mem.write( addr, 2, s.rf[ rd(inst) ] & 0xFFFF )

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
    a, (b, _) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result  = a - b
    s.rf[ rd( inst ) ] = trim_32( result )

    if S( inst ):
      if rd(inst) == 15: raise Exception('Writing SPSR not implemented!')
      s.N = (result >> 31)&1
      s.Z = trim_32( result ) == 0
      s.C = not borrow_from( result )
      s.V = overflow_from_sub( a, b, result )
  s.pc += 4

#-----------------------------------------------------------------------
# swi
#-----------------------------------------------------------------------
from syscalls import do_syscall
def execute_swi( s, inst ):
  if condition_passed( s, cond(inst) ):
    do_syscall( s, s.rf[7] )
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
  if condition_passed( s, cond(inst) ):
    a, (b, cout) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result = trim_32( a ^ b )

    if S(inst):
      s.N = (result >> 31)&1
      s.Z = result == 0
      s.C = cout
  s.pc += 4

#-----------------------------------------------------------------------
# tst
#-----------------------------------------------------------------------
def execute_tst( s, inst ):
  if condition_passed( s, cond(inst) ):
    a, (b, cout) = s.rf[ rn( inst ) ], shifter_operand( s, inst )
    result = trim_32( a & b )

    if S(inst):
      s.N = (result >> 31)&1
      s.Z = result == 0
      s.C = cout
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
  if condition_passed( s, cond(inst) ):
    if rd(inst) == 15: raise Exception('UNPREDICTABLE')
    if rm(inst) == 15: raise Exception('UNPREDICTABLE')
    if rs(inst) == 15: raise Exception('UNPREDICTABLE')
    if rn(inst) == 15: raise Exception('UNPREDICTABLE')

    RdHi, RdLo  = rn(inst), rd(inst)
    Rm,   Rs    = s.rf[ rm(inst) ], s.rf[ rs(inst) ]
    result      = Rm * Rs

    if RdHi == RdLo: raise Exception('UNPREDICTABLE')

    s.rf[ RdHi ] = trim_32( result >> 32 )
    s.rf[ RdLo ] = trim_32( result )

    if S(inst):
      s.N = (result >> 63)&1
      s.Z = result == 0
  s.pc += 4

#=======================================================================
# Create Decoder
#=======================================================================

decode = create_risc_decoder( encodings, globals(), debug=True )

