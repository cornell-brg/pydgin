#=======================================================================
# isa.py
#=======================================================================

from utils import trim, trim_5, signed, sext, sext_byte, \
                  bits2float, float2bits

from instruction  import rd, rs, rt, fd, fs, ft, imm, jtarg, shamt
from pydgin.misc  import create_risc_decoder
from polyhs_types import *

# shreesha: to implement a gcd instruction
#from fractions import gcd

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
# ['eret',    '000000xxxxxxxxxxxxxxxxxxxx001100'],
  # AMO
  ['amo_add',  '100111xxxxxxxxxxxxxxx00000000010'],
  ['amo_and',  '100111xxxxxxxxxxxxxxx00000000011'],
  ['amo_or',   '100111xxxxxxxxxxxxxxx00000000100'],
# ['amo_xchg', '100111xxxxxxxxxxxxxxx00000001101'],
# ['amo_min',  '100111xxxxxxxxxxxxxxx00000001110'],
  # Data-Parallel
  ['xloop',   '110100xxxxx00000xxxxxxxxxxxxxxxx'],
  ['stop',    '10011100000000000000000000000000'],
  ['utidx',   '1001110000000000xxxxx00000001001'],
  ['mtuts',   '01001000000xxxxxxxxxx00000001000'],
  ['mfuts',   '010010xxxxxxxxxxxxxxx00000001001'],
  # ???
# ['syncl',   '10011100000000000000000000000001'],
# ['stat',    '10011100000xxxxx0000000000001111'],
  # Floating Point
  ['add_s',   '010001xxxxxxxxxxxxxxxxxxxx000000'],
  ['sub_s',   '010001xxxxxxxxxxxxxxxxxxxx000001'],
  ['mul_s',   '010001xxxxxxxxxxxxxxxxxxxx000010'],
  ['div_s',   '010001xxxxxxxxxxxxxxxxxxxx000011'],
  ['c_eq_s',  '01000110000xxxxxxxxxxxxxxx110010'],
  ['c_lt_s',  '01000110000xxxxxxxxxxxxxxx111100'],
  ['c_le_s',  '01000110000xxxxxxxxxxxxxxx111110'],
# ['c_f_s',   '01000110000xxxxxxxxxxxxxxx110000'],
# ['c_un_s',  '01000110000xxxxxxxxxxxxxxx110001'],
# ['c_ngl_s', '01000110000xxxxxxxxxxxxxxx111011'],
# ['c_nge_s'  '01000110000xxxxxxxxxxxxxxx111101'],
# ['c_ngt_s', '01000110000xxxxxxxxxxxxxxx111111'],
  ['cvt_w_s', '0100011000000000xxxxxxxxxx100100'],
  ['cvt_s_w', '0100011010000000xxxxxxxxxx100000'],
 ['trunc_w_s','0100011000000000xxxxxxxxxx001101'],
  # shreesha: gcd instruction
 #['gcd',      '100111xxxxxxxxxxxxxxx00000010011'],
  # shreesha: polyhs extensions
 ['ds_get',   '100111xxxxxxxxxxxxxxx00000010011'],
 ['ds_set',   '100111xxxxxxxxxxxxxxx00000010100'],
 ['ds_init',  '100111xxxxxxxxxxxxxxx00000010101'],
 ['ds_alloc', '00100000000xxxxxxxxxxxxxxxxxxxxx'],
 ['ds_dealloc','100111xxxxx000000000000000010110'],
 ['ds_halt',  '10011100000000000000000000010111'],

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
  elif rd(inst) == reg_map['c0_count']:
    s.rf[rt(inst)] = s.ncycles
  elif rd(inst) == reg_map['c0_numcores']:
    s.rf[rt(inst)] = 1
  elif rd(inst) == reg_map['c0_counthi']:
    print "WARNING: counthi always returns 0..."
    s.rf[rt(inst)] = 0
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
  elif rd(inst) == reg_map['c0_staten']:
    s.stats_en = s.rf[rt(inst)]
    if s.stats_en == 0:
      print
      print 'STATS OFF! Terminating!'
      print 'timing cycles: %d' % (s.stat_ncycles)
      print 'total  cycles: %d' % (s.ncycles)
      # TODO: this is an okay way to terminate the simulator?
      #       sys.exit(1) is not valid python
      s.status = 1
      s.running = False
  #elif rd(inst) ==  2: pass
  #  if sink[ s.sink_ptr ] != s.rf[ rt(inst) ]:
  #    print 'sink:', sink[ s.sink_ptr ], 's.rf:', s.rf[ rt(inst) ]
  #    raise Exception('Instruction: mtc0 failed!')
  #  print 'SUCCESS: s.rf[' + str( rt(inst) ) + '] == ' + str( sink[ s.sink_ptr ] )
  #  s.sink_ptr += 1
  else:
    raise Exception('Invalid mtc0 destination: %d!' % rd(inst) )
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
  if syscall_number in syscall_funcs:
    syscall_funcs[ syscall_number ]( s )
  else:
    print "WARNING: syscall not implemented!", syscall_number
  s.pc += 4

#-----------------------------------------------------------------------
# Atomic Memory Operation instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# amo.add
#-----------------------------------------------------------------------
def execute_amo_add( s, inst ):
  temp = s.mem.read( s.rf[ rs(inst) ], 4 )
  s.mem.write( s.rf[rs(inst)], 4, trim(temp + s.rf[rt(inst)]) )
  s.rf[ rd(inst) ] = temp
  s.pc += 4

#-----------------------------------------------------------------------
# amo.and
#-----------------------------------------------------------------------
def execute_amo_and( s, inst ):
  temp = s.mem.read( s.rf[ rs(inst) ], 4 )
  s.mem.write( s.rf[rs(inst)], 4, temp & s.rf[rt(inst)] )
  s.rf[ rd(inst) ] = temp
  s.pc += 4

#-----------------------------------------------------------------------
# amo.or
#-----------------------------------------------------------------------
def execute_amo_or( s, inst ):
  temp = s.mem.read( s.rf[ rs(inst) ], 4 )
  s.mem.write( s.rf[rs(inst)], 4, temp | s.rf[rt(inst)] )
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
# utidx
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
# Floating-Point Instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# add_s
#-----------------------------------------------------------------------
def execute_add_s( s, inst ):
  a = bits2float( s.rf[ fs( inst ) ] )
  b = bits2float( s.rf[ ft( inst ) ] )
  s.rf[ fd( inst ) ] = float2bits( a + b )
  s.pc += 4

#-----------------------------------------------------------------------
# sub_s
#-----------------------------------------------------------------------
def execute_sub_s( s, inst ):
  a = bits2float( s.rf[ fs( inst ) ] )
  b = bits2float( s.rf[ ft( inst ) ] )
  s.rf[ fd( inst ) ] = float2bits( a - b )
  s.pc += 4

#-----------------------------------------------------------------------
# mul_s
#-----------------------------------------------------------------------
def execute_mul_s( s, inst ):
  a = bits2float( s.rf[ fs( inst ) ] )
  b = bits2float( s.rf[ ft( inst ) ] )
  s.rf[ fd( inst ) ] = float2bits( a * b )
  s.pc += 4

#-----------------------------------------------------------------------
# div_s
#-----------------------------------------------------------------------
def execute_div_s( s, inst ):
  a = bits2float( s.rf[ fs( inst ) ] )
  b = bits2float( s.rf[ ft( inst ) ] )
  s.rf[ fd( inst ) ] = float2bits( a / b )
  s.pc += 4

#-----------------------------------------------------------------------
# c_eq_s
#-----------------------------------------------------------------------
def execute_c_eq_s( s, inst ):
  a = bits2float( s.rf[ fs( inst ) ] )
  b = bits2float( s.rf[ ft( inst ) ] )
  s.rf[ fd(inst) ] = 1 if a == b else 0
  s.pc += 4

#-----------------------------------------------------------------------
# c_lt_s
#-----------------------------------------------------------------------
def execute_c_lt_s( s, inst ):
  a = bits2float( s.rf[ fs( inst ) ] )
  b = bits2float( s.rf[ ft( inst ) ] )
  s.rf[ fd(inst) ] = 1 if a < b else 0
  s.pc += 4

#-----------------------------------------------------------------------
# c_le_s
#-----------------------------------------------------------------------
def execute_c_le_s( s, inst ):
  a = bits2float( s.rf[ fs( inst ) ] )
  b = bits2float( s.rf[ ft( inst ) ] )
  s.rf[ fd(inst) ] = 1 if a <= b else 0
  s.pc += 4

#-----------------------------------------------------------------------
# cvt_w_s
#-----------------------------------------------------------------------
def execute_cvt_w_s( s, inst ):
  x = bits2float( s.rf[ fs( inst ) ] )
  s.rf[ fd(inst) ] = trim( int( x ) )
  s.pc += 4

#-----------------------------------------------------------------------
# cvt_s_w
#-----------------------------------------------------------------------
def execute_cvt_s_w( s, inst ):
  x = signed( s.rf[ fs( inst ) ] )
  s.rf[ fd(inst) ] = float2bits( float( x ) )
  s.pc += 4

#-----------------------------------------------------------------------
# trunc_w_s
#-----------------------------------------------------------------------
def execute_trunc_w_s( s, inst ):
  # TODO: check for overflow
  x = bits2float( s.rf[ fs(inst) ] )
  s.rf[ fd(inst) ] = trim(int(x))  # round down
  s.pc += 4

##-----------------------------------------------------------------------
## gcd
##-----------------------------------------------------------------------
#def execute_gcd( s, inst ):
#  s.rf[ rd(inst) ] = trim( gcd( s.rf[ rs(inst) ], s.rf[ rt(inst) ] ) )
#  s.pc += 4

##-----------------------------------------------------------------------
## gcd -- fake vecincr accelerator
##-----------------------------------------------------------------------
#def execute_gcd( s, inst ):
#  src_base  = s.rf[ rs(inst) ]
#  dest_base = s.rf[ rd(inst) ]
#  len_ = s.rf[ rt(inst) ]
#  for off in range( len_ ):
#    src_addr  = src_base  + ( off * 4 )
#    dest_addr = dest_base + ( off * 4 )
#    update    = s.mem.read( src_addr, 4 ) + 1
#    s.mem.write( dest_addr, 4, update )
#  s.pc += 4

#-----------------------------------------------------------------------
# ds_alloc instruction
#-----------------------------------------------------------------------
def execute_ds_alloc( s, inst ):
  # determine the next available index in s.dstruct
  index = 0
  for x in xrange( 0, s.ds_table.num_regs ):
    if s.ds_table[ x ] == 0:
      index = x
      break

  if index < s.ds_table.num_regs:
    s.ds_type[ index ] = imm( inst )
    s.rf[ rt(inst) ]   = index
  else:
    s.rf[ rt(inst) ] = -1
  s.pc += 4

#-----------------------------------------------------------------------
# ds_dealloc instruction
#-----------------------------------------------------------------------
def execute_ds_dealloc( s , inst ):
  s.ds_table[ s.rf[ rs(inst) ] ] = 0
  s.pc += 4

#-----------------------------------------------------------------------
# ds_init instruction
#-----------------------------------------------------------------------
def execute_ds_init( s, inst ):
  s.ds_table[ s.rf[ rd(inst) ] ] = s.rf[ rs(inst) ]
  s.dt_table[ s.rf[ rd(inst) ] ] = s.rf[ rt(inst) ]
  s.pc += 4

#-----------------------------------------------------------------------
# ds_halt instruction
#-----------------------------------------------------------------------
def execute_ds_halt( s, inst ):
  s.pc += 4

#-----------------------------------------------------------------------
# ds_get instruction
#-----------------------------------------------------------------------
def execute_ds_get( s, inst ):

  # get the index for ds_table, dt_table
  iterator = iterator_fields( s.rf[ rs( inst ) ] )
  dstruct  = s.ds_type[ iterator[0] ]

  if dstruct  == VECTOR:
    # get the base address
    base_addr = s.ds_table[ iterator[0] ]
    dt_ptr    = s.dt_table[ iterator[0] ]
    metadata  = s.mem.read( dt_ptr, 4 )
    dt_desc   = dt_desc_fields( metadata )

    # PRIMITIVE TYPES
    if    dt_desc[2] == 0:
      # base + ( index * sizeof( T ) )
      mem_addr = base_addr + ( iterator[1] * dt_desc[1] )
      # load memory location
      s.rf[ rd(inst) ] = s.mem.read( mem_addr, dt_desc[1] )
    # USER-DEFINED TYPES
    elif dt_desc[2] == 1:
      #   1. get metadata of the field
      #       dt_ptr = dt_ptr * index
      #       metadata_field = load from dt_ptr
      #   2. compute mem_addr
      #      mem_addr = base_addr + ( index * sizeof( T ) )
      #                   + offset_of_field
      #   3. load value
      #      mem_read( mem_addr, sizeof( field )
      field_dt_ptr   = dt_ptr + rt( inst ) * 4
      field_metadata = s.mem.read( field_dt_ptr, 4 )
      field_dt_desc  = dt_desc_fields( field_metadata )
      # base + ( index * sizeof( T ) ) + offset
      mem_addr = \
        base_addr + ( iterator[1] * dt_desc[1] ) + field_dt_desc[0]
      # load memory location
      s.rf[ rd(inst) ] = s.mem.read( mem_addr, field_dt_desc[1] )

  s.pc += 4

#-----------------------------------------------------------------------
# ds_set instruction
#-----------------------------------------------------------------------
def execute_ds_set( s, inst ):

  # get the index for ds_table, dt_table
  iterator = iterator_fields( s.rf[ rd( inst ) ] )
  dstruct  = s.ds_type[ iterator[0] ]

  if dstruct  == VECTOR:
    # get the base address
    base_addr = s.ds_table[ iterator[0] ]
    dt_ptr    = s.dt_table[ iterator[0] ]
    metadata  = s.mem.read( dt_ptr, 4 )
    dt_desc   = dt_desc_fields( metadata )

    # PRIMITIVE TYPES
    if dt_desc[2] == 0:
      # base + ( index * sizeof( T ) )
      mem_addr  = base_addr + ( iterator[1] * dt_desc[1] )
      # store to memory location
      s.mem.write( mem_addr, dt_desc[1], s.rf[rt(inst)] )
    # USER-DEFINED TYPES
    elif dt_desc[2] == 1:
      #   1. get metadata of the field
      #       dt_ptr = dt_ptr * index
      #       metadata_field = load from dt_ptr
      #   2. compute mem_addr
      #      mem_addr = base_addr + ( index * sizeof( T ) )
      #                   + offset_of_field
      #   3. store value
      #      mem_write( mem_addr, sizeof( field )
      field_dt_ptr   = dt_ptr + rs( inst ) * 4
      field_metadata = s.mem.read( field_dt_ptr, 4 )
      field_dt_desc  = dt_desc_fields( field_metadata )
      # base + ( index * sizeof( T ) ) + offset
      mem_addr = \
        base_addr + ( iterator[1] * dt_desc[1] ) + field_dt_desc[0]
      # store to memory location
      s.mem.write( mem_addr, field_dt_desc[1], s.rf[rt(inst)] )

  s.pc += 4

#=======================================================================
# Create Decoder
#=======================================================================

decode = create_risc_decoder( encodings, globals(), debug=True )

