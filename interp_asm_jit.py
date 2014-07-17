#=======================================================================
# interp_asm_jit.py
#=======================================================================
# RPython implementation of Parc ISA interpreter, with JIT.

import sys
import os

from rpython.rlib.rarithmetic import string_to_int as stoi
from rpython.rlib.jit         import JitDriver

#=======================================================================
# Utility Functions
#=======================================================================

#-----------------------------------------------------------------------
# sext
#-----------------------------------------------------------------------
# Sign extend 16-bit immediate fields.
def sext( value ):
  if value & 0x8000:
    return 0xFFFF0000 | value
  return value

#-----------------------------------------------------------------------
# signed
#-----------------------------------------------------------------------
def signed( value ):
  if value & 0x80000000:
    twos_complement = ~value + 1
    return -trim( twos_complement )
  return value

#-----------------------------------------------------------------------
# trim
#-----------------------------------------------------------------------
# Trim arithmetic to 16-bit values.
def trim( value ):
  return value & 0xFFFFFFFF

#-----------------------------------------------------------------------
# trim_5
#-----------------------------------------------------------------------
# Trim arithmetic to 5-bit values.
def trim_5( value ):
  return value & 0b11111

#-----------------------------------------------------------------------
# register_inst
#-----------------------------------------------------------------------
# Utility decorator for building decode table.
def register_inst( func ):
  prefix, suffix = func.func_name.split('_')
  assert prefix == 'execute'
  decode_table[ suffix ] = func
  return func

#=======================================================================
# Regsiter Definitions
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

  'status'    :  1,
  'mngr2proc' :  1,
  'proc2mngr' :  2,
  'statsen'   : 10,
  'coreid'    : 17,
}

reset_vector = 0x00000400
data_section = 0x00002000

#=======================================================================
# Instruction Definitions
#=======================================================================

decode_table = {}

#-----------------------------------------------------------------------
# Coprocessor 0 Instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# mfc0
#-----------------------------------------------------------------------
@register_inst
def execute_mfc0( s, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 1 )
  rt, rd = reg_map[ f0 ], reg_map[ f1 ]
  if   rd ==  1:
    rf[ rt ] = src[ s.src_ptr ]
    s.src_ptr += 1
  elif rd == 17: pass
  else: raise Exception('Invalid mfc0 destination!')
  s.pc += 1

#-----------------------------------------------------------------------
# mtc0
#-----------------------------------------------------------------------
@register_inst
def execute_mtc0( s, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 1 )
  rt, rd = reg_map[ f0 ], reg_map[ f1 ]
  if   rd ==  1: pass
  elif rd ==  2:
    if sink[ s.sink_ptr ] != rf[ rt ]:
      print 'sink:', sink[ s.sink_ptr ], 'rf:', rf[ rt ]
      raise Exception('Instruction: mtc0 failed!')
    print 'SUCCESS: rf[' + str( rt ) + '] == ' + str( sink[ s.sink_ptr ] )
    s.sink_ptr += 1
  elif rd == 10: pass
  else: raise Exception('Invalid mtc0 destination!')
  s.pc += 1

#-----------------------------------------------------------------------
# Register-register arithmetic, logical, and comparison instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# addu
#-----------------------------------------------------------------------
@register_inst
def execute_addu( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[ rd ] = trim( rf[ rs ] + rf[ rt ] )
  s.pc += 1

#-----------------------------------------------------------------------
# print
#-----------------------------------------------------------------------
@register_inst
def execute_print( s, src, sink, rf, fields ):
  rt = reg_map[ fields ]
  result = fields + ' = ' + str( rf[rt] )
  print result
  s.pc += 1

#-----------------------------------------------------------------------
# subu
#-----------------------------------------------------------------------
@register_inst
def execute_subu( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = trim( rf[rs] - rf[rt] )
  s.pc += 1

#-----------------------------------------------------------------------
# and
#-----------------------------------------------------------------------
@register_inst
def execute_and( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rs] & rf[rt]
  s.pc += 1

#-----------------------------------------------------------------------
# or
#-----------------------------------------------------------------------
@register_inst
def execute_or( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rs] | rf[rt]
  s.pc += 1

#-----------------------------------------------------------------------
# xor
#-----------------------------------------------------------------------
@register_inst
def execute_xor( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rs] ^ rf[rt]
  s.pc += 1

#-----------------------------------------------------------------------
# nor
#-----------------------------------------------------------------------
@register_inst
def execute_nor( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = trim( ~(rf[rs] | rf[rt]) )
  s.pc += 1

#-----------------------------------------------------------------------
# slt
#-----------------------------------------------------------------------
@register_inst
def execute_slt( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = signed( rf[rs] ) < signed( rf[rt] )
  s.pc += 1

#-----------------------------------------------------------------------
# sltu
#-----------------------------------------------------------------------
@register_inst
def execute_sltu( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rs] < rf[rt]
  s.pc += 1

#-----------------------------------------------------------------------
# Register-immediate arithmetic, logical, and comparison instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# addiu
#-----------------------------------------------------------------------
@register_inst
def execute_addiu( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[ rt ] = trim( rf[ rs ] + sext( imm ) )
  s.pc += 1

#-----------------------------------------------------------------------
# andi
#-----------------------------------------------------------------------
@register_inst
def execute_andi( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = rf[rs] & imm
  s.pc += 1

#-----------------------------------------------------------------------
# ori
#-----------------------------------------------------------------------
@register_inst
def execute_ori( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = rf[rs] | imm
  s.pc += 1

#-----------------------------------------------------------------------
# xori
#-----------------------------------------------------------------------
@register_inst
def execute_xori( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = rf[rs] ^ imm
  s.pc += 1

#-----------------------------------------------------------------------
# slti
#-----------------------------------------------------------------------
@register_inst
def execute_slti( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = signed( rf[rs] ) < signed( sext(imm) )
  s.pc += 1

#-----------------------------------------------------------------------
# sltiu
#-----------------------------------------------------------------------
@register_inst
def execute_sltiu( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = rf[rs] < sext(imm)
  s.pc += 1

#-----------------------------------------------------------------------
# Shift instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# sll
#-----------------------------------------------------------------------
@register_inst
def execute_sll( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, shamt = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rd] = trim( rf[rt] << shamt )
  s.pc += 1

#-----------------------------------------------------------------------
# srl
#-----------------------------------------------------------------------
@register_inst
def execute_srl( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, shamt = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rd] = rf[rt] >> shamt
  s.pc += 1

#-----------------------------------------------------------------------
# sra
#-----------------------------------------------------------------------
@register_inst
def execute_sra( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, shamt = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rd] = trim( signed( rf[rt] ) >> shamt )
  s.pc += 1

#-----------------------------------------------------------------------
# sllv
#-----------------------------------------------------------------------
@register_inst
def execute_sllv( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, rs  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = trim( rf[rt] << trim_5( rf[rs] ) )
  s.pc += 1

#-----------------------------------------------------------------------
# srlv
#-----------------------------------------------------------------------
@register_inst
def execute_srlv( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, rs  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rt] >> trim_5( rf[rs] )
  s.pc += 1

#-----------------------------------------------------------------------
# srav
#-----------------------------------------------------------------------
@register_inst
def execute_srav( s, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, rs  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  # TODO: should it really be masked like this?
  rf[rd] = trim( signed( rf[rt] ) >> trim_5( rf[rs] ) )
  s.pc += 1

#-----------------------------------------------------------------------
# Unconditional jump instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# j
#-----------------------------------------------------------------------
@register_inst
def execute_j( s, src, sink, rf, fields ):
  if fields in s.symtable: jtarg = s.symtable[ fields ]
  else:                    jtarg = stoi( fields, base=0 )
  #s.pc = ((s.pc + 4) & 0xF0000000) | (jtarg << 2)
  # TODO: HACKY
  s.pc = ((s.pc + 1) & 0xF0000000) | jtarg

#-----------------------------------------------------------------------
# jal
#-----------------------------------------------------------------------
@register_inst
def execute_jal( s, src, sink, rf, fields ):
  if fields in s.symtable: jtarg = s.symtable[ fields ]
  else:                    jtarg = stoi( fields, base=0 )
  #rf[31] = s.pc + 4
  #s.pc = ((s.pc + 4) & 0xF0000000) | (jtarg << 2)
  # TODO: HACKY
  rf[31] = 4*(s.pc + 1) + reset_vector
  s.pc   = ( (s.pc + 1) & 0xF0000000) | jtarg

#-----------------------------------------------------------------------
# jr
#-----------------------------------------------------------------------
@register_inst
def execute_jr( s, src, sink, rf, fields ):
  rs   = reg_map[ fields ]
  s.pc = rf[rs]

#-----------------------------------------------------------------------
# jalr
#-----------------------------------------------------------------------
@register_inst
def execute_jalr( s, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 2 )
  rd, rs = reg_map[ f0 ], reg_map[ f1 ]
  #rf[rd] = s.pc + 4
  # TODO: HACKY
  rf[rd] = 4*(s.pc + 1) + reset_vector
  s.pc   = rf[rs]

#-----------------------------------------------------------------------
# lui
#-----------------------------------------------------------------------
@register_inst
def execute_lui( s, src, sink, rf, fields ):
  f0, f1  = fields.split( ' ', 2 )
  rt, imm = reg_map[ f0 ], stoi( f1, base=0 )
  rf[rt] = imm << 16
  s.pc += 1


#-----------------------------------------------------------------------
# Conditional branch instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# beq
#-----------------------------------------------------------------------
@register_inst
def execute_beq( s, src, sink, rf, fields ):
  f0, f1, f2  = fields.split( ' ', 3 )
  rt, rs      = reg_map[ f0 ], reg_map[ f1 ]
  if f2 in s.symtable: imm = s.symtable[ f2 ]
  else:                imm = stoi( f2, base=0 )

  # TODO: assuming label is absolute, not offset!
  if rf[rs] == rf[rt]:
    s.pc  = imm
    #s.pc  = (s.pc + 1 + sext(imm)) << 2
  else:
    s.pc += 1

#-----------------------------------------------------------------------
# bne
#-----------------------------------------------------------------------
@register_inst
def execute_bne( s, src, sink, rf, fields ):
  f0, f1, f2  = fields.split( ' ', 3 )
  rt, rs      = reg_map[ f0 ], reg_map[ f1 ]
  if f2 in s.symtable: imm = s.symtable[ f2 ]
  else:                imm = stoi( f2, base=0 )

  # TODO: assuming label is absolute, not offset!
  if rf[rs] != rf[rt]:
    s.pc  = imm
    #s.pc  = (s.pc + 1 + sext(imm)) << 2
  else:
    s.pc += 1

#-----------------------------------------------------------------------
# blez
#-----------------------------------------------------------------------
@register_inst
def execute_blez( s, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 2 )
  rs     = reg_map[ f0 ]
  if f1 in s.symtable: imm = s.symtable[ f1 ]
  else:                imm = stoi( f1, base=0 )

  # TODO: assuming label is absolute, not offset!
  if signed( rf[rs] ) <= 0:
    s.pc  = imm
    #s.pc  = (s.pc + 1 + sext(imm)) << 2
  else:
    s.pc += 1

#-----------------------------------------------------------------------
# bgtz
#-----------------------------------------------------------------------
@register_inst
def execute_bgtz( s, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 2 )
  rs     = reg_map[ f0 ]
  if f1 in s.symtable: imm = s.symtable[ f1 ]
  else:                imm = stoi( f1, base=0 )

  # TODO: assuming label is absolute, not offset!
  if signed( rf[rs] ) > 0:
    s.pc  = imm
    #s.pc  = (s.pc + 1 + sext(imm)) << 2
  else:
    s.pc += 1

#-----------------------------------------------------------------------
# bltz
#-----------------------------------------------------------------------
@register_inst
def execute_bltz( s, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 2 )
  rs     = reg_map[ f0 ]
  if f1 in s.symtable: imm = s.symtable[ f1 ]
  else:                imm = stoi( f1, base=0 )

  # TODO: assuming label is absolute, not offset!
  if signed( rf[rs] ) < 0:
    s.pc  = imm
    #s.pc  = (s.pc + 1 + sext(imm)) << 2
  else:
    s.pc += 1

#-----------------------------------------------------------------------
# bgez
#-----------------------------------------------------------------------
@register_inst
def execute_bgez( s, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 2 )
  rs     = reg_map[ f0 ]
  if f1 in s.symtable: imm = s.symtable[ f1 ]
  else:                imm = stoi( f1, base=0 )

  # TODO: assuming label is absolute, not offset!
  if signed( rf[rs] ) >= 0:
    s.pc  = imm
    #s.pc  = (s.pc + 1 + sext(imm)) << 2
  else:
    s.pc += 1

#-----------------------------------------------------------------------
# Load instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# lw
#-----------------------------------------------------------------------
@register_inst
def execute_lw( s, src, sink, rf, fields ):
  f0, f1,  f2 = fields.split( ' ', 3 )
  rt, imm, rs = reg_map[ f0 ], stoi( f1, base=0 ), reg_map[ f2 ]
  addr = rf[rs] + sext(imm) - data_section
  rf[rt] = s.mem.read( addr, 4 )
  s.pc += 1

#=======================================================================
# Main Loop
#=======================================================================

#-----------------------------------------------------------------------
# jit
#-----------------------------------------------------------------------

jitdriver = JitDriver( greens =['pc','insts',],
                       reds   =['state','symtable','src','sink',]
                     )

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-----------------------------------------------------------------------
# mainloop
#-----------------------------------------------------------------------
def mainloop( insts, memory, symtable, src, sink ):
  s = State( memory, symtable )

  # main interpreter loop

  while s.pc < len( insts ):

    # jit hint: jit_merge_point indicates start of opcode dispatch

    jitdriver.jit_merge_point(
        pc       = s.pc,
        state    = s,
        insts    = insts,
        symtable = symtable,
        src      = src,
        sink     = sink,
    )

    old = s.pc

    # skip nop instructions

    if insts[s.pc] == 'nop':
      inst = 'nop'
      s.pc += 1

    # instruction dispatch

    else:
      inst, fields = insts[s.pc].split( ' ', 1 )
      decode_table[inst]( s, src, sink, s.rf, fields )

    print old, ']]]', inst

    # jit hint: can_enter_jit indicates end of an application level loop

    if s.pc < old:
      jitdriver.can_enter_jit(
          pc       = s.pc,
          state    = s,
          insts    = insts,
          symtable = symtable,
          src      = src,
          sink     = sink,
      )

  # verify we successfully completed our program

  if s.sink_ptr != len( sink ):
    raise Exception('Failed to successfully receive all sink tokens!')

#-----------------------------------------------------------------------
# RegisterFile
#-----------------------------------------------------------------------
class RegisterFile( object ):
  def __init__( self ):
    self.regs = [0] * 32
  def __getitem__( self, idx ):
    return self.regs[idx]
  def __setitem__( self, idx, value ):
    self.regs[idx] = value

#-----------------------------------------------------------------------
# Memory
#-----------------------------------------------------------------------
class Memory( object ):
  def __init__( self ):
    self.data = [' ']*2**10

  def read( self, start_addr, num_bytes ):
    value = 0
    for i in range( num_bytes-1, -1, -1 ):
      value = value << 8
      value = value | ord( self.data[ start_addr + i ] )
    return value

  def write( self, start_addr, num_bytes, value ):
    for i in range( num_bytes ):
      self.data[ start_addr + i ] = chr(value & 0xFF)
      value = value >> 8

#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State( object ):
  def __init__( self, memory, symtable ):
    self.src_ptr  = 0
    self.sink_ptr = 0
    self.pc       = 0
    self.rf       = RegisterFile()
    self.mem      = memory
    self.symtable = symtable

#-----------------------------------------------------------------------
# parse
#-----------------------------------------------------------------------
COPY    = 0
COMMENT = 1
MTC0    = 2
MFC0    = 3
HI_LO   = 4
HI      = 5
LO      = 6
DATA    = 7
def parse( fp ):

  insts    = []
  src      = []
  sink     = []
  symtable = {}
  hi       = {}
  lo       = {}
  data     = []

  inst_str = ''
  src_str  = ''
  sink_str = ''

  temp_str = ''

  last     = None
  mode     = COPY

  for char in fp.read():

    if char == '\n':
      if inst_str:
        insts.append( inst_str.strip() )
        inst_str = ''
      if src_str:
        src.append( stoi( src_str, base=0 ) )
        src_str = ''
      if sink_str:
        sink.append( stoi( sink_str, base=0 ) )
        sink_str = ''
      if temp_str:
        data.append( temp_str )
        temp_str = ''
      last = None
      mode = COPY

    elif char == '#':
      mode = COMMENT

    elif mode == COPY and char == '<':
      mode = MFC0

    elif mode == COPY and char == '>':
      mode = MTC0

    elif mode == COPY and char == ':':
      symtable[ inst_str ] = len( insts )
      inst_str = ''
      mode = COMMENT

    elif mode == COPY and char == '%':
      temp_str = ''
      mode = HI_LO

    elif mode == COPY and char == '.':
      temp_str = ''
      mode = DATA

    elif mode == COPY and char == '(':
      if last != ' ':
        inst_str += ' '

    elif mode == COPY and char not in [',',')'] \
         and not (last == char == ' '):
      inst_str += char
      last = char

    elif mode == MFC0:
      src_str += char

    elif mode == MTC0:
      sink_str += char

    elif mode == DATA:
      temp_str += char
      if temp_str == 'data':
        mode, temp_str = COMMENT, ''

    elif mode == HI_LO:
      temp_str += char
      if   temp_str == 'hi':
        mode, temp_str = HI, ''
      elif temp_str == 'lo':
        mode, temp_str = LO, ''

    elif mode == HI and char not in ['[','(',' ']:
      if char in [']', ')']:
        hi[ temp_str ] = len( insts )
        temp_str = ''
      else:
        temp_str += char

    elif mode == LO and char not in ['[','(',' ']:
      if char in [']', ')']:
        lo[ temp_str ] = len( insts )
        temp_str = ''
      else:
        temp_str += char

  for label, pc in hi.items():
    insts[ pc ] += ' ' + hex( symtable[ label ] >> 16 )
  for label, pc in lo.items():
    insts[ pc ] += ' ' + hex( symtable[ label ] & 0xFFFF )

  addr      = 0
  num_bytes = 0
  mem  = Memory()
  for item in data:
    size, value = item.split(' ', 1)
    if   size == 'word': num_bytes = 4
    elif size == 'half': num_bytes = 2
    elif size == 'byte': num_bytes = 1
    mem.write( addr, num_bytes, stoi( value, base=0 ) )
    addr += num_bytes

  print '*'*70
  print 'Instructions'
  print '============'
  for inst in insts:
    print inst
  print
  print 'Source'
  print '======'
  print src
  print
  print 'Sink'
  print '===='
  print sink
  print
  print 'Symbol Table'
  print '============'
  for key, value in symtable.items():
    print key, value
  print '*'*70

  return insts, mem, symtable, src, sink

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run(fp):
  program, memory, symtable, src, sink  = parse( fp )
  mainloop( program, memory, symtable, src, sink )

#-----------------------------------------------------------------------
# entry_point
#-----------------------------------------------------------------------
def entry_point(argv):
  try:
    filename = argv[1]
  except IndexError:
    print "You must supply a filename"
    return 1

  run(open(filename, 'r'))
  return 0

#-----------------------------------------------------------------------
# target
#-----------------------------------------------------------------------
# Enables RPython translation of our interpreter.
def target( *args ):
  return entry_point, None

#-----------------------------------------------------------------------
# main
#-----------------------------------------------------------------------
# Enables CPython simulation of our interpreter.
if __name__ == "__main__":
  entry_point( sys.argv )
