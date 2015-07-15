#=======================================================================
# isa.py
#=======================================================================

ENABLE_FP = True

from utils        import sext_32, signed, sext, trim
from pydgin.misc  import create_risc_decoder, FatalError, \
                         NotImplementedInstError
from pydgin.utils import (
  trim_32, specialize, intmask, bits2float, float2bits
)

from helpers import *

import isa_RV32I, isa_RV64I, isa_RV32M, isa_RV64M, isa_RV32A, isa_RV64A

# TODO: super hacky! fixme to only import encoding_* funcs!

from isa_RV32I import *
from isa_RV64I import *
from isa_RV32M import *
from isa_RV64M import *
from isa_RV32A import *
from isa_RV64A import *
if ENABLE_FP:
  import isa_RV32F, isa_RV64F, isa_RV32D, isa_RV64D
  from isa_RV32F import *
  from isa_RV64F import *
  from isa_RV32D import *
  from isa_RV64D import *

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

  'x0'   :  0,   'x1'   :  1,   'x2'   :  2,   'x3'   :  3,
  'x4'   :  4,   'x5'   :  5,   'x6'   :  6,   'x7'   :  7,
  'x8'   :  8,   'x9'   :  9,   'x10'  : 10,   'x11'  : 11,
  'x12'  : 12,   'x13'  : 13,   'x14'  : 14,   'x15'  : 15,
  'x16'  : 16,   'x17'  : 17,   'x18'  : 18,   'x19'  : 19,
  'x20'  : 20,   'x21'  : 21,   'x22'  : 22,   'x23'  : 23,
  'x24'  : 24,   'x25'  : 25,   'x26'  : 26,   'x27'  : 27,
  'x28'  : 28,   'x29'  : 29,   'x30'  : 30,   'x31'  : 31,

  # abi as of jan 2015:
  # https://blog.riscv.org/wp-content/uploads/2015/01/riscv-calling.pdf

  'zero' :  0,   'ra'   :  1,   'sp'   :  2,   'gp'   :  3,
  'tp'   :  4,   't0'   :  5,   't1'   :  6,   't2'   :  7,
  's0'   :  8,   's1'   :  9,   'a0'   : 10,   'a1'   : 11,
  'a2'   : 12,   'a3'   : 13,   'a4'   : 14,   'a5'   : 15,
  'a6'   : 16,   'a7'   : 17,   's2'   : 18,   's3'   : 19,
  's4'   : 20,   's5'   : 21,   's6'   : 22,   's7'   : 23,
  's8'   : 24,   's9'   : 25,   's10'  : 26,   's11'  : 27,
  't3'   : 28,   't4'   : 29,   't5'   : 30,   't6'   : 31,

  'fp'   : 8,

  # floating point

  'f0'   :  0,   'f1'   :  1,   'f2'   :  2,   'f3'   :  3,
  'f4'   :  4,   'f5'   :  5,   'f6'   :  6,   'f7'   :  7,
  'f8'   :  8,   'f9'   :  9,   'f10'  : 10,   'f11'  : 11,
  'f12'  : 12,   'f13'  : 13,   'f14'  : 14,   'f15'  : 15,
  'f16'  : 16,   'f17'  : 17,   'f18'  : 18,   'f19'  : 19,
  'f20'  : 20,   'f21'  : 21,   'f22'  : 22,   'f23'  : 23,
  'f24'  : 24,   'f25'  : 25,   'f26'  : 26,   'f27'  : 27,
  'f28'  : 28,   'f29'  : 29,   'f30'  : 30,   'f31'  : 31,

  # abi as of jan 2015:
  # https://blog.riscv.org/wp-content/uploads/2015/01/riscv-calling.pdf

  'ft0'  :  0,   'ft1'  :  1,   'ft2'  :  2,   'ft3'  :  3,
  'ft4'  :  4,   'ft5'  :  5,   'ft6'  :  6,   'ft7'  :  7,
  'fs0'  :  8,   'fs1'  :  9,   'fa0'  : 10,   'fa1'  : 11,
  'fa2'  : 12,   'fa3'  : 13,   'fa4'  : 14,   'fa5'  : 15,
  'fa6'  : 16,   'fa7'  : 17,   'fs2'  : 18,   'fs3'  : 19,
  'fs4'  : 20,   'fs5'  : 21,   'fs6'  : 22,   'fs7'  : 23,
  'fs8'  : 24,   'fs9'  : 25,   'fs10' : 26,   'fs11' : 27,
  'ft8'  : 28,   'ft9'  : 29,   'ft10' : 30,   'ft11' : 31,

}

#=======================================================================
# Instruction Encodings
#=======================================================================

other_encodings = [
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

  # HACK: mapping fsd and fld ops to nop for translatable subset
  ['nop',                'xxxxxxxxxxxxxxxxx011xxxxx0000111'],
  ['nop',                'xxxxxxxxxxxxxxxxx011xxxxx0100111'],
]

base_enc = ( isa_RV32I.encodings + isa_RV64I.encodings )
extn_enc = ( isa_RV32M.encodings + isa_RV64M.encodings
           + isa_RV32A.encodings + isa_RV64A.encodings )

if ENABLE_FP:
  fp_enc   = ( isa_RV32F.encodings + isa_RV64F.encodings
             + isa_RV32D.encodings + isa_RV64D.encodings )
else:
  fp_enc   = []

encodings = base_enc + extn_enc + fp_enc + other_encodings

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_nop( s, inst ):
  s.pc += 4

def execute_sret( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_sfence_vm( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_wfi( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_mrth( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_mrts( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_hrts( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_csrrw( s, inst ):
  result = s.rf[inst.rs1]
  # currently only support csr == 3, which accesses fcsr
  if inst.csr == 3:
    s.fcsr, s.rf[inst.rd] = s.rf[inst.rs1], s.fcsr
  # TODO: use the actual csr value of pass/fail
  elif result & 0x1:
    status = result >> 1
    if status: raise FatalError("Fail! %s" % (result >> 1 ) )
    else:      raise FatalError("Pass!")
  else:
    raise NotImplementedInstError()
  s.pc += 4

def execute_csrrs( s, inst ):
  # currently only support csr == 3, which accesses fcsr
  if inst.csr == 3:
    s.rf[inst.rd] = s.fcsr
  else:
    raise NotImplementedInstError()
  s.pc += 4

def execute_csrrc( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_csrrwi( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_csrrsi( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_csrrci( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom0( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom0_rs1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom0_rs1_rs2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom0_rd( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom0_rd_rs1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom0_rd_rs1_rs2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom1_rs1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom1_rs1_rs2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom1_rd( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom1_rd_rs1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom1_rd_rs1_rs2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom2_rs1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom2_rs1_rs2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom2_rd( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom2_rd_rs1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom2_rd_rs1_rs2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom3( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom3_rs1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom3_rs1_rs2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom3_rd( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom3_rd_rs1( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4

def execute_custom3_rd_rs1_rs2( s, inst ):
  raise NotImplementedInstError()
  s.pc += 4


#=======================================================================
# Create Decoder
#=======================================================================

decode = create_risc_decoder( encodings, globals(), debug=True )

