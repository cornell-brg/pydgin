#=======================================================================
# interp_asm_jit.py
#=======================================================================
# RPython implementation of Parc ISA interpreter, with JIT.

import sys
import os

from   rpython.rlib.rarithmetic import string_to_int as stoi
from   rpython.rlib.rarithmetic import r_uint
from   rpython.rlib.jit import JitDriver

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
def execute_mfc0( p, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 1 )
  f1 = f1.strip() # TODO: clean this up
  rt, rd = reg_map[ f0 ], reg_map[ f1 ]
  if   rd ==  1:
    rf[ rt ] = src[ p.src_ptr ]
    p.src_ptr += 1
  elif rd == 17: pass
  else: raise Exception('Invalid mfc0 destination!')

#-----------------------------------------------------------------------
# mtc0
#-----------------------------------------------------------------------
@register_inst
def execute_mtc0( p, src, sink, rf, fields ):
  f0, f1 = fields.split( ' ', 1 )
  f1 = f1.strip() # TODO: clean this up
  rt, rd = reg_map[ f0 ], reg_map[ f1 ]
  if   rd ==  1: pass
  elif rd ==  2:
    if sink[ p.sink_ptr ] != rf[ rt ]:
      print 'sink:', sink[ p.sink_ptr ], 'rf:', rf[ rt ]
      raise Exception('Instruction: mtc0 failed!')
    print 'SUCCESS: rf[' + str( rt ) + '] == ' + str( sink[ p.sink_ptr ] )
    p.sink_ptr += 1
  elif rd == 10: pass
  else: raise Exception('Invalid mtc0 destination!')

#-----------------------------------------------------------------------
# Register-register arithmetic, logical, and comparison instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# addu
#-----------------------------------------------------------------------
@register_inst
def execute_addu( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[ rd ] = trim( rf[ rs ] + rf[ rt ] )

#-----------------------------------------------------------------------
# print
#-----------------------------------------------------------------------
@register_inst
def execute_print( p, src, sink, rf, fields ):
  rt = reg_map[ fields ]
  result = fields + ' = ' + str( rf[rt] )
  print result

#-----------------------------------------------------------------------
# subu
#-----------------------------------------------------------------------
@register_inst
def execute_subu( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = trim( rf[rs] - rf[rt] )

#-----------------------------------------------------------------------
# and
#-----------------------------------------------------------------------
@register_inst
def execute_and( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rs] & rf[rt]

#-----------------------------------------------------------------------
# or
#-----------------------------------------------------------------------
@register_inst
def execute_or( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rs] | rf[rt]

#-----------------------------------------------------------------------
# xor
#-----------------------------------------------------------------------
@register_inst
def execute_xor( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rs] ^ rf[rt]

#-----------------------------------------------------------------------
# nor
#-----------------------------------------------------------------------
@register_inst
def execute_nor( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = trim( ~(rf[rs] | rf[rt]) )

#-----------------------------------------------------------------------
# slt
#-----------------------------------------------------------------------
@register_inst
def execute_slt( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = signed( rf[rs] ) < signed( rf[rt] )

#-----------------------------------------------------------------------
# sltu
#-----------------------------------------------------------------------
@register_inst
def execute_sltu( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rs, rt  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rs] < rf[rt]

#-----------------------------------------------------------------------
# Register-immediate arithmetic, logical, and comparison instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# addiu
#-----------------------------------------------------------------------
@register_inst
def execute_addiu( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[ rt ] = trim( rf[ rs ] + sext( imm ) )

#-----------------------------------------------------------------------
# andi
#-----------------------------------------------------------------------
@register_inst
def execute_andi( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = rf[rs] & imm #zext

#-----------------------------------------------------------------------
# ori
#-----------------------------------------------------------------------
@register_inst
def execute_ori( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = rf[rs] | imm #zext

#-----------------------------------------------------------------------
# xori
#-----------------------------------------------------------------------
@register_inst
def execute_xori( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = rf[rs] ^ imm #zext

#-----------------------------------------------------------------------
# slti
#-----------------------------------------------------------------------
@register_inst
def execute_slti( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = signed( rf[rs] ) < signed( sext(imm) )

#-----------------------------------------------------------------------
# sltiu
#-----------------------------------------------------------------------
@register_inst
def execute_sltiu( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rt, rs, imm = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rt] = rf[rs] < sext(imm)

#-----------------------------------------------------------------------
# Shift instructions
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# sll
#-----------------------------------------------------------------------
@register_inst
def execute_sll( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, shamt = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rd] = trim( rf[rt] << shamt )

#-----------------------------------------------------------------------
# srl
#-----------------------------------------------------------------------
@register_inst
def execute_srl( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, shamt = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rd] = rf[rt] >> shamt

#-----------------------------------------------------------------------
# sra
#-----------------------------------------------------------------------
@register_inst
def execute_sra( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, shamt = reg_map[ f0 ], reg_map[ f1 ], stoi( f2, base=0 )
  rf[rd] = trim( signed( rf[rt] ) >> shamt )

#-----------------------------------------------------------------------
# sllv
#-----------------------------------------------------------------------
@register_inst
def execute_sllv( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, rs  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = trim( rf[rt] << trim_5( rf[rs] ) )

#-----------------------------------------------------------------------
# srlv
#-----------------------------------------------------------------------
@register_inst
def execute_srlv( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, rs  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  rf[rd] = rf[rt] >> trim_5( rf[rs] )

#-----------------------------------------------------------------------
# srav
#-----------------------------------------------------------------------
@register_inst
def execute_srav( p, src, sink, rf, fields ):
  f0, f1, f2 = fields.split( ' ', 3 )
  rd, rt, rs  = reg_map[ f0 ], reg_map[ f1 ], reg_map[ f2 ]
  # TODO: should it really be masked like this?
  rf[rd] = trim( signed( rf[rt] ) >> trim_5( rf[rs] ) )

#=======================================================================
# Main Loop
#=======================================================================

#-----------------------------------------------------------------------
# jit
#-----------------------------------------------------------------------

jitdriver = JitDriver( greens =['pc', 'insts',],
                       reds   =['ptrs','src','sink','rf',]
                     )

def jitpolicy(driver):
  from rpython.jit.codewriter.policy import JitPolicy
  return JitPolicy()

#-----------------------------------------------------------------------
# mainloop
#-----------------------------------------------------------------------
def mainloop( insts, src, sink ):
  pc = 0
  rf = RegisterFile()


  p = Ptrs()

  while pc < len( insts ):

    jitdriver.jit_merge_point(
        pc       = pc,
        insts    = insts,
        ptrs     = p,
        src      = src,
        sink     = sink,
        rf       = rf
    )

    if insts[pc] == 'nop':
      inst = 'nop'
    else:
      inst, fields = insts[pc].split( ' ', 1 )
      decode_table[inst]( p, src, sink, rf, fields )


    pc += 1

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
# Ptrs
#-----------------------------------------------------------------------
class Ptrs( object ):
  def __init__( self ):
    self.src_ptr  = 0
    self.sink_ptr = 0

#-----------------------------------------------------------------------
# parse
#-----------------------------------------------------------------------
COPY    = 0
COMMENT = 1
MTC0    = 2
MFC0    = 3
def parse( fp ):

  insts    = []
  src      = []
  sink     = []

  inst_str = ''
  src_str  = ''
  sink_str = ''

  last     = None
  mode     = COPY

  for char in fp.read():

    if char == '\n':
      if inst_str:
        insts.append( inst_str )
        inst_str = ''
      if src_str:
        src.append( stoi( src_str, base=0 ) )
        src_str = ''
      if sink_str:
        sink.append( stoi( sink_str, base=0 ) )
        sink_str = ''
      last = None
      mode = COPY

    elif char == '#':
      mode = COMMENT

    elif char == '<':
      mode = MFC0

    elif char == '>':
      mode = MTC0

    elif mode == COPY and char not in [',','(',')'] \
         and not (last == char == ' '):
      inst_str += char
      last = char

    elif mode == MFC0:
      src_str += char

    elif mode == MTC0:
      sink_str += char

  print insts
  print src
  print sink
  return insts, src, sink

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run(fp):
  program, src, sink  = parse( fp )
  mainloop( program, src, sink )

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
