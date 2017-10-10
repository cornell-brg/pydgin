#=======================================================================
# isa.py
#=======================================================================

from        utils import trim_5
from pydgin.utils import signed, sext_16, sext_8, trim_32, \
                         bits2float, float2bits

from pydgin.misc import create_risc_decoder, FatalError

from machine import ChildListStackEntry

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
# 'mngr2proc' :  1,   # mfc0
# 'proc2mngr' :  2,   # mtc0
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

# Here's what I think our coprocessor registers are being used for:
# cp0 regs

# r1: assembly test
# r2
# r3
# r4
# r5
# r6
# r7
# r8
# r9
# r10: core id
# r11
# r12
# r13
# r14
# r15: core type
# r16: num cores
# r17: thread id (used to be called core id)
# r18
# r19
# r20
# r21: stats en

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [
  ['nop',      '000000_00000_00000_00000_00000_000000'],
  #---------------------------------------------------------------------
  # Coprocessor
  #---------------------------------------------------------------------
  ['mfc0',     '010000_00000_xxxxx_xxxxx_00000_000000'],
  ['mtc0',     '010000_00100_xxxxx_xxxxx_00000_000000'],
  #['mtc2',    '010010_00100_xxxxx_xxxxx_00000_000000'],
  #---------------------------------------------------------------------
  # Arithmetic
  #---------------------------------------------------------------------
  ['addu',     '000000_xxxxx_xxxxx_xxxxx_00000_100001'],
  ['subu',     '000000_xxxxx_xxxxx_xxxxx_00000_100011'],
  ['and',      '000000_xxxxx_xxxxx_xxxxx_00000_100100'],
  ['or',       '000000_xxxxx_xxxxx_xxxxx_00000_100101'],
  ['xor',      '000000_xxxxx_xxxxx_xxxxx_00000_100110'],
  ['nor',      '000000_xxxxx_xxxxx_xxxxx_00000_100111'],
  ['slt',      '000000_xxxxx_xxxxx_xxxxx_00000_101010'],
  ['sltu',     '000000_xxxxx_xxxxx_xxxxx_00000_101011'],
  #---------------------------------------------------------------------
  # Arithmetic Immediate
  #---------------------------------------------------------------------
  ['addiu',    '001001_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['andi',     '001100_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['ori',      '001101_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['xori',     '001110_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['slti',     '001010_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['sltiu',    '001011_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['lui',      '001111_00000_xxxxx_xxxxx_xxxxx_xxxxxx'],
  #---------------------------------------------------------------------
  # Shift
  #---------------------------------------------------------------------
  ['sll',      '000000_00000_xxxxx_xxxxx_xxxxx_000000'],
  ['srl',      '000000_00000_xxxxx_xxxxx_xxxxx_000010'],
  ['sra',      '000000_00000_xxxxx_xxxxx_xxxxx_000011'],
  ['sllv',     '000000_xxxxx_xxxxx_xxxxx_00000_000100'],
  ['srlv',     '000000_xxxxx_xxxxx_xxxxx_00000_000110'],
  ['srav',     '000000_xxxxx_xxxxx_xxxxx_00000_000111'],
  #---------------------------------------------------------------------
  # Mul/Div/Rem
  #---------------------------------------------------------------------
  ['mul',      '011100_xxxxx_xxxxx_xxxxx_00000_000010'],
  ['div',      '100111_xxxxx_xxxxx_xxxxx_00000_000101'],
  ['divu',     '100111_xxxxx_xxxxx_xxxxx_00000_000111'],
  ['rem',      '100111_xxxxx_xxxxx_xxxxx_00000_000110'],
  ['remu',     '100111_xxxxx_xxxxx_xxxxx_00000_001000'],
  #---------------------------------------------------------------------
  # Loads
  #---------------------------------------------------------------------
  ['lw',       '100011_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['lh',       '100001_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['lhu',      '100101_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['lb',       '100000_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['lbu',      '100100_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  #---------------------------------------------------------------------
  # Stores
  #---------------------------------------------------------------------
  ['sw',       '101011_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['sh',       '101001_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['sb',       '101000_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  #---------------------------------------------------------------------
  # Jumps
  #---------------------------------------------------------------------
  ['j',        '000010_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['jal',      '000011_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['jr',       '000000_xxxxx_00000_00000_00000_001000'],
  ['jalr',     '000000_xxxxx_00000_xxxxx_00000_001001'],
  #---------------------------------------------------------------------
  # Branches
  #---------------------------------------------------------------------
  ['beq',      '000100_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['bne',      '000101_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['blez',     '000110_xxxxx_00000_xxxxx_xxxxx_xxxxxx'],
  ['bgtz',     '000111_xxxxx_00000_xxxxx_xxxxx_xxxxxx'],
  ['bltz',     '000001_xxxxx_00000_xxxxx_xxxxx_xxxxxx'],
  ['bgez',     '000001_xxxxx_00001_xxxxx_xxxxx_xxxxxx'],
  #---------------------------------------------------------------------
  # Conditional
  #---------------------------------------------------------------------
  ['movn',     '000000_xxxxx_xxxxx_xxxxx_00000_001011'],
  ['movz',     '000000_xxxxx_xxxxx_xxxxx_00000_001010'],
  #---------------------------------------------------------------------
  # Syscall
  #---------------------------------------------------------------------
  ['syscall',  '000000_xxxxx_xxxxx_xxxxx_xxxxx_001100'],
  ['eret',     '000000_xxxxx_xxxxx_xxxxx_xxxxx_011000'],
  # NOTE: compiler seems to generate eret with the following encoding
  ['eret',     '010000_10000_00000_00000_00000_011000'],
  #---------------------------------------------------------------------
  # AMO
  #---------------------------------------------------------------------
  ['amo_add',  '100111_xxxxx_xxxxx_xxxxx_00000_000010'],
  ['amo_and',  '100111_xxxxx_xxxxx_xxxxx_00000_000011'],
  ['amo_or',   '100111_xxxxx_xxxxx_xxxxx_00000_000100'],
  ['amo_xchg', '100111_xxxxx_xxxxx_xxxxx_00000_001101'],
  ['amo_min',  '100111_xxxxx_xxxxx_xxxxx_00000_001110'],
  #---------------------------------------------------------------------
  # Data-Parallel
  #---------------------------------------------------------------------
  ['syncl',    '100111_00000_00000_00000_00000_000001'],
  ['xloop',    '110100_xxxxx_00000_xxxxx_xxxxx_xxxxxx'],
  ['stop',     '100111_00000_00000_00000_00000_000000'],
  ['utidx',    '100111_00000_00000_xxxxx_00000_001001'],
  ['mtuts',    '010010_00000_xxxxx_xxxxx_00000_001000'],
  ['mfuts',    '010010_xxxxx_xxxxx_xxxxx_00000_001001'],
  #---------------------------------------------------------------------
  # XLOOPS
  #---------------------------------------------------------------------
  ['xloop_uc', '110001_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['xloop_or', '110010_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['xloop_om', '111101_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['xloop_orm','111010_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['addiu_xi', '110110_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['addu_xi',  '100111_xxxxx_xxxxx_xxxxx_xxxxx_010000'],
  ['subu_xi',  '100111_xxxxx_xxxxx_xxxxx_xxxxx_010001'],
  #-----------------------------------------------------------------------
  # XPC
  #-----------------------------------------------------------------------
  ['pcall',    '111011_xxxxx_xxxxx_xxxxx_xxxxx_xxxxxx'],
  ['pcallr',   '111100_xxxxx_xxxxx_00000_00000_000001'],
  ['pcallzr',  '111100_xxxxx_xxxxx_00000_00000_000010'],
  ['pcallrx',  '111100_xxxxx_xxxxx_00000_00000_000011'],
  ['psync',    '111100_00000_00000_00000_00000_000000'],
  ['mtx',      '010010_xxxxx_xxxxx_00000_xxxxx_xxxxxx'],
  ['mfx',      '010010_xxxxx_xxxxx_00001_xxxxx_xxxxxx'],
  #---------------------------------------------------------------------
  # Misc
  #---------------------------------------------------------------------
  ['stat',     '100111_00000_xxxxx_00000_00000_001111'],
  ['hint_wl',  '100111_xxxxx_xxxxx_xxxxx_xxxxx_010010'],
  ['mug',      '010111_xxxxx_xxxxx_00000_00000_000000'],
  #---------------------------------------------------------------------
  # Floating Point
  #---------------------------------------------------------------------
  ['add_s',    '010001_xxxxx_xxxxx_xxxxx_xxxxx_000000'],
  ['sub_s',    '010001_xxxxx_xxxxx_xxxxx_xxxxx_000001'],
  ['mul_s',    '010001_xxxxx_xxxxx_xxxxx_xxxxx_000010'],
  ['div_s',    '010001_xxxxx_xxxxx_xxxxx_xxxxx_000011'],
  ['c_eq_s',   '010001_10000_xxxxx_xxxxx_xxxxx_110010'],
  ['c_lt_s',   '010001_10000_xxxxx_xxxxx_xxxxx_111100'],
  ['c_le_s',   '010001_10000_xxxxx_xxxxx_xxxxx_111110'],
# ['c_f_s',    '010001_10000_xxxxx_xxxxx_xxxxx_110000'],
# ['c_un_s',   '010001_10000_xxxxx_xxxxx_xxxxx_110001'],
# ['c_ngl_s',  '010001_10000_xxxxx_xxxxx_xxxxx_111011'],
# ['c_nge_s'   '010001_10000_xxxxx_xxxxx_xxxxx_111101'],
# ['c_ngt_s',  '010001_10000_xxxxx_xxxxx_xxxxx_111111'],
  ['cvt_w_s',  '010001_10000_00000_xxxxx_xxxxx_100100'],
  ['cvt_s_w',  '010001_10100_00000_xxxxx_xxxxx_100000'],
  ['trunc_w_s','010001_10000_00000_xxxxx_xxxxx_001101'],
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
  #if   inst.rd ==  1: pass
  #  s.rf[ inst.rt ] = src[ s.src_ptr ]
  #  s.src_ptr += 1
  # return actual core id (this is actually thread id)
  if   inst.rd == reg_map['c0_coreid']:
    # return actual core id (this is actually thread id)
    # but on Pydgin we don't have thread swapping so they are actually the
    # same thing
    s.rf[inst.rt] = s.core_id
  elif inst.rd == reg_map['c0_count']:
    s.rf[inst.rt] = s.num_insts
  elif inst.rd == reg_map['c0_fromsysc0']:
    # return actual core id
    s.rf[inst.rt] = s.core_id
  elif inst.rd == reg_map['c0_fromsysc5']:
    # return core type based on if it's in stats region or not
    s.rf[inst.rt] = s.stats_core_type if s.stats_en else s.core_type
  elif inst.rd == reg_map['c0_numcores']:
    # return actual numcores
    s.rf[inst.rt] = s.ncores
  elif inst.rd == reg_map['c0_counthi']:
    # print "WARNING: counthi always returns 0..."
    s.rf[inst.rt] = 0
  else:
    raise FatalError('Invalid mfc0 destination: %d!' % inst.rd )
  s.pc += 4

#-----------------------------------------------------------------------
# mtc0
#-----------------------------------------------------------------------
def execute_mtc0( s, inst ):
  if   inst.rd == reg_map['status']:
    if s.testbin:
      val = s.rf[inst.rt]
      if val == 0:
        print "  [ passed ] %s" % s.exe_name
      else:
        line_num = 0x7fffffff & val
        print "  [ FAILED ] %s (line %s)" % (s.exe_name, line_num)
      s.running = False
    else:
      print 'SETTING STATUS'
      s.status = s.rf[inst.rt]
  elif inst.rd == reg_map['statsen']:
    s.stats_en = s.rf[inst.rt]
  elif inst.rd == reg_map['c0_staten']:
    s.stats_en = s.rf[inst.rt]

  #elif inst.rd ==  2: pass
  #  if sink[ s.sink_ptr ] != s.rf[ inst.rt ]:
  #    print 'sink:', sink[ s.sink_ptr ], 's.rf:', s.rf[ inst.rt ]
  #    raise Exception('Instruction: mtc0 failed!')
  #  print 'SUCCESS: s.rf[' + str( inst.rt ) + '] == ' + str( sink[ s.sink_ptr ] )
  #  s.sink_ptr += 1

  else:
    raise FatalError('Invalid mtc0 destination: %d!' % inst.rd )
  s.pc += 4

#-----------------------------------------------------------------------
# Register-register arithmetic, logical, and comparison instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# addu
#-----------------------------------------------------------------------
def execute_addu( s, inst ):
  s.rf[ inst.rd ] = trim_32( s.rf[ inst.rs ] + s.rf[ inst.rt ] )
  s.pc += 4

#-----------------------------------------------------------------------
# subu
#-----------------------------------------------------------------------
def execute_subu( s, inst ):
  s.rf[inst.rd] = trim_32( s.rf[inst.rs] - s.rf[inst.rt] )
  s.pc += 4

#-----------------------------------------------------------------------
# and
#-----------------------------------------------------------------------
def execute_and( s, inst ):
  s.rf[inst.rd] = s.rf[inst.rs] & s.rf[inst.rt]
  s.pc += 4

#-----------------------------------------------------------------------
# or
#-----------------------------------------------------------------------
def execute_or( s, inst ):
  s.rf[inst.rd] = s.rf[inst.rs] | s.rf[inst.rt]
  s.pc += 4

#-----------------------------------------------------------------------
# xor
#-----------------------------------------------------------------------
def execute_xor( s, inst ):
  s.rf[inst.rd] = s.rf[inst.rs] ^ s.rf[inst.rt]
  s.pc += 4

#-----------------------------------------------------------------------
# nor
#-----------------------------------------------------------------------
def execute_nor( s, inst ):
  s.rf[inst.rd] = trim_32( ~(s.rf[inst.rs] | s.rf[inst.rt]) )
  s.pc += 4

#-----------------------------------------------------------------------
# slt
#-----------------------------------------------------------------------
def execute_slt( s, inst ):
  s.rf[inst.rd] = signed( s.rf[inst.rs] ) < signed( s.rf[inst.rt] )
  s.pc += 4

#-----------------------------------------------------------------------
# sltu
#-----------------------------------------------------------------------
def execute_sltu( s, inst ):
  s.rf[inst.rd] = s.rf[inst.rs] < s.rf[inst.rt]
  s.pc += 4

#-----------------------------------------------------------------------
# mul
#-----------------------------------------------------------------------
def execute_mul( s, inst ):
  s.rf[ inst.rd ] = trim_32( s.rf[ inst.rs ] * s.rf[ inst.rt ] )
  s.pc += 4

#-----------------------------------------------------------------------
# div
#-----------------------------------------------------------------------
# http://stackoverflow.com/a/6084608
def execute_div( s, inst ):
  x    = signed( s.rf[ inst.rs ] )
  y    = signed( s.rf[ inst.rt ] )
  sign = -1 if (x < 0)^(y < 0) else 1

  s.rf[ inst.rd ] = abs(x) / abs(y) * sign
  s.pc += 4

#-----------------------------------------------------------------------
# divu
#-----------------------------------------------------------------------
def execute_divu( s, inst ):
  s.rf[ inst.rd ] = s.rf[ inst.rs ] / s.rf[ inst.rt ]
  s.pc += 4

#-----------------------------------------------------------------------
# rem
#-----------------------------------------------------------------------
# http://stackoverflow.com/a/6084608
def execute_rem( s, inst ):
  x = signed( s.rf[ inst.rs ] )
  y = signed( s.rf[ inst.rt ] )

  s.rf[ inst.rd ] = abs(x) % abs(y) * (1 if x > 0 else -1)
  s.pc += 4

#-----------------------------------------------------------------------
# remu
#-----------------------------------------------------------------------
def execute_remu( s, inst ):
  s.rf[ inst.rd ] = s.rf[ inst.rs ] % s.rf[ inst.rt ]
  s.pc += 4

#-----------------------------------------------------------------------
# Register-inst.immediate arithmetic, logical, and comparison instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# addiu
#-----------------------------------------------------------------------
def execute_addiu( s, inst ):
  s.rf[ inst.rt ] = trim_32( s.rf[ inst.rs ] + sext_16( inst.imm ) )
  s.pc += 4

#-----------------------------------------------------------------------
# andi
#-----------------------------------------------------------------------
def execute_andi( s, inst ):
  s.rf[inst.rt] = s.rf[inst.rs] & inst.imm
  s.pc += 4

#-----------------------------------------------------------------------
# ori
#-----------------------------------------------------------------------
def execute_ori( s, inst ):
  s.rf[inst.rt] = s.rf[inst.rs] | inst.imm
  s.pc += 4

#-----------------------------------------------------------------------
# xori
#-----------------------------------------------------------------------
def execute_xori( s, inst ):
  s.rf[inst.rt] = s.rf[inst.rs] ^ inst.imm
  s.pc += 4

#-----------------------------------------------------------------------
# slti
#-----------------------------------------------------------------------
def execute_slti( s, inst ):
  s.rf[inst.rt] = signed( s.rf[inst.rs] ) < signed( sext_16(inst.imm) )
  s.pc += 4

#-----------------------------------------------------------------------
# sltiu
#-----------------------------------------------------------------------
def execute_sltiu( s, inst ):
  s.rf[inst.rt] = s.rf[inst.rs] < sext_16(inst.imm)
  s.pc += 4

#-----------------------------------------------------------------------
# Shift instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# sll
#-----------------------------------------------------------------------
def execute_sll( s, inst ):
  s.rf[inst.rd] = trim_32( s.rf[inst.rt] << inst.shamt )
  s.pc += 4

#-----------------------------------------------------------------------
# srl
#-----------------------------------------------------------------------
def execute_srl( s, inst ):
  s.rf[inst.rd] = s.rf[inst.rt] >> inst.shamt
  s.pc += 4

#-----------------------------------------------------------------------
# sra
#-----------------------------------------------------------------------
def execute_sra( s, inst ):
  s.rf[inst.rd] = trim_32( signed( s.rf[inst.rt] ) >> inst.shamt )
  s.pc += 4

#-----------------------------------------------------------------------
# sllv
#-----------------------------------------------------------------------
def execute_sllv( s, inst ):
  s.rf[inst.rd] = trim_32( s.rf[inst.rt] << trim_5( s.rf[inst.rs] ) )
  s.pc += 4

#-----------------------------------------------------------------------
# srlv
#-----------------------------------------------------------------------
def execute_srlv( s, inst ):
  s.rf[inst.rd] = s.rf[inst.rt] >> trim_5( s.rf[inst.rs] )
  s.pc += 4

#-----------------------------------------------------------------------
# srav
#-----------------------------------------------------------------------
def execute_srav( s, inst ):
  # TODO: should it really be masked like this?
  s.rf[inst.rd] = trim_32( signed( s.rf[inst.rt] ) >> trim_5( s.rf[inst.rs] ) )
  s.pc += 4

#-----------------------------------------------------------------------
# Unconditional jump instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# j
#-----------------------------------------------------------------------
def execute_j( s, inst ):
  s.pc = ((s.pc + 4) & 0xF0000000) | (inst.jtarg << 2)

#-----------------------------------------------------------------------
# jal
#-----------------------------------------------------------------------

def execute_jal( s, inst ):
  s.rf[31] = s.pc + 4
  s.pc = ((s.pc + 4) & 0xF0000000) | (inst.jtarg << 2)
  # shreesha: tasktrace
  # if the target address belongs to one of the runtime-related
  # functions (TaskGroup(), run(), wait(), run_and_wait()), then set the
  # runtime mode flag and record the return address if in task-mode and set
  # the task-mode to false.
  #
  # NOTE: 09/29/2017
  # Updates: If starting a new parallel section which is detected by the
  # first call to run_and_wait or wait, clear the task queue and reset the
  # task counter, current taskid
  if s.pc in s.runtime_dict.keys() and s.stat_inst_en[8]:
    if s.task_mode:
      s.task_mode = False
      s.task_ras.append( s.rf[31] )
    if ((not s.parallel_section) \
       and ( s.runtime_dict[s.pc] == "run_and_wait" or s.runtime_dict[s.pc] == "wait")):
      s.parallel_section = True
      s.parallel_section_ra = s.rf[31]
    s.runtime_mode = True

#-----------------------------------------------------------------------
# jr
#-----------------------------------------------------------------------
# If we are executing parallel calls, we need to treat jr as a branch
# back to the top of the function and increment the work index. Only when
# all the requested calls have been performed, we jump back to the return
# address as normal. We differentiate this case from a nested function
# call within a pcall by checking if $ra is set to a magic number. The
# work index is assumed to be initialized in $a0.  We cannot guarantee
# that the compiler will not overwrite $a0 inside the kernel, so we need
# to initialize $a0 with the updated work index before looping back to
# the start of the kernel.
#
# If all requested calls have been performed, we swap the active regfile
# pointer to the scalar regfile and disable the XPC bit.
def execute_jr( s, inst ):

  s.pc = s.rf[inst.rs]

  # shreesha: tasktrace
  # Returning to runtime-mode
  if s.pc in s.runtime_ras:
    s.runtime_mode = True
    s.task_mode = False
    s.runtime_ras.pop()

  # shreesha: tasktrace
  # Returning to task-mode
  if s.pc in s.task_ras:
    s.task_mode = True
    s.task_ras.pop()
    s.runtime_mode = False

  # shreesha: tasktrace
  # End of a parallel section
  if s.pc == s.parallel_section_ra:
    s.parallel_section = False
    s.parallel_section_ra = 0
    s.curr_taskid = 0
    s.task_counter = 0
    s.task_queue = []

#-----------------------------------------------------------------------
# jalr
#-----------------------------------------------------------------------
def execute_jalr( s, inst ):
  s.rf[inst.rd] = s.pc + 4
  s.pc   = s.rf[inst.rs]
  # shreesha: tasktrace
  # check if we are in runtime mode and that stat instruction code for
  # executing a task has been set, if this is true then we are executing in
  # task mode, record where we entered the task mode & reset runtime mode
  if s.runtime_mode and s.stat_inst_en[10] and s.stat_inst_en[8]:
    s.runtime_mode = False
    s.task_mode = True
    s.runtime_ras.append( s.rf[inst.rd] )
    if s.parallel_section_type:
      s.curr_taskid = s.curr_taskid + 1

#-----------------------------------------------------------------------
# lui
#-----------------------------------------------------------------------
def execute_lui( s, inst ):
  s.rf[ inst.rt ] = inst.imm << 16
  s.pc += 4

#-----------------------------------------------------------------------
# Conditional branch instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# beq
#-----------------------------------------------------------------------
def execute_beq( s, inst ):
  if s.rf[inst.rs] == s.rf[inst.rt]:
    s.pc  = s.pc + 4 + (signed(sext_16(inst.imm)) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# bne
#-----------------------------------------------------------------------
def execute_bne( s, inst ):
  if s.rf[inst.rs] != s.rf[inst.rt]:
    s.pc  = s.pc + 4 + (signed(sext_16(inst.imm)) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# blez
#-----------------------------------------------------------------------
def execute_blez( s, inst ):
  if signed( s.rf[inst.rs] ) <= 0:
    s.pc  = s.pc + 4 + (signed(sext_16(inst.imm)) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# bgtz
#-----------------------------------------------------------------------
def execute_bgtz( s, inst ):
  if signed( s.rf[inst.rs] ) > 0:
    s.pc  = s.pc + 4 + (signed(sext_16(inst.imm)) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# bltz
#-----------------------------------------------------------------------
def execute_bltz( s, inst ):
  if signed( s.rf[inst.rs] ) < 0:
    s.pc  = s.pc + 4 + (signed(sext_16(inst.imm)) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# bgez
#-----------------------------------------------------------------------
def execute_bgez( s, inst ):
  if signed( s.rf[inst.rs] ) >= 0:
    s.pc  = s.pc + 4 + (signed(sext_16(inst.imm)) << 2)
  else:
    s.pc += 4

#-----------------------------------------------------------------------
# Load instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# lw
#-----------------------------------------------------------------------
def execute_lw( s, inst ):
  addr = trim_32( s.rf[inst.rs] + sext_16(inst.imm) )
  s.rf[inst.rt] = s.mem.read( addr, 4 )
  s.pc += 4

#-----------------------------------------------------------------------
# lh
#-----------------------------------------------------------------------
def execute_lh( s, inst ):
  addr = trim_32( s.rf[inst.rs] + sext_16(inst.imm) )
  s.rf[inst.rt] = sext_16( s.mem.read( addr, 2 ) )
  s.pc += 4

#-----------------------------------------------------------------------
# lhu
#-----------------------------------------------------------------------
def execute_lhu( s, inst ):
  addr = trim_32( s.rf[inst.rs] + sext_16(inst.imm) )
  s.rf[inst.rt] = s.mem.read( addr, 2 )
  s.pc += 4

#-----------------------------------------------------------------------
# lb
#-----------------------------------------------------------------------
def execute_lb( s, inst ):
  addr = trim_32( s.rf[inst.rs] + sext_16(inst.imm) )
  s.rf[inst.rt] = sext_8( s.mem.read( addr, 1 ) )
  s.pc += 4

#-----------------------------------------------------------------------
# lbu
#-----------------------------------------------------------------------
def execute_lbu( s, inst ):
  addr = trim_32( s.rf[inst.rs] + sext_16(inst.imm) )
  s.rf[inst.rt] = s.mem.read( addr, 1 )
  s.pc += 4

#-----------------------------------------------------------------------
# Store instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# sw
#-----------------------------------------------------------------------
def execute_sw( s, inst ):
  addr = trim_32( s.rf[inst.rs] + sext_16(inst.imm) )
  s.mem.write( addr, 4, s.rf[inst.rt] )
  s.pc += 4

#-----------------------------------------------------------------------
# sh
#-----------------------------------------------------------------------
def execute_sh( s, inst ):
  addr = trim_32( s.rf[inst.rs] + sext_16(inst.imm) )
  s.mem.write( addr, 2, s.rf[inst.rt] )
  s.pc += 4

#-----------------------------------------------------------------------
# sb
#-----------------------------------------------------------------------
def execute_sb( s, inst ):
  addr = trim_32( s.rf[inst.rs] + sext_16(inst.imm) )
  s.mem.write( addr, 1, s.rf[inst.rt] )
  s.pc += 4

#-----------------------------------------------------------------------
# movn
#-----------------------------------------------------------------------
def execute_movn( s, inst ):
  if s.rf[inst.rt] != 0:
    s.rf[inst.rd] = s.rf[inst.rs]
  s.pc += 4

#-----------------------------------------------------------------------
# movz
#-----------------------------------------------------------------------
def execute_movz( s, inst ):
  if s.rf[inst.rt] == 0:
    s.rf[inst.rd] = s.rf[inst.rs]
  s.pc += 4

#-----------------------------------------------------------------------
# Syscall instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# syscall
#-----------------------------------------------------------------------
#from syscalls import syscall_funcs
from syscalls import do_syscall
def execute_syscall( s, inst ):
  #v0 = reg_map['v0']
  #syscall_number = s.rf[ v0 ]
  #if syscall_number in syscall_funcs:
  #  syscall_funcs[ syscall_number ]( s )
  #else:
  #  print "WARNING: syscall not implemented!", syscall_number
  do_syscall( s )
  s.pc += 4

#-----------------------------------------------------------------------
# eret
#-----------------------------------------------------------------------
# Note that eret is only meaningful if we're running in pkernel mode
def execute_eret( s, inst ):
  assert s.pkernel
  s.pc = s.epc + 4

#-----------------------------------------------------------------------
# Atomic Memory Operation instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# amo.add
#-----------------------------------------------------------------------
def execute_amo_add( s, inst ):
  temp = s.mem.read( s.rf[ inst.rs ], 4 )
  s.mem.write( s.rf[inst.rs], 4, trim_32(temp + s.rf[inst.rt]) )
  s.rf[ inst.rd ] = temp
  s.pc += 4

#-----------------------------------------------------------------------
# amo.and
#-----------------------------------------------------------------------
def execute_amo_and( s, inst ):
  temp = s.mem.read( s.rf[ inst.rs ], 4 )
  s.mem.write( s.rf[inst.rs], 4, temp & s.rf[inst.rt] )
  s.rf[ inst.rd ] = temp
  s.pc += 4

#-----------------------------------------------------------------------
# amo.or
#-----------------------------------------------------------------------
def execute_amo_or( s, inst ):
  temp = s.mem.read( s.rf[ inst.rs ], 4 )
  s.mem.write( s.rf[inst.rs], 4, temp | s.rf[inst.rt] )
  s.rf[ inst.rd ] = temp
  s.pc += 4

#-----------------------------------------------------------------------
# amo.xchg
#-----------------------------------------------------------------------
def execute_amo_xchg( s, inst ):
  temp = s.mem.read( s.rf[ inst.rs ], 4 )
  s.mem.write( s.rf[inst.rs], 4, s.rf[inst.rt] )
  s.rf[ inst.rd ] = temp
  s.pc += 4

#-----------------------------------------------------------------------
# amo.min
#-----------------------------------------------------------------------
def execute_amo_min( s, inst ):
  temp = s.mem.read( s.rf[ inst.rs ], 4 )
  s.mem.write( s.rf[inst.rs], 4, min( temp, s.rf[inst.rt] ) )
  s.rf[ inst.rd ] = temp
  s.pc += 4

#-----------------------------------------------------------------------
# Data-Parallel
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# sync.l
#-----------------------------------------------------------------------
def execute_syncl( s, inst ):
  # TODO: sync doesn't do anything in pydgin
  s.pc += 4

#-----------------------------------------------------------------------
# xloop
#-----------------------------------------------------------------------
# Not to be confused with XLOOPS instructions
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
  raise FatalError('mfuts is unsupported!')
  s.pc += 4

#-----------------------------------------------------------------------
# Floating-Point Instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# add_s
#-----------------------------------------------------------------------
def execute_add_s( s, inst ):
  a = bits2float( s.rf[ inst.fs ] )
  b = bits2float( s.rf[ inst.ft ] )
  s.rf[ inst.fd ] = float2bits( a + b )
  s.pc += 4

#-----------------------------------------------------------------------
# sub_s
#-----------------------------------------------------------------------
def execute_sub_s( s, inst ):
  a = bits2float( s.rf[ inst.fs ] )
  b = bits2float( s.rf[ inst.ft ] )
  s.rf[ inst.fd ] = float2bits( a - b )
  s.pc += 4

#-----------------------------------------------------------------------
# mul_s
#-----------------------------------------------------------------------
def execute_mul_s( s, inst ):
  a = bits2float( s.rf[ inst.fs ] )
  b = bits2float( s.rf[ inst.ft ] )
  s.rf[ inst.fd ] = float2bits( a * b )
  s.pc += 4

#-----------------------------------------------------------------------
# div_s
#-----------------------------------------------------------------------
def execute_div_s( s, inst ):
  a = bits2float( s.rf[ inst.fs ] )
  b = bits2float( s.rf[ inst.ft ] )
  s.rf[ inst.fd ] = float2bits( a / b )
  s.pc += 4

#-----------------------------------------------------------------------
# c_eq_s
#-----------------------------------------------------------------------
def execute_c_eq_s( s, inst ):
  a = bits2float( s.rf[ inst.fs ] )
  b = bits2float( s.rf[ inst.ft ] )
  s.rf[ inst.fd ] = 1 if a == b else 0
  s.pc += 4

#-----------------------------------------------------------------------
# c_lt_s
#-----------------------------------------------------------------------
def execute_c_lt_s( s, inst ):
  a = bits2float( s.rf[ inst.fs ] )
  b = bits2float( s.rf[ inst.ft ] )
  s.rf[ inst.fd ] = 1 if a < b else 0
  s.pc += 4

#-----------------------------------------------------------------------
# c_le_s
#-----------------------------------------------------------------------
def execute_c_le_s( s, inst ):
  a = bits2float( s.rf[ inst.fs ] )
  b = bits2float( s.rf[ inst.ft ] )
  s.rf[ inst.fd ] = 1 if a <= b else 0
  s.pc += 4

#-----------------------------------------------------------------------
# cvt_w_s
#-----------------------------------------------------------------------
def execute_cvt_w_s( s, inst ):
  x = bits2float( s.rf[ inst.fs ] )
  s.rf[ inst.fd ] = trim_32( int( x ) )
  s.pc += 4

#-----------------------------------------------------------------------
# cvt_s_w
#-----------------------------------------------------------------------
def execute_cvt_s_w( s, inst ):
  x = signed( s.rf[ inst.fs ] )
  s.rf[ inst.fd ] = float2bits( float( x ) )
  s.pc += 4

#-----------------------------------------------------------------------
# trunc_w_s
#-----------------------------------------------------------------------
def execute_trunc_w_s( s, inst ):
  # TODO: check for overflow
  x = bits2float( s.rf[ inst.fs ] )
  s.rf[ inst.fd ] = trim_32(int(x))  # round down
  s.pc += 4

#-----------------------------------------------------------------------
# XLOOPS instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# xloop_uc
#-----------------------------------------------------------------------
# implemented as bne
def execute_xloop_uc( s, inst ):
  execute_bne( s, inst )

#-----------------------------------------------------------------------
# xloop_or
#-----------------------------------------------------------------------
# implemented as bne
def execute_xloop_or( s, inst ):
  execute_bne( s, inst )

#-----------------------------------------------------------------------
# xloop_om
#-----------------------------------------------------------------------
# implemented as bne
def execute_xloop_om( s, inst ):
  execute_bne( s, inst )

#-----------------------------------------------------------------------
# xloop_orm
#-----------------------------------------------------------------------
# implemented as bne
def execute_xloop_orm( s, inst ):
  execute_bne( s, inst )

#-----------------------------------------------------------------------
# xloop_addiu_xi
#-----------------------------------------------------------------------
# implemented as addiu
def execute_addiu_xi( s, inst ):
  execute_addiu( s, inst )

#-----------------------------------------------------------------------
# xloop_addu_xi
#-----------------------------------------------------------------------
# implemented as addu
def execute_addu_xi( s, inst ):
  execute_addu( s, inst )

#-----------------------------------------------------------------------
# xloop_subu_xi
#-----------------------------------------------------------------------
# implemented as subu
def execute_subu_xi( s, inst ):
  execute_subu( s, inst )

#-------------------------------------------------------------------------
# XPC instructions
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
# pcall
#-------------------------------------------------------------------------
# Set a bit to signify that we are now executing parallel calls and
# initialize XPC registers for tracking the current work index and the
# total number of calls. Otherwise, the pcall looks like a normal
# function call except that a signed 16b offset from the current PC is
# used as the jump target instead of a 26b absolute PC (i.e., br
# semantics instead of jal semantics). Note that we must also initialize
# register $a0 to the work index. The work index is incremented by the
# hardware after each execution of the function (see: jr). We store a
# magic value (i.e., 1) to $ra so that we can differentiate when to
# return from the pcall function and when to return from a nested
# function after the XPC bit is set. A separate microarchitectural
# register is used to save the return address for returning from the
# pcall function.
#
# When executing a pcall, we switch the regfile pointer to use the
# accelerator regfile instead of the scalar regfile. This is swapped back
# when we return from the pcall.
def execute_pcall( s, inst ):
  s.xpc_pcall_type = 'pcall'
  s.xpc_en         = True
  s.xpc_start_idx  = s.rf[ inst.rs ]
  s.xpc_end_idx    = s.rf[ inst.rt ]
  s.xpc_idx        = s.xpc_start_idx
  assert ( s.xpc_end_idx - s.xpc_start_idx ) > 0

  s.rf     = s.xpc_rf
  s.rf[4]  = s.xpc_idx
  s.rf[31] = s.xpc_return_trigger

  s.xpc_return_addr = s.pc + 4
  s.pc              = s.pc + 4 + (signed(sext_16(inst.imm)) << 2)
  s.xpc_start_addr  = s.pc

  s.num_pcalls += 1

#-------------------------------------------------------------------------
# pcallr
#-------------------------------------------------------------------------
# This is the same as pcall with a different signature. It assumes that
# the start index and size are packed into rf[rs] with the upper 24 bits
# as start and the lower 8 bits as size. Then rf[rt] has the jump target.
#
# This version of pcall exists because we really wanted three registers:
# begin, end, jump target. We tried to put the jump target into a 16b
# immediate, but the target was too far away and the compiler
# complained. We got around that by adding an adhoc handler right next
# to the pcall, but we thought this was too hacky and decided to make
# pcallr instead.
#
# For the first attempt at pcallr, we tried packing the start and end
# indices into a single source operand. The upper 16 bits were start
# and the lower 16 bits were end. Unfortunately, there were some indices
# that went above 2^16, so we changed it to 24 bits start and 8 bits
# size.
def execute_pcallr( s, inst ):
  s.xpc_pcall_type = 'pcallr'
  s.xpc_en         = True
  s.xpc_start_idx  = s.rf[ inst.rs ] >> 8
  size             = s.rf[ inst.rs ] & 0x000000FF
  s.xpc_end_idx    = s.xpc_start_idx + size
  s.xpc_idx        = s.xpc_start_idx
  assert ( s.xpc_end_idx - s.xpc_start_idx ) > 0

  s.xpc_return_addr = s.pc + 4
  s.pc              = s.rf[ inst.rt ]
  s.xpc_start_addr  = s.pc

  s.rf     = s.xpc_rf
  s.rf[4]  = s.xpc_idx
  s.rf[31] = s.xpc_return_trigger

  s.num_pcalls += 1

#-------------------------------------------------------------------------
# pcallzr
#-------------------------------------------------------------------------
# This is another variant of pcall. It takes two registers: a size and a
# jump target. The start index is assumed to be 0. This variant is used
# in the single-tile XPC because we need one giant pcall for the entire
# loop.
def execute_pcallzr( s, inst ):
  s.xpc_pcall_type = 'pcallzr'
  s.xpc_en         = True
  s.xpc_start_idx  = 0
  s.xpc_end_idx    = s.rf[ inst.rs ]
  s.xpc_idx        = s.xpc_start_idx
  assert ( s.xpc_end_idx - s.xpc_start_idx ) > 0

  s.xpc_return_addr = s.pc + 4
  s.pc              = s.rf[ inst.rt ]
  s.xpc_start_addr  = s.pc

  s.rf     = s.xpc_rf
  s.rf[4]  = s.xpc_idx
  s.rf[31] = s.xpc_return_trigger

  s.num_pcalls += 1

#-------------------------------------------------------------------------
# pcallrx
#-------------------------------------------------------------------------
# This variant of pcall looks just like a jalr, except it puts a return
# trigger in r31 so that jr knows when the pcall is over.
def execute_pcallrx( s, inst ):
  s.xpc_pcall_type  = 'pcallrx'
  s.xpc_en          = True

  s.xpc_return_addr = s.pc + 4
  s.pc              = s.rf[ inst.rs ]

  s.xpc_saved_ra    = s.rf[31]
  # Switch to accel regfile if --accel-rf
  if s.accel_rf:
    s.rf = s.xpc_rf
  s.rf[31]          = s.xpc_return_trigger

  s.num_pcalls += 1

#-------------------------------------------------------------------------
# psync
#-------------------------------------------------------------------------
# Treat as a nop for serial semantics of pcall.
def execute_psync( s, inst ):
  s.pc += 4

#-------------------------------------------------------------------------
# mtx
#-------------------------------------------------------------------------
# Move a value from the scalar regfile to the accelerator regfile.
def execute_mtx( s, inst ):
  s.xpc_rf[inst.rs] = s.scalar_rf[inst.rt]
  s.pc += 4

#-------------------------------------------------------------------------
# mfx
#-------------------------------------------------------------------------
# Move a value from the accelerator regfile to the scalar regfile.
def execute_mfx( s, inst ):
  s.scalar_rf[inst.rt] = s.xpc_rf[inst.rs]
  s.pc += 4

#-----------------------------------------------------------------------
# Misc instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# stat
#-----------------------------------------------------------------------
def execute_stat( s, inst ):
  s.pc += 4
  stat_en = inst.stat_en
  stat_id = inst.stat_id
  # instead of accumulating all of the stats every cycle, we mark the
  # beginning cycle and add the difference to the accumulator when turned
  # off (or the program has ended)

  # turn on stats
  if stat_en and (not s.stat_inst_en[ stat_id ]):
    s.stat_inst_en[ stat_id ] = True
    s.stat_inst_begin[ stat_id ] = s.num_insts

  # turn off stats -- accumulate the difference
  elif (not stat_en) and s.stat_inst_en[ stat_id ]:
    s.stat_inst_en[ stat_id ] = False
    s.stat_inst_num_insts[ stat_id ] += s.num_insts - s.stat_inst_begin[ stat_id ]

  # shreesha: task-tracing
  # enq event
  if stat_en and stat_id == 13 and s.stat_inst_en[8] and (not s.parallel_section_type):
    s.task_counter = s.task_counter + 1
    s.task_queue.append(s.task_counter)
    if (not s.parallel_section_type):
      s.curr_child_list.append(s.task_counter)
      s.task_graph.append([s.parallel_section_counter,s.curr_taskid,s.task_counter])
  # deq event
  elif stat_en and stat_id == 12 and s.stat_inst_en[8] and (not s.parallel_section_type):
    s.curr_taskid = s.task_queue[-1]
    s.task_queue.pop()
    s.strand_type = 0
  # start of wait()
  elif stat_en and stat_id == 3 and s.stat_inst_en[8] and (not s.parallel_section_type):
    if (not s.parallel_section_type):
      item = ChildListStackEntry()
      item.parent = s.curr_taskid
      item.child_list = s.curr_child_list
      s.child_list_stack.append(item)
      s.curr_child_list = []
  # end of wait()
  elif (not stat_en) and stat_id == 3 and s.stat_inst_en[8] and (not s.parallel_section_type):
    s.task_counter = s.task_counter + 1
    s.curr_taskid = s.task_counter
    s.strand_type = 1
    if not s.parallel_section_type:
      item = s.child_list_stack[-1]
      for edge in item.child_list:
        s.task_graph.append([s.parallel_section_counter,edge,s.curr_taskid])
      s.child_list_stack.pop()
      for entry in s.child_list_stack:
        for i,edge in enumerate(entry.child_list):
          if edge == item.parent:
            entry.child_list[i] = s.curr_taskid
  # end of a parallel section
  elif stat_en and stat_id == 8:
    s.parallel_section_counter = s.parallel_section_counter + 1
    s.parallel_section_type = 0
  # start of a data-parallel loop
  elif stat_en and stat_id == 4:
    s.parallel_section_type = 1
    s.curr_taskid = 0

#-----------------------------------------------------------------------
# hint_wl
#-----------------------------------------------------------------------
def execute_hint_wl( s, inst ):
  s.pc += 4

#-----------------------------------------------------------------------
# mug
#-----------------------------------------------------------------------
def execute_mug( s, inst ):
  s.pc += 4

#=======================================================================
# Create Decoder
#=======================================================================

decode = create_risc_decoder( encodings, globals(), debug=True )

