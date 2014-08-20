#=======================================================================
# isa.py
#=======================================================================

import py
import re

from utils    import rd, rs, rt, imm, jtarg, shamt
from utils    import trim, trim_5, signed, sext, sext_byte

# we mark pure (trace elidable) functions that don't have any side effects
from rpython.rlib.jit import elidable

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

  'zero' :  0,   'at'   :  1,   'v0'   :  2,   'v1'   :  3,
  'a0'   :  4,   'a1'   :  5,   'a2'   :  6,   'a3'   :  7,
  'a4'   :  8,   'a5'   :  9,   'a6'   : 10,   'a7'   : 11,
  't0'   : 12,   't1'   : 13,   't2'   : 14,   't3'   : 15,
# 't0'   :  8,   't1'   :  9,   't2'   : 10,   't3'   : 11, # old abi
# 't4'   : 12,   't5'   : 13,   't6'   : 14,   't7'   : 15, # old abi
  's0'   : 16,   's1'   : 17,   's2'   : 18,   's3'   : 19,
  's4'   : 20,   's5'   : 21,   's6'   : 22,   's7'   : 23,
  't8'   : 24,   't9'   : 25,   'k0'   : 26,   'k1'   : 27,
  'gp'   : 28,   'sp'   : 29,   's8'   : 30,   'ra'   : 31,

  # currently implemented coprocessor 0 registers

  'status'    :  1,   # mtc0
 #'mngr2proc' :  1,   #      mfc0
 #'proc2mngr' :  2,   # mtc0
  'statsen'   : 10,   # mtc0
  'coreid'    : 17,   #      mfc0

  # coprocesser 0 registers currently used by parcv3-scalar
  # https://github.com/cornell-brg/pyparc/tree/master/parcv3-scalar

  # TODO: better names as specificed in isa doc?
  # https://github.com/cornell-brg/maven-docs/blob/master/parc-isa.txt

  'c0_toserv'    :  1,  # mtc0
  'c0_fromserv'  :  2,  #      mfc0
  'c0_tosysc0'   :  3,  # mtc0
  'c0_tosysc1'   :  4,  # mtc0
  'c0_tosysc2'   :  5,  # mtc0
  'c0_tosysc3'   :  6,  # mtc0
  'c0_tosysc4'   :  7,  # mtc0
  'c0_tosysc5'   :  8,  # mtc0
  'c0_count'     :  9,  # mtc0 mfc0
  'c0_fromsysc0' : 10,  #      mfc0
  'c0_fromsysc1' : 11,  #      mfc0
  'c0_fromsysc2' : 12,  #      mfc0
  'c0_fromsysc3' : 13,  #      mfc0
  'c0_fromsysc4' : 14,  #      mfc0
  'c0_fromsysc5' : 15,  #      mfc0
  'c0_numcores'  : 16,  #      mfc0
  'c0_coreid'    : 17,  #      mfc0
  'c0_tidmask'   : 18,  # mtc0 mfc0
  'c0_tidstop'   : 19,  # mtc0 mfc0
  'c0_staten'    : 21,  # mtc0 mfc0
  'c0_counthi'   : 25,  # mtc0 mfc0
}

# Other useful register identifiers might be found in gem5, however,
# it would be nice to find a more authoritative source for these:
#
# - https://github.com/cornell-brg/gem5-mcpat/blob/master/src/arch/mips/registers.hh
#
# zero                  :  0
# assember              :  1
# syscall_success       :  7
# first_argument        :  4
# return_value          :  2
# kernel reg0           : 26
# kernel reg1           : 27
# global_pointer        : 28
# stack_pointer         : 29
# frame_pointer         : 30
# return_address        : 31
# syscall_pseudo_return :  3

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [
  ['nop',      '00000000000000000000000000000000'],
  # Coprocessor
  ['mfc0',     '01000000000xxxxxxxxxx00000000000'],
  ['mtc0',     '01000000100xxxxxxxxxx00000000000'],
  #['mtc2',    '01001000100xxxxxxxxxx00000000000'],
  # Arithmetic
  ['addu',     '000000xxxxxxxxxxxxxxx00000100001'],
  ['subu',     '000000xxxxxxxxxxxxxxx00000100011'],
  ['and',      '000000xxxxxxxxxxxxxxx00000100100'],
  ['or',       '000000xxxxxxxxxxxxxxx00000100101'],
  ['xor',      '000000xxxxxxxxxxxxxxx00000100110'],
  ['nor',      '000000xxxxxxxxxxxxxxx00000100111'],
  ['slt',      '000000xxxxxxxxxxxxxxx00000101010'],
  ['sltu',     '000000xxxxxxxxxxxxxxx00000101011'],
  # Arithmetic Immediate
  ['addiu',    '001001xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['andi',     '001100xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['ori',      '001101xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['xori',     '001110xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['slti',     '001010xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['sltiu',    '001011xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['lui',      '00111100000xxxxxxxxxxxxxxxxxxxxx'],
  # Shift
  ['sll',      '00000000000xxxxxxxxxxxxxxx000000'],
  ['srl',      '00000000000xxxxxxxxxxxxxxx000010'],
  ['sra',      '00000000000xxxxxxxxxxxxxxx000011'],
  ['sllv',     '000000xxxxxxxxxxxxxxx00000000100'],
  ['srlv',     '000000xxxxxxxxxxxxxxx00000000110'],
  ['srav',     '000000xxxxxxxxxxxxxxx00000000111'],
  # Mul/Div/Rem
  ['mul',      '011100xxxxxxxxxxxxxxx00000000010'],
  ['div',      '100111xxxxxxxxxxxxxxx00000000101'],
  ['divu',     '100111xxxxxxxxxxxxxxx00000000111'],
  ['rem',      '100111xxxxxxxxxxxxxxx00000000110'],
  ['remu',     '100111xxxxxxxxxxxxxxx00000001000'],
  # Loads
  ['lw',       '100011xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['lh',       '100001xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['lhu',      '100101xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['lb',       '100000xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['lbu',      '100100xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  # Stores
  ['sw',       '101011xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['sh',       '101001xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['sb',       '101000xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  # Jumps
  ['j',        '000010xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['jal',      '000011xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['jr',       '000000xxxxx000000000000000001000'],
  ['jalr',     '000000xxxxx00000xxxxx00000001001'],
  # Branches
  ['beq',      '000100xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['bne',      '000101xxxxxxxxxxxxxxxxxxxxxxxxxx'],
  ['blez',     '000110xxxxx00000xxxxxxxxxxxxxxxx'],
  ['bgtz',     '000111xxxxx00000xxxxxxxxxxxxxxxx'],
  ['bltz',     '000001xxxxx00000xxxxxxxxxxxxxxxx'],
  ['bgez',     '000001xxxxx00001xxxxxxxxxxxxxxxx'],
  # Conditional
  ['movn',    '000000xxxxxxxxxxxxxxx00000001011'],
  ['movz',    '000000xxxxxxxxxxxxxxx00000001010'],
  # Syscall
  ['syscall', '000000xxxxxxxxxxxxxxxxxxxx001100'],
  #['eret',    '000000xxxxxxxxxxxxxxxxxxxx001100'],
  # AMO
  #['amo_add',  '100111xxxxxxxxxxxxxxx00000000010'],
  #['amo_and',  '100111xxxxxxxxxxxxxxx00000000011'],
  ['amo_or',   '100111xxxxxxxxxxxxxxx00000000100'],
  #['amo_xchg', '100111xxxxxxxxxxxxxxx00000001101'],
  #['amo_min',  '100111xxxxxxxxxxxxxxx00000001110'],
  # Data-Parallel
  ['xloop',   '110100xxxxx00000xxxxxxxxxxxxxxxx'],
  ['stop',    '10011100000000000000000000000000'],
  ['utidx',   '1001110000000000xxxxx00000001001'],
  ['mtuts',   '01001000000xxxxxxxxxx00000001000'],
  ['mfuts',   '010010xxxxxxxxxxxxxxx00000001001'],
  # ???
  #['syncl',   '10011100000000000000000000000001'],
  #['stat',    '10011100000xxxxx0000000000001111'],
  # Floating Point
  #['add_s',   '010001xxxxxxxxxxxxxxxxxxxx000000'],
  #['sub_s',   '010001xxxxxxxxxxxxxxxxxxxx000001'],
  #['mul_s',   '010001xxxxxxxxxxxxxxxxxxxx000010'],
  #['div_s',   '010001xxxxxxxxxxxxxxxxxxxx000011'],
  #['c_eq_s',  '01000110000xxxxxxxxxxxxxxx110010'],
  #['c_lt_s',  '01000110000xxxxxxxxxxxxxxx111100'],
  #['c_le_s',  '01000110000xxxxxxxxxxxxxxx111110'],
  #['cvt_w_s', '0100011000000000xxxxxxxxxx100100'],
  #['cvt_s_w', '0100011010000000xxxxxxxxxx100000'],
  #['trunc',   '0100011000000000xxxxxxxxxx001101'],
]

#=======================================================================
# Instruction Definitions
#=======================================================================

#-----------------------------------------------------------------------
# Coprocessor 0 Instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# nop
#-----------------------------------------------------------------------
def execute_nop( s, inst ):
  s.pc += 4

#-----------------------------------------------------------------------
# mfc0
#-----------------------------------------------------------------------
def execute_mfc0( s, inst ):
  #if   rd(inst) ==  1: pass
  #  s.rf[ rt(inst) ] = src[ s.src_ptr ]
  #  s.src_ptr += 1
  if   rd(inst) == reg_map['c0_coreid']:
    s.rf[rt(inst)] = 0
  elif rd(inst) == reg_map['c0_numcores']:
    s.rf[rt(inst)] = 1
  else:
    raise Exception('Invalid mfc0 destination: %d!' % rd(inst) )
  s.pc += 4

#-----------------------------------------------------------------------
# mtc0
#-----------------------------------------------------------------------
def execute_mtc0( s, inst ):
  if   rd(inst) == reg_map['status']:
    print 'SETTING STATUS'
    s.status = s.rf[rt(inst)]
  elif rd(inst) == reg_map['statsen']:
    s.stats_en = s.rf[rt(inst)]
  #elif rd(inst) ==  2: pass
  #  if sink[ s.sink_ptr ] != s.rf[ rt(inst) ]:
  #    print 'sink:', sink[ s.sink_ptr ], 's.rf:', s.rf[ rt(inst) ]
  #    raise Exception('Instruction: mtc0 failed!')
  #  print 'SUCCESS: s.rf[' + str( rt(inst) ) + '] == ' + str( sink[ s.sink_ptr ] )
  #  s.sink_ptr += 1
  else:
    raise Exception('Invalid mtc0 destination!')
  s.pc += 4

#-----------------------------------------------------------------------
# Register-register arithmetic, logical, and comparison instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# addu
#-----------------------------------------------------------------------
def execute_addu( s, inst ):
  s.rf[ rd(inst) ] = trim( s.rf[ rs(inst) ] + s.rf[ rt(inst) ] )
  s.pc += 4

#-----------------------------------------------------------------------
# subu
#-----------------------------------------------------------------------
def execute_subu( s, inst ):
  s.rf[rd(inst)] = trim( s.rf[rs(inst)] - s.rf[rt(inst)] )
  s.pc += 4

#-----------------------------------------------------------------------
# and
#-----------------------------------------------------------------------
def execute_and( s, inst ):
  s.rf[rd(inst)] = s.rf[rs(inst)] & s.rf[rt(inst)]
  s.pc += 4

#-----------------------------------------------------------------------
# or
#-----------------------------------------------------------------------
def execute_or( s, inst ):
  s.rf[rd(inst)] = s.rf[rs(inst)] | s.rf[rt(inst)]
  s.pc += 4

#-----------------------------------------------------------------------
# xor
#-----------------------------------------------------------------------
def execute_xor( s, inst ):
  s.rf[rd(inst)] = s.rf[rs(inst)] ^ s.rf[rt(inst)]
  s.pc += 4

#-----------------------------------------------------------------------
# nor
#-----------------------------------------------------------------------
def execute_nor( s, inst ):
  s.rf[rd(inst)] = trim( ~(s.rf[rs(inst)] | s.rf[rt(inst)]) )
  s.pc += 4

#-----------------------------------------------------------------------
# slt
#-----------------------------------------------------------------------
def execute_slt( s, inst ):
  s.rf[rd(inst)] = signed( s.rf[rs(inst)] ) < signed( s.rf[rt(inst)] )
  s.pc += 4

#-----------------------------------------------------------------------
# sltu
#-----------------------------------------------------------------------
def execute_sltu( s, inst ):
  s.rf[rd(inst)] = s.rf[rs(inst)] < s.rf[rt(inst)]
  s.pc += 4

#-----------------------------------------------------------------------
# mul
#-----------------------------------------------------------------------
def execute_mul( s, inst ):
  s.rf[ rd(inst) ] = trim( s.rf[ rs(inst) ] * s.rf[ rt(inst) ] )
  s.pc += 4

#-----------------------------------------------------------------------
# div
#-----------------------------------------------------------------------
# http://stackoverflow.com/a/6084608
def execute_div( s, inst ):
  x    = signed( s.rf[ rs(inst) ] )
  y    = signed( s.rf[ rt(inst) ] )
  sign = -1 if (x < 0)^(y < 0) else 1

  s.rf[ rd(inst) ] = abs(x) / abs(y) * sign
  s.pc += 4

#-----------------------------------------------------------------------
# divu
#-----------------------------------------------------------------------
def execute_divu( s, inst ):
  s.rf[ rd(inst) ] = s.rf[ rs(inst) ] / s.rf[ rt(inst) ]
  s.pc += 4

#-----------------------------------------------------------------------
# rem
#-----------------------------------------------------------------------
# http://stackoverflow.com/a/6084608
def execute_rem( s, inst ):
  x = signed( s.rf[ rs(inst) ] )
  y = signed( s.rf[ rt(inst) ] )

  s.rf[ rd(inst) ] = abs(x) % abs(y) * (1 if x > 0 else -1)
  s.pc += 4

#-----------------------------------------------------------------------
# remu
#-----------------------------------------------------------------------
def execute_remu( s, inst ):
  s.rf[ rd(inst) ] = s.rf[ rs(inst) ] % s.rf[ rt(inst) ]
  s.pc += 4

#-----------------------------------------------------------------------
# Register-imm(inst)ediate arithmetic, logical, and comparison instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# addiu
#-----------------------------------------------------------------------
def execute_addiu( s, inst ):
  s.rf[ rt(inst) ] = trim( s.rf[ rs(inst) ] + sext( imm(inst) ) )
  s.pc += 4

#-----------------------------------------------------------------------
# andi
#-----------------------------------------------------------------------
def execute_andi( s, inst ):
  s.rf[rt(inst)] = s.rf[rs(inst)] & imm(inst)
  s.pc += 4

#-----------------------------------------------------------------------
# ori
#-----------------------------------------------------------------------
def execute_ori( s, inst ):
  s.rf[rt(inst)] = s.rf[rs(inst)] | imm(inst)
  s.pc += 4

#-----------------------------------------------------------------------
# xori
#-----------------------------------------------------------------------
def execute_xori( s, inst ):
  s.rf[rt(inst)] = s.rf[rs(inst)] ^ imm(inst)
  s.pc += 4

#-----------------------------------------------------------------------
# slti
#-----------------------------------------------------------------------
def execute_slti( s, inst ):
  s.rf[rt(inst)] = signed( s.rf[rs(inst)] ) < signed( sext(imm(inst)) )
  s.pc += 4

#-----------------------------------------------------------------------
# sltiu
#-----------------------------------------------------------------------
def execute_sltiu( s, inst ):
  s.rf[rt(inst)] = s.rf[rs(inst)] < sext(imm(inst))
  s.pc += 4

#-----------------------------------------------------------------------
# Shift instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# sll
#-----------------------------------------------------------------------
def execute_sll( s, inst ):
  s.rf[rd(inst)] = trim( s.rf[rt(inst)] << shamt(inst) )
  s.pc += 4

#-----------------------------------------------------------------------
# srl
#-----------------------------------------------------------------------
def execute_srl( s, inst ):
  s.rf[rd(inst)] = s.rf[rt(inst)] >> shamt(inst)
  s.pc += 4

#-----------------------------------------------------------------------
# sra
#-----------------------------------------------------------------------
def execute_sra( s, inst ):
  s.rf[rd(inst)] = trim( signed( s.rf[rt(inst)] ) >> shamt(inst) )
  s.pc += 4

#-----------------------------------------------------------------------
# sllv
#-----------------------------------------------------------------------
def execute_sllv( s, inst ):
  s.rf[rd(inst)] = trim( s.rf[rt(inst)] << trim_5( s.rf[rs(inst)] ) )
  s.pc += 4

#-----------------------------------------------------------------------
# srlv
#-----------------------------------------------------------------------
def execute_srlv( s, inst ):
  s.rf[rd(inst)] = s.rf[rt(inst)] >> trim_5( s.rf[rs(inst)] )
  s.pc += 4

#-----------------------------------------------------------------------
# srav
#-----------------------------------------------------------------------
def execute_srav( s, inst ):
  # TODO: should it really be masked like this?
  s.rf[rd(inst)] = trim( signed( s.rf[rt(inst)] ) >> trim_5( s.rf[rs(inst)] ) )
  s.pc += 4

#-----------------------------------------------------------------------
# Unconditional jump instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# j
#-----------------------------------------------------------------------
def execute_j( s, inst ):
  s.pc = ((s.pc + 4) & 0xF0000000) | (jtarg(inst) << 2)

#-----------------------------------------------------------------------
# jal
#-----------------------------------------------------------------------
def execute_jal( s, inst ):
  s.rf[31] = s.pc + 4
  s.pc = ((s.pc + 4) & 0xF0000000) | (jtarg(inst) << 2)

#-----------------------------------------------------------------------
# jr
#-----------------------------------------------------------------------
def execute_jr( s, inst ):
  s.pc = s.rf[rs(inst)]

#-----------------------------------------------------------------------
# jalr
#-----------------------------------------------------------------------
def execute_jalr( s, inst ):
  s.rf[rd(inst)] = s.pc + 4
  s.pc   = s.rf[rs(inst)]

#-----------------------------------------------------------------------
# lui
#-----------------------------------------------------------------------
def execute_lui( s, inst ):
  s.rf[ rt(inst) ] = imm(inst) << 16
  s.pc += 4


#-----------------------------------------------------------------------
# Conditional branch instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# beq
#-----------------------------------------------------------------------
def execute_beq( s, inst ):
  if s.rf[rs(inst)] == s.rf[rt(inst)]:
    s.pc  = s.pc + 4 + (signed(sext(imm(inst))) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# bne
#-----------------------------------------------------------------------
def execute_bne( s, inst ):
  if s.rf[rs(inst)] != s.rf[rt(inst)]:
    s.pc  = s.pc + 4 + (signed(sext(imm(inst))) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# blez
#-----------------------------------------------------------------------
def execute_blez( s, inst ):
  if signed( s.rf[rs(inst)] ) <= 0:
    s.pc  = s.pc + 4 + (signed(sext(imm(inst))) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# bgtz
#-----------------------------------------------------------------------
def execute_bgtz( s, inst ):
  if signed( s.rf[rs(inst)] ) > 0:
    s.pc  = s.pc + 4 + (signed(sext(imm(inst))) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# bltz
#-----------------------------------------------------------------------
def execute_bltz( s, inst ):
  if signed( s.rf[rs(inst)] ) < 0:
    s.pc  = s.pc + 4 + (signed(sext(imm(inst))) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# bgez
#-----------------------------------------------------------------------
def execute_bgez( s, inst ):
  if signed( s.rf[rs(inst)] ) >= 0:
    s.pc  = s.pc + 4 + (signed(sext(imm(inst))) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# Load instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# lw
#-----------------------------------------------------------------------
def execute_lw( s, inst ):
  addr = trim( s.rf[rs(inst)] + sext(imm(inst)) )
  s.rf[rt(inst)] = s.mem.read( addr, 4 )
  s.pc += 4

#-----------------------------------------------------------------------
# lh
#-----------------------------------------------------------------------
def execute_lh( s, inst ):
  addr = trim( s.rf[rs(inst)] + sext(imm(inst)) )
  s.rf[rt(inst)] = sext( s.mem.read( addr, 2 ) )
  s.pc += 4

#-----------------------------------------------------------------------
# lhu
#-----------------------------------------------------------------------
def execute_lhu( s, inst ):
  addr = trim( s.rf[rs(inst)] + sext(imm(inst)) )
  s.rf[rt(inst)] = s.mem.read( addr, 2 )
  s.pc += 4

#-----------------------------------------------------------------------
# lb
#-----------------------------------------------------------------------
def execute_lb( s, inst ):
  addr = trim( s.rf[rs(inst)] + sext(imm(inst)) )
  s.rf[rt(inst)] = sext_byte( s.mem.read( addr, 1 ) )
  s.pc += 4

#-----------------------------------------------------------------------
# lbu
#-----------------------------------------------------------------------
def execute_lbu( s, inst ):
  addr = trim( s.rf[rs(inst)] + sext(imm(inst)) )
  s.rf[rt(inst)] = s.mem.read( addr, 1 )
  s.pc += 4

#-----------------------------------------------------------------------
# Store instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# sw
#-----------------------------------------------------------------------
def execute_sw( s, inst ):
  addr = trim( s.rf[rs(inst)] + sext(imm(inst)) )
  s.mem.write( addr, 4, s.rf[rt(inst)] )
  s.pc += 4

#-----------------------------------------------------------------------
# sh
#-----------------------------------------------------------------------
def execute_sh( s, inst ):
  addr = trim( s.rf[rs(inst)] + sext(imm(inst)) )
  s.mem.write( addr, 2, s.rf[rt(inst)] )
  s.pc += 4

#-----------------------------------------------------------------------
# sb
#-----------------------------------------------------------------------
def execute_sb( s, inst ):
  addr = trim( s.rf[rs(inst)] + sext(imm(inst)) )
  s.mem.write( addr, 1, s.rf[rt(inst)] )
  s.pc += 4

#-----------------------------------------------------------------------
# movn
#-----------------------------------------------------------------------
def execute_movn( s, inst ):
  if s.rf[rt(inst)] != 0:
    s.rf[rd(inst)] = s.rf[rs(inst)]
  s.pc += 4

#-----------------------------------------------------------------------
# movz
#-----------------------------------------------------------------------
def execute_movz( s, inst ):
  if s.rf[rt(inst)] == 0:
    s.rf[rd(inst)] = s.rf[rs(inst)]
  s.pc += 4

#-----------------------------------------------------------------------
# Syscall instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# syscall
#-----------------------------------------------------------------------
from syscalls import syscall_funcs
def execute_syscall( s, inst ):
  v0 = reg_map['v0']
  syscall_number = s.rf[ v0 ]
  syscall_funcs[ syscall_number ]( s )
  s.pc += 4

#-----------------------------------------------------------------------
# Atomic Memory Operation instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# amo.or
#-----------------------------------------------------------------------
def execute_amo_or( s, inst ):
  temp = s.mem.read( s.rf[ rs(inst) ], 4 )
  val  = temp | s.rf[ rt(inst) ]
  s.mem.write( s.rf[ rs(inst) ], 4, val )
  s.rf[ rd(inst) ] = temp
  s.pc += 4

#-----------------------------------------------------------------------
# Data-Parallel
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# xloop
#-----------------------------------------------------------------------
def execute_xloop( s, inst ):
  print 'WARNING: xloop implemented as noop!'
  s.pc += 4

#-----------------------------------------------------------------------
# stop
#-----------------------------------------------------------------------
def execute_stop( s, inst ):
  print 'WARNING: stop implemented as noop!'
  s.pc += 4

#-----------------------------------------------------------------------
# stop
#-----------------------------------------------------------------------
def execute_utidx( s, inst ):
  print 'WARNING: utidx implemented as noop!'
  s.pc += 4

#-----------------------------------------------------------------------
# mtuts
#-----------------------------------------------------------------------
def execute_mtuts( s, inst ):
  print 'WARNING: mtuts implemented as noop!'
  s.pc += 4

#-----------------------------------------------------------------------
# mfuts
#-----------------------------------------------------------------------
def execute_mfuts( s, inst ):
  raise Exception('mfuts is unsupported!')
  s.pc += 4

#-----------------------------------------------------------------------
# TEMPORARY
#-----------------------------------------------------------------------
#masks = [
#['mfc0',  0xffe007ff, 0x40000000 ],
#['mtc0',  0xffe007ff, 0x40800000 ],
#['addu',  0xfc0007ff, 0x00000021 ],
#['subu',  0xfc0007ff, 0x00000023 ],
#['and',   0xfc0007ff, 0x00000024 ],
#['or',    0xfc0007ff, 0x00000025 ],
#['xor',   0xfc0007ff, 0x00000026 ],
#['nor',   0xfc0007ff, 0x00000027 ],
#['slt',   0xfc0007ff, 0x0000002a ],
#['sltu',  0xfc0007ff, 0x0000002b ],
#['addiu', 0xfc000000, 0x24000000 ],
#['andi',  0xfc000000, 0x30000000 ],
#['ori',   0xfc000000, 0x34000000 ],
#['xori',  0xfc000000, 0x38000000 ],
#['slti',  0xfc000000, 0x28000000 ],
#['sltiu', 0xfc000000, 0x2c000000 ],
#['sll',   0xffe0003f, 0x00000000 ],
#['srl',   0xffe0003f, 0x00000002 ],
#['sra',   0xffe0003f, 0x00000003 ],
#['sllv',  0xfc0007ff, 0x00000004 ],
#['srlv',  0xfc0007ff, 0x00000006 ],
#['srav',  0xfc0007ff, 0x00000007 ],
#['lui',   0xffe00000, 0x3c000000 ],
#['mul',   0xfc0007ff, 0x70000002 ],
#['div',   0xfc0007ff, 0x9c000005 ],
#['divu',  0xfc0007ff, 0x9c000007 ],
#['rem',   0xfc0007ff, 0x9c000006 ],
#['remu',  0xfc0007ff, 0x9c000008 ],
#['lw',    0xfc000000, 0x8c000000 ],
#['lh',    0xfc000000, 0x84000000 ],
#['lhu',   0xfc000000, 0x94000000 ],
#['lb',    0xfc000000, 0x80000000 ],
#['lbu',   0xfc000000, 0x90000000 ],
#['sw',    0xfc000000, 0xac000000 ],
#['sh',    0xfc000000, 0xa4000000 ],
#['sb',    0xfc000000, 0xa0000000 ],
#['j',     0xfc000000, 0x08000000 ],
#['jal',   0xfc000000, 0x0c000000 ],
#['jr',    0xfc1fffff, 0x00000008 ],
#['jalr',  0xfc1f07ff, 0x00000009 ],
#['beq',   0xfc000000, 0x10000000 ],
#['bne',   0xfc000000, 0x14000000 ],
#['blez',  0xfc1f0000, 0x18000000 ],
#['bgtz',  0xfc1f0000, 0x1c000000 ],
#['bltz',  0xfc1f0000, 0x04000000 ],
#['bgez',  0xfc1f0000, 0x04010000 ],
#['mtc2',  0xffe007ff, 0x48800000 ],
#]
#
#for inst, m, x in masks:
#  mstr = '{:032b}'.format(m)
#  xstr = '{:032b}'.format(x)
#  out  = ''
#  for mbit, xbit in zip( mstr, xstr ):
#    if   mbit == '0': out += 'x'
#    else:             out += xbit
#  print '{:8} {}'.format( inst, out )

#-----------------------------------------------------------------------
# Create Decode Table
#-----------------------------------------------------------------------

inst_nbits = len( encodings[0][1] )

def split_encodings( enc ):
  return [x for x in re.split( '(x*)', enc ) if x]

bit_fields = [ split_encodings( enc ) for inst, enc in encodings ]

# This approach allows us to automatically generate trees for
# table-based decoders. However a previous paper indicates that
# siwtch-based decoders are better for performance.
#
#   http://web.eecs.umich.edu/~taustin/papers/WBT01-decode.pdf
#
def normalize_fields( bit_fields ):

  field_idx  = 0
  bit_idx    = 0

  while bit_idx < inst_nbits:

    this_field_nbits = min( [len(x) for x in  zip( *bit_fields)[field_idx]] )

    new_bit_fields = []

    for inst in bit_fields:

      if len( inst[field_idx] ) == this_field_nbits:
        new_bit_fields.append( inst )
        continue

      split_a  = inst[field_idx][0:this_field_nbits]
      split_b  = inst[field_idx][this_field_nbits:]
      new_inst = inst[0:field_idx] + [split_a, split_b] + inst[field_idx+1:]
      new_bit_fields.append( new_inst )

    field_idx += 1
    bit_idx   += this_field_nbits
    bit_fields = new_bit_fields

  return bit_fields

#bit_fields = normalize_fields( bit_fields )

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


