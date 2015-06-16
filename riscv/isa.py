#=======================================================================
# isa.py
#=======================================================================

from pydgin.misc import create_risc_decoder, FatalError
from utils import sext_32, signed
from helpers import *

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

def sext_xlen( val ):
  return val

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
  # TODO, is this right?
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] >> SHAMT( s, inst ) )
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
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] >> (s.rf[inst.rs2] & 0x1F) )
  s.pc += 4

def execute_sraw( s, inst ):
  s.rf[ inst.rd ] = sext_32( s.rf[inst.rs1] >> (s.rf[inst.rs2] & 0x1F) )
  s.pc += 4

def execute_lb( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_lh( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_lw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_ld( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_lbu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_lhu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_lwu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sb( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sh( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sd( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fence( s, inst ):
  s.pc += 4

def execute_fence_i( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_mul( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_mulh( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_mulhsu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_mulhu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_div( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_divu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_rem( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_remu( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_mulw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_divw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_divuw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_remw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_remuw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoadd_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoxor_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoor_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoand_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amomin_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amomax_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amominu_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amomaxu_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoswap_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_lr_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sc_w( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoadd_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoxor_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoor_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoand_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amomin_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amomax_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amominu_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amomaxu_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_amoswap_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_lr_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_sc_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_scall( s, inst ):
  raise NotImplementedError()
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

def execute_csrrw( s, inst ):
  result = s.rf[inst.rs1]
  if result & 0x1:
    status = result >> 1
    if status: raise FatalError("Fail! {}".format( result >> 1 ) )
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
  raise NotImplementedError()
  s.pc += 4

def execute_fsub_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmul_s( s, inst ):
  raise NotImplementedError()
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
  raise NotImplementedError()
  s.pc += 4

def execute_fsub_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fmul_d( s, inst ):
  raise NotImplementedError()
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
  raise NotImplementedError()
  s.pc += 4

def execute_flt_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_feq_s( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fle_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_flt_d( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_feq_d( s, inst ):
  raise NotImplementedError()
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
  raise NotImplementedError()
  s.pc += 4

def execute_fclass_s( s, inst ):
  raise NotImplementedError()
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
  raise NotImplementedError()
  s.pc += 4

def execute_fclass_d( s, inst ):
  raise NotImplementedError()
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
  raise NotImplementedError()
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
  raise NotImplementedError()
  s.pc += 4

def execute_flw( s, inst ):
  raise NotImplementedError()
  s.pc += 4

def execute_fld( s, inst ):
  raise NotImplementedError()
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

