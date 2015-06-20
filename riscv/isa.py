#=======================================================================
# isa.py
#=======================================================================

from utils        import sext_32, signed, sext, trim
from pydgin.misc  import create_risc_decoder, FatalError
from pydgin.utils import (
  trim_32, specialize, intmask, bits2float, float2bits
)
from softfloat._abi import ffi
lib = ffi.dlopen('../build/libsoftfloat.so')

from helpers import *
from syscalls import do_syscall

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [
  ['beq',                'xxxxxxxxxxxxxxxxx000xxxxx1100011'],
  ['bne',                'xxxxxxxxxxxxxxxxx001xxxxx1100011'],
  ['blt',                'xxxxxxxxxxxxxxxxx100xxxxx1100011'],
  ['bge',                'xxxxxxxxxxxxxxxxx101xxxxx1100011'],
  ['bltu',               'xxxxxxxxxxxxxxxxx110xxxxx1100011'],
  ['bgeu',               'xxxxxxxxxxxxxxxxx111xxxxx1100011'],
  ['jalr',               'xxxxxxxxxxxxxxxxx000xxxxx1100111'],
  ['jal',                'xxxxxxxxxxxxxxxxxxxxxxxxx1101111'],
  ['lui',                'xxxxxxxxxxxxxxxxxxxxxxxxx0110111'],
  ['auipc',              'xxxxxxxxxxxxxxxxxxxxxxxxx0010111'],
  ['addi',               'xxxxxxxxxxxxxxxxx000xxxxx0010011'],
  ['slli',               '000000xxxxxxxxxxx001xxxxx0010011'],
  ['slti',               'xxxxxxxxxxxxxxxxx010xxxxx0010011'],
  ['sltiu',              'xxxxxxxxxxxxxxxxx011xxxxx0010011'],
  ['xori',               'xxxxxxxxxxxxxxxxx100xxxxx0010011'],
  ['srli',               '000000xxxxxxxxxxx101xxxxx0010011'],
  ['srai',               '010000xxxxxxxxxxx101xxxxx0010011'],
  ['ori',                'xxxxxxxxxxxxxxxxx110xxxxx0010011'],
  ['andi',               'xxxxxxxxxxxxxxxxx111xxxxx0010011'],
  ['add',                '0000000xxxxxxxxxx000xxxxx0110011'],
  ['sub',                '0100000xxxxxxxxxx000xxxxx0110011'],
  ['sll',                '0000000xxxxxxxxxx001xxxxx0110011'],
  ['slt',                '0000000xxxxxxxxxx010xxxxx0110011'],
  ['sltu',               '0000000xxxxxxxxxx011xxxxx0110011'],
  ['xor',                '0000000xxxxxxxxxx100xxxxx0110011'],
  ['srl',                '0000000xxxxxxxxxx101xxxxx0110011'],
  ['sra',                '0100000xxxxxxxxxx101xxxxx0110011'],
  ['or',                 '0000000xxxxxxxxxx110xxxxx0110011'],
  ['and',                '0000000xxxxxxxxxx111xxxxx0110011'],
  ['addiw',              'xxxxxxxxxxxxxxxxx000xxxxx0011011'],
  ['slliw',              '0000000xxxxxxxxxx001xxxxx0011011'],
  ['srliw',              '0000000xxxxxxxxxx101xxxxx0011011'],
  ['sraiw',              '0100000xxxxxxxxxx101xxxxx0011011'],
  ['addw',               '0000000xxxxxxxxxx000xxxxx0111011'],
  ['subw',               '0100000xxxxxxxxxx000xxxxx0111011'],
  ['sllw',               '0000000xxxxxxxxxx001xxxxx0111011'],
  ['srlw',               '0000000xxxxxxxxxx101xxxxx0111011'],
  ['sraw',               '0100000xxxxxxxxxx101xxxxx0111011'],
  ['lb',                 'xxxxxxxxxxxxxxxxx000xxxxx0000011'],
  ['lh',                 'xxxxxxxxxxxxxxxxx001xxxxx0000011'],
  ['lw',                 'xxxxxxxxxxxxxxxxx010xxxxx0000011'],
  ['ld',                 'xxxxxxxxxxxxxxxxx011xxxxx0000011'],
  ['lbu',                'xxxxxxxxxxxxxxxxx100xxxxx0000011'],
  ['lhu',                'xxxxxxxxxxxxxxxxx101xxxxx0000011'],
  ['lwu',                'xxxxxxxxxxxxxxxxx110xxxxx0000011'],
  ['sb',                 'xxxxxxxxxxxxxxxxx000xxxxx0100011'],
  ['sh',                 'xxxxxxxxxxxxxxxxx001xxxxx0100011'],
  ['sw',                 'xxxxxxxxxxxxxxxxx010xxxxx0100011'],
  ['sd',                 'xxxxxxxxxxxxxxxxx011xxxxx0100011'],
  ['fence',              'xxxxxxxxxxxxxxxxx000xxxxx0001111'],
  ['fence_i',            'xxxxxxxxxxxxxxxxx001xxxxx0001111'],
  ['mul',                '0000001xxxxxxxxxx000xxxxx0110011'],
  ['mulh',               '0000001xxxxxxxxxx001xxxxx0110011'],
  ['mulhsu',             '0000001xxxxxxxxxx010xxxxx0110011'],
  ['mulhu',              '0000001xxxxxxxxxx011xxxxx0110011'],
  ['div',                '0000001xxxxxxxxxx100xxxxx0110011'],
  ['divu',               '0000001xxxxxxxxxx101xxxxx0110011'],
  ['rem',                '0000001xxxxxxxxxx110xxxxx0110011'],
  ['remu',               '0000001xxxxxxxxxx111xxxxx0110011'],
  ['mulw',               '0000001xxxxxxxxxx000xxxxx0111011'],
  ['divw',               '0000001xxxxxxxxxx100xxxxx0111011'],
  ['divuw',              '0000001xxxxxxxxxx101xxxxx0111011'],
  ['remw',               '0000001xxxxxxxxxx110xxxxx0111011'],
  ['remuw',              '0000001xxxxxxxxxx111xxxxx0111011'],
  ['amoadd_w',           '00000xxxxxxxxxxxx010xxxxx0101111'],
  ['amoxor_w',           '00100xxxxxxxxxxxx010xxxxx0101111'],
  ['amoor_w',            '01000xxxxxxxxxxxx010xxxxx0101111'],
  ['amoand_w',           '01100xxxxxxxxxxxx010xxxxx0101111'],
  ['amomin_w',           '10000xxxxxxxxxxxx010xxxxx0101111'],
  ['amomax_w',           '10100xxxxxxxxxxxx010xxxxx0101111'],
  ['amominu_w',          '11000xxxxxxxxxxxx010xxxxx0101111'],
  ['amomaxu_w',          '11100xxxxxxxxxxxx010xxxxx0101111'],
  ['amoswap_w',          '00001xxxxxxxxxxxx010xxxxx0101111'],
  ['lr_w',               '00010xx00000xxxxx010xxxxx0101111'],
  ['sc_w',               '00011xxxxxxxxxxxx010xxxxx0101111'],
  ['amoadd_d',           '00000xxxxxxxxxxxx011xxxxx0101111'],
  ['amoxor_d',           '00100xxxxxxxxxxxx011xxxxx0101111'],
  ['amoor_d',            '01000xxxxxxxxxxxx011xxxxx0101111'],
  ['amoand_d',           '01100xxxxxxxxxxxx011xxxxx0101111'],
  ['amomin_d',           '10000xxxxxxxxxxxx011xxxxx0101111'],
  ['amomax_d',           '10100xxxxxxxxxxxx011xxxxx0101111'],
  ['amominu_d',          '11000xxxxxxxxxxxx011xxxxx0101111'],
  ['amomaxu_d',          '11100xxxxxxxxxxxx011xxxxx0101111'],
  ['amoswap_d',          '00001xxxxxxxxxxxx011xxxxx0101111'],
  ['lr_d',               '00010xx00000xxxxx011xxxxx0101111'],
  ['sc_d',               '00011xxxxxxxxxxxx011xxxxx0101111'],
  ['scall',              '00000000000000000000000001110011'],
  ['sbreak',             '00000000000100000000000001110011'],
  ['sret',               '00010000000000000000000001110011'],
  ['sfence_vm',          '000100000001xxxxx000000001110011'],
  ['wfi',                '00010000001000000000000001110011'],
  ['mrth',               '00110000011000000000000001110011'],
  ['mrts',               '00110000010100000000000001110011'],
  ['hrts',               '00100000010100000000000001110011'],

  ['fsflags',            '000000000001xxxxx001xxxxx1110011'],

  ['csrrw',              'xxxxxxxxxxxxxxxxx001xxxxx1110011'],
  ['csrrs',              'xxxxxxxxxxxxxxxxx010xxxxx1110011'],
  ['csrrc',              'xxxxxxxxxxxxxxxxx011xxxxx1110011'],
  ['csrrwi',             'xxxxxxxxxxxxxxxxx101xxxxx1110011'],
  ['csrrsi',             'xxxxxxxxxxxxxxxxx110xxxxx1110011'],
  ['csrrci',             'xxxxxxxxxxxxxxxxx111xxxxx1110011'],

  ['fadd_s',             '0000000xxxxxxxxxxxxxxxxxx1010011'],
  ['fsub_s',             '0000100xxxxxxxxxxxxxxxxxx1010011'],
  ['fmul_s',             '0001000xxxxxxxxxxxxxxxxxx1010011'],
  ['fdiv_s',             '0001100xxxxxxxxxxxxxxxxxx1010011'],
  ['fsgnj_s',            '0010000xxxxxxxxxx000xxxxx1010011'],
  ['fsgnjn_s',           '0010000xxxxxxxxxx001xxxxx1010011'],
  ['fsgnjx_s',           '0010000xxxxxxxxxx010xxxxx1010011'],
  ['fmin_s',             '0010100xxxxxxxxxx000xxxxx1010011'],
  ['fmax_s',             '0010100xxxxxxxxxx001xxxxx1010011'],
  ['fsqrt_s',            '010110000000xxxxxxxxxxxxx1010011'],
  ['fadd_d',             '0000001xxxxxxxxxxxxxxxxxx1010011'],
  ['fsub_d',             '0000101xxxxxxxxxxxxxxxxxx1010011'],
  ['fmul_d',             '0001001xxxxxxxxxxxxxxxxxx1010011'],
  ['fdiv_d',             '0001101xxxxxxxxxxxxxxxxxx1010011'],
  ['fsgnj_d',            '0010001xxxxxxxxxx000xxxxx1010011'],
  ['fsgnjn_d',           '0010001xxxxxxxxxx001xxxxx1010011'],
  ['fsgnjx_d',           '0010001xxxxxxxxxx010xxxxx1010011'],
  ['fmin_d',             '0010101xxxxxxxxxx000xxxxx1010011'],
  ['fmax_d',             '0010101xxxxxxxxxx001xxxxx1010011'],
  ['fcvt_s_d',           '010000000001xxxxxxxxxxxxx1010011'],
  ['fcvt_d_s',           '010000100000xxxxxxxxxxxxx1010011'],
  ['fsqrt_d',            '010110100000xxxxxxxxxxxxx1010011'],
  ['fle_s',              '1010000xxxxxxxxxx000xxxxx1010011'],
  ['flt_s',              '1010000xxxxxxxxxx001xxxxx1010011'],
  ['feq_s',              '1010000xxxxxxxxxx010xxxxx1010011'],
  ['fle_d',              '1010001xxxxxxxxxx000xxxxx1010011'],
  ['flt_d',              '1010001xxxxxxxxxx001xxxxx1010011'],
  ['feq_d',              '1010001xxxxxxxxxx010xxxxx1010011'],
  ['fcvt_w_s',           '110000000000xxxxxxxxxxxxx1010011'],
  ['fcvt_wu_s',          '110000000001xxxxxxxxxxxxx1010011'],
  ['fcvt_l_s',           '110000000010xxxxxxxxxxxxx1010011'],
  ['fcvt_lu_s',          '110000000011xxxxxxxxxxxxx1010011'],
  ['fmv_x_s',            '111000000000xxxxx000xxxxx1010011'],
  ['fclass_s',           '111000000000xxxxx001xxxxx1010011'],
  ['fcvt_w_d',           '110000100000xxxxxxxxxxxxx1010011'],
  ['fcvt_wu_d',          '110000100001xxxxxxxxxxxxx1010011'],
  ['fcvt_l_d',           '110000100010xxxxxxxxxxxxx1010011'],
  ['fcvt_lu_d',          '110000100011xxxxxxxxxxxxx1010011'],
  ['fmv_x_d',            '111000100000xxxxx000xxxxx1010011'],
  ['fclass_d',           '111000100000xxxxx001xxxxx1010011'],
  ['fcvt_s_w',           '110100000000xxxxxxxxxxxxx1010011'],
  ['fcvt_s_wu',          '110100000001xxxxxxxxxxxxx1010011'],
  ['fcvt_s_l',           '110100000010xxxxxxxxxxxxx1010011'],
  ['fcvt_s_lu',          '110100000011xxxxxxxxxxxxx1010011'],
  ['fmv_s_x',            '111100000000xxxxx000xxxxx1010011'],
  ['fcvt_d_w',           '110100100000xxxxxxxxxxxxx1010011'],
  ['fcvt_d_wu',          '110100100001xxxxxxxxxxxxx1010011'],
  ['fcvt_d_l',           '110100100010xxxxxxxxxxxxx1010011'],
  ['fcvt_d_lu',          '110100100011xxxxxxxxxxxxx1010011'],
  ['fmv_d_x',            '111100100000xxxxx000xxxxx1010011'],
  ['flw',                'xxxxxxxxxxxxxxxxx010xxxxx0000111'],
  ['fld',                'xxxxxxxxxxxxxxxxx011xxxxx0000111'],
  ['fsw',                'xxxxxxxxxxxxxxxxx010xxxxx0100111'],
  ['fsd',                'xxxxxxxxxxxxxxxxx011xxxxx0100111'],
  ['fmadd_s',            'xxxxx00xxxxxxxxxxxxxxxxxx1000011'],
  ['fmsub_s',            'xxxxx00xxxxxxxxxxxxxxxxxx1000111'],
  ['fnmsub_s',           'xxxxx00xxxxxxxxxxxxxxxxxx1001011'],
  ['fnmadd_s',           'xxxxx00xxxxxxxxxxxxxxxxxx1001111'],
  ['fmadd_d',            'xxxxx01xxxxxxxxxxxxxxxxxx1000011'],
  ['fmsub_d',            'xxxxx01xxxxxxxxxxxxxxxxxx1000111'],
  ['fnmsub_d',           'xxxxx01xxxxxxxxxxxxxxxxxx1001011'],
  ['fnmadd_d',           'xxxxx01xxxxxxxxxxxxxxxxxx1001111'],
  ['custom0',            'xxxxxxxxxxxxxxxxx000xxxxx0001011'],
  ['custom0_rs1',        'xxxxxxxxxxxxxxxxx010xxxxx0001011'],
  ['custom0_rs1_rs2',    'xxxxxxxxxxxxxxxxx011xxxxx0001011'],
  ['custom0_rd',         'xxxxxxxxxxxxxxxxx100xxxxx0001011'],
  ['custom0_rd_rs1',     'xxxxxxxxxxxxxxxxx110xxxxx0001011'],
  ['custom0_rd_rs1_rs2', 'xxxxxxxxxxxxxxxxx111xxxxx0001011'],
  ['custom1',            'xxxxxxxxxxxxxxxxx000xxxxx0101011'],
  ['custom1_rs1',        'xxxxxxxxxxxxxxxxx010xxxxx0101011'],
  ['custom1_rs1_rs2',    'xxxxxxxxxxxxxxxxx011xxxxx0101011'],
  ['custom1_rd',         'xxxxxxxxxxxxxxxxx100xxxxx0101011'],
  ['custom1_rd_rs1',     'xxxxxxxxxxxxxxxxx110xxxxx0101011'],
  ['custom1_rd_rs1_rs2', 'xxxxxxxxxxxxxxxxx111xxxxx0101011'],
  ['custom2',            'xxxxxxxxxxxxxxxxx000xxxxx1011011'],
  ['custom2_rs1',        'xxxxxxxxxxxxxxxxx010xxxxx1011011'],
  ['custom2_rs1_rs2',    'xxxxxxxxxxxxxxxxx011xxxxx1011011'],
  ['custom2_rd',         'xxxxxxxxxxxxxxxxx100xxxxx1011011'],
  ['custom2_rd_rs1',     'xxxxxxxxxxxxxxxxx110xxxxx1011011'],
  ['custom2_rd_rs1_rs2', 'xxxxxxxxxxxxxxxxx111xxxxx1011011'],
  ['custom3',            'xxxxxxxxxxxxxxxxx000xxxxx1111011'],
  ['custom3_rs1',        'xxxxxxxxxxxxxxxxx010xxxxx1111011'],
  ['custom3_rs1_rs2',    'xxxxxxxxxxxxxxxxx011xxxxx1111011'],
  ['custom3_rd',         'xxxxxxxxxxxxxxxxx100xxxxx1111011'],
  ['custom3_rd_rs1',     'xxxxxxxxxxxxxxxxx110xxxxx1111011'],
  ['custom3_rd_rs1_rs2', 'xxxxxxxxxxxxxxxxx111xxxxx1111011'],
]

#=======================================================================
# Instruction Definitions
#=======================================================================

@specialize.argtype(0)
def sext_xlen( val ):
  return val

# TODO: move this elsewhere?
def multhi64( a, b ):
  # returns the high 64 bits of 64 bit multiplication
  # using this trick to get the high bits of 64-bit multiplication:
  # http://stackoverflow.com/questions/28868367/getting-the-high-part-of-64-bit-integer-multiplication
  a_hi, a_lo = trim_32(a >> 32), trim_32(a)
  b_hi, b_lo = trim_32(b >> 32), trim_32(b)

  a_x_b_hi =  a_hi * b_hi
  a_x_b_mid = a_hi * b_lo
  b_x_a_mid = b_hi * a_lo
  a_x_b_lo =  a_lo * b_lo

  carry_bit = ( trim_32( a_x_b_mid ) + trim_32( b_x_a_mid ) +
                (a_x_b_lo >> 32) ) >> 32

  return a_x_b_hi + (a_x_b_mid >> 32) + (b_x_a_mid >> 32) + carry_bit


def execute_beq( s, inst ):
  if s.rf[inst.rs1] == s.rf[inst.rs2]:
    s.pc = BRANCH_TARGET( s, inst )
  else:
    s.pc += 4

def execute_bne( s, inst ):
  if s.rf[inst.rs1] != s.rf[inst.rs2]:
    s.pc = BRANCH_TARGET( s, inst )
  else:
    s.pc += 4

def execute_blt( s, inst ):
  if signed(s.rf[inst.rs1], 64) < signed(s.rf[inst.rs2], 64):
    s.pc = BRANCH_TARGET( s, inst )
  else:
    s.pc += 4

def execute_bge( s, inst ):
  if signed(s.rf[inst.rs1], 64) >= signed(s.rf[inst.rs2], 64):
    s.pc = BRANCH_TARGET( s, inst )
  else:
    s.pc += 4

def execute_bltu( s, inst ):
  if s.rf[inst.rs1] < s.rf[inst.rs2]:
    s.pc = BRANCH_TARGET( s, inst )
  else:
    s.pc += 4

def execute_bgeu( s, inst ):
  if s.rf[inst.rs1] >= s.rf[inst.rs2]:
    s.pc = BRANCH_TARGET( s, inst )
  else:
    s.pc += 4

def execute_jalr( s, inst ):
  tmp = sext_xlen( s.pc + 4 )
  s.pc = (s.rf[inst.rs1] + inst.i_imm) &  0xFFFFFFFE
  s.rf[ inst.rd ] = tmp;

def execute_jal( s, inst ):
  tmp = sext_xlen( s.pc + 4 )
  s.pc = JUMP_TARGET( s, inst )
  s.rf[ inst.rd ] = tmp;

def execute_lui( s, inst ):
  s.rf[ inst.rd ] = inst.u_imm
  s.pc += 4

def execute_auipc( s, inst ):
  s.rf[ inst.rd ] = sext_xlen(inst.u_imm + s.pc)
  s.pc += 4

def execute_addi( s, inst ):
  s.rf[ inst.rd ] = sext_xlen( s.rf[inst.rs1] + inst.i_imm )
  s.pc += 4

def execute_slli( s, inst ):
  if SHAMT( s, inst ) > s.xlen:
    raise TRAP_ILLEGAL_INSTRUCTION()
  s.rf[ inst.rd ] = sext_xlen( s.rf[inst.rs1] << SHAMT( s, inst ) )
  s.pc += 4

def execute_slti( s, inst ):
  s.rf[ inst.rd ] = signed( s.rf[inst.rs1], 64 ) < signed( inst.i_imm, 64 )
  s.pc += 4

def execute_sltiu( s, inst ):
  s.rf[ inst.rd ] = s.rf[inst.rs1] < inst.i_imm
  s.pc += 4

def execute_xori( s, inst ):
  s.rf[ inst.rd ] = inst.i_imm ^ s.rf[inst.rs1]
  s.pc += 4

def execute_srli( s, inst ):
  if s.xlen == 64:
    s.rf[ inst.rd ] = s.rf[inst.rs1] >> SHAMT( s, inst )
  elif SHAMT( s, inst ) & 0x20:
    raise TRAP_ILLEGAL_INSTRUCTION()
  else:
    s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] >> SHAMT( s, inst ) )
  s.pc += 4

def execute_srai( s, inst ):
  if s.xlen == 64:
    s.rf[ inst.rd ] = signed( s.rf[inst.rs1], 64 ) >> SHAMT( s, inst )
  elif SHAMT( s, inst ) & 0x20:
    raise TRAP_ILLEGAL_INSTRUCTION()
  else:
    s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] >> SHAMT( s, inst ) )
  s.pc += 4

def execute_ori( s, inst ):
  s.rf[ inst.rd ] = inst.i_imm | s.rf[inst.rs1]
  s.pc += 4

def execute_andi( s, inst ):
  s.rf[ inst.rd ] = inst.i_imm & s.rf[inst.rs1]
  s.pc += 4

def execute_add( s, inst ):
  s.rf[ inst.rd ] = sext_xlen( s.rf[inst.rs1] + s.rf[inst.rs2])
  s.pc += 4

def execute_sub( s, inst ):
  s.rf[ inst.rd ] = sext_xlen( s.rf[inst.rs1] - s.rf[inst.rs2])
  s.pc += 4

def execute_sll( s, inst ):
  shamt = s.rf[inst.rs2] & (s.xlen-1)
  s.rf[ inst.rd ] = sext_xlen( s.rf[inst.rs1] << shamt )
  s.pc += 4

def execute_slt( s, inst ):
  s.rf[ inst.rd ] = signed( s.rf[inst.rs1], 64 ) < signed( s.rf[inst.rs2], 64)
  s.pc += 4

def execute_sltu( s, inst ):
  s.rf[ inst.rd ] = s.rf[inst.rs1] < s.rf[inst.rs2]
  s.pc += 4

def execute_xor( s, inst ):
  s.rf[ inst.rd ] = s.rf[inst.rs1] ^ s.rf[inst.rs2]
  s.pc += 4

def execute_srl( s, inst ):
  if s.xlen == 64:
    s.rf[ inst.rd ] = s.rf[inst.rs1] >> (s.rf[inst.rs2] & 0x3F)
  else:
    s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] >> (s.rf[inst.rs2] & 0x1F) )
  s.pc += 4

def execute_sra( s, inst ):
  s.rf[ inst.rd ] = sext_xlen(
    signed( s.rf[inst.rs1], 64 ) >> (s.rf[inst.rs2] & (s.xlen-1))
  )
  s.pc += 4

def execute_or( s, inst ):
  s.rf[ inst.rd ] = s.rf[inst.rs1] | s.rf[inst.rs2]
  s.pc += 4

def execute_and( s, inst ):
  s.rf[ inst.rd ] = s.rf[inst.rs1] & s.rf[inst.rs2]
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

def execute_lb( s, inst ):
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = sext( s.mem.read( addr, 1 ), 8 )
  s.pc += 4

def execute_lh( s, inst ):
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = sext( s.mem.read( addr, 2 ), 16 )
  s.pc += 4

def execute_lw( s, inst ):
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = sext_32( s.mem.read( addr, 4 ) )
  s.pc += 4

def execute_ld( s, inst ):
  # TODO: make memory support 64-bit ops
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = ( s.mem.read( addr+4, 4 ) << 32 ) \
                  | s.mem.read( addr, 4 )
  s.pc += 4

def execute_lbu( s, inst ):
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = s.mem.read( addr, 1 )
  s.pc += 4

def execute_lhu( s, inst ):
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = s.mem.read( addr, 2 )
  s.pc += 4

def execute_lwu( s, inst ):
  addr = s.rf[inst.rs1] + inst.i_imm
  s.rf[inst.rd] = s.mem.read( addr, 4 )
  s.pc += 4

def execute_sb( s, inst ):
  addr = s.rf[inst.rs1] + inst.s_imm
  s.mem.write( addr, 1, trim( s.rf[inst.rs2], 8 ) )
  s.pc += 4

def execute_sh( s, inst ):
  addr = s.rf[inst.rs1] + inst.s_imm
  s.mem.write( addr, 2, trim( s.rf[inst.rs2], 16 ) )
  s.pc += 4

def execute_sw( s, inst ):
  addr = s.rf[inst.rs1] + inst.s_imm
  s.mem.write( addr, 4, trim_32( s.rf[inst.rs2] ) )
  s.pc += 4

def execute_sd( s, inst ):
  # TODO: make memory support 64-bit ops
  addr = s.rf[inst.rs1] + inst.s_imm
  s.mem.write( addr,   4, trim_32( s.rf[inst.rs2] ) )
  s.mem.write( addr+4, 4, trim_32( s.rf[inst.rs2] >> 32 ) )
  s.pc += 4

def execute_fence( s, inst ):
  s.pc += 4

def execute_fence_i( s, inst ):
  # TODO: MMU flush icache
  s.pc += 4

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

def execute_amoswap_w( s, inst ):
  addr  = s.rf[inst.rs1]
  value = s.mem.read( addr, 4 )
  s.mem.write( addr, 4, trim(s.rf[inst.rs2], 32))
  s.rf[inst.rd] = sext_32( value )
  s.pc += 4

def execute_lr_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sc_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoadd_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = value + s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amoxor_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = value ^ s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amoor_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = value | s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amoand_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = value & s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amomin_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = min( signed(value, 64), signed(s.rf[inst.rs2], 64) )
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amomax_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = max( signed(value, 64), signed(s.rf[inst.rs2], 64) )
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amominu_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = min( value, s.rf[inst.rs2] )
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amomaxu_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = max( value, s.rf[inst.rs2] )
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_amoswap_d( s, inst ):
  addr  = s.rf[inst.rs1]
  value = (( s.mem.read( addr+4, 4 ) << 32 ) \
           | s.mem.read( addr,   4 ))
  new   = s.rf[inst.rs2]
  s.mem.write( addr,   4, trim_32( new )       )
  s.mem.write( addr+4, 4, trim_32( new >> 32 ) )
  s.rf[inst.rd] = value
  s.pc += 4

def execute_lr_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sc_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_scall( s, inst ):
  do_syscall( s )
  s.pc += 4

def execute_sbreak( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sret( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sfence_vm( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_wfi( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_mrth( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_mrts( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_hrts( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsflags( s, inst ):
  old = s.fcsr & 0x1F
  new = s.rf[inst.rs1] & 0x1F
  s.fcsr = ((s.fcsr >> 5) << 5) | new
  s.rf[inst.rd] = old
  s.pc += 4

def execute_csrrw( s, inst ):
  result = s.rf[inst.rs1]
  if result & 0x1:
    status = result >> 1
    if status: raise FatalError("Fail! %s" % (result >> 1 ) )
    else:      raise FatalError("Pass!")
  else:
    raise NotImplementedError()
  s.pc += 4

def execute_csrrs( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_csrrc( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_csrrwi( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_csrrsi( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_csrrci( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fadd_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.fp[ inst.rd ] = sext_32( lib.f32_add( a, b ) )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0

  #print 'fp[{:2}] = {}, fp[{:2}] = {}'.format( inst.rs1, a, inst.rs2, b ), '---',
  #print 'fp[{:2}] = {}, fp[{:2}] = {}'.format( inst.rs1, bits2float(a), inst.rs2, bits2float(b) )
  #print hex(out), bits2float( out ), '{:05b}'.format( s.fcsr )

  s.pc += 4

def execute_fsub_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.fp[ inst.rd ] = sext_32( lib.f32_sub( a, b ) )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0

  s.pc += 4

def execute_fmul_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.fp[ inst.rd ] = sext_32( lib.f32_mul( a, b ) )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0

  s.pc += 4

def execute_fdiv_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsgnj_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsgnjn_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsgnjx_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmin_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmax_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsqrt_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fadd_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.fp[ inst.rd ] = lib.f64_add( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0

  #print 'fp[{:2}] = {}, fp[{:2}] = {}'.format( inst.rs1, a, inst.rs2, b ), '---',
  #print 'fp[{:2}] = {}, fp[{:2}] = {}'.format( inst.rs1, bits2float(a), inst.rs2, bits2float(b) )
  #print hex(out), bits2float( out ), '{:05b}'.format( s.fcsr )

  s.pc += 4

def execute_fsub_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.fp[ inst.rd ] = lib.f64_sub( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0

  s.pc += 4

def execute_fmul_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.fp[ inst.rd ] = lib.f64_mul( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0

  s.pc += 4

def execute_fdiv_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsgnj_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsgnjn_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsgnjx_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmin_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmax_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_s_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_d_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsqrt_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fle_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.rf[ inst.rd ] = lib.f32_le( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_flt_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.rf[ inst.rd ] = lib.f32_lt( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_feq_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.rf[ inst.rd ] = lib.f32_eq( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fle_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.rf[ inst.rd ] = lib.f64_le( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_flt_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.rf[ inst.rd ] = lib.f64_lt( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_feq_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.rf[ inst.rd ] = lib.f64_eq( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fcvt_w_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_wu_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_l_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_lu_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmv_x_s( s, inst ):
  s.rf[inst.rd] = sext_32( s.fp[inst.rs1] )
  s.pc += 4

def execute_fclass_s( s, inst ):
  s.rf[inst.rd] = lib.f32_classify( trim_32( s.fp[inst.rs1] ) )
  s.pc += 4

def execute_fcvt_w_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_wu_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_l_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_lu_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmv_x_d( s, inst ):
  s.rf[inst.rd] = s.fp[inst.rs1]
  s.pc += 4

def execute_fclass_d( s, inst ):
  s.rf[inst.rd] = lib.f64_classify( s.fp[inst.rs1] )
  s.pc += 4

def execute_fcvt_s_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_s_wu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_s_l( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_s_lu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmv_s_x( s, inst ):
  s.fp[inst.rd] = s.rf[inst.rs1]
  s.pc += 4

def execute_fcvt_d_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_d_wu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_d_l( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fcvt_d_lu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmv_d_x( s, inst ):
  s.fp[inst.rd] = s.rf[inst.rs1]
  s.pc += 4

def execute_flw( s, inst ):
  addr          = s.rf[inst.rs1] + inst.i_imm
  s.fp[inst.rd] = sext_32( s.mem.read( addr, 4 ) )
  s.pc += 4

def execute_fld( s, inst ):
  # TODO: make memory support 64-bit ops
  addr          = s.rf[inst.rs1] + inst.i_imm
  s.fp[inst.rd] = ( s.mem.read( addr+4, 4 ) << 32 ) \
                  | s.mem.read( addr, 4 )
  s.pc += 4

def execute_fsw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fsd( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmadd_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmsub_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fnmsub_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fnmadd_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmadd_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmsub_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fnmsub_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fnmadd_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom0( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom0_rs1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom0_rs1_rs2( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom0_rd( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom0_rd_rs1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom0_rd_rs1_rs2( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom1_rs1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom1_rs1_rs2( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom1_rd( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom1_rd_rs1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom1_rd_rs1_rs2( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom2( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom2_rs1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom2_rs1_rs2( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom2_rd( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom2_rd_rs1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom2_rd_rs1_rs2( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom3( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom3_rs1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom3_rs1_rs2( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom3_rd( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom3_rd_rs1( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_custom3_rd_rs1_rs2( s, inst ):
  raise NotImplementedError()
  s.pc += 4


#=======================================================================
# Create Decoder
#=======================================================================

decode = create_risc_decoder( encodings, globals(), debug=True )

