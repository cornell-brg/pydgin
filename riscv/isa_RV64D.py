#=======================================================================
# isa_RV64D.py
#=======================================================================
'RISC-V instructions for the double-precision floating point extension.'

from utils        import sext_xlen, sext_32, sext, signed, trim
from pydgin.utils import trim_32
from helpers      import *

import softfloat as sfp

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [

  ['fcvt_l_d',           '110000100010xxxxxxxxxxxxx1010011'],
  ['fcvt_lu_d',          '110000100011xxxxxxxxxxxxx1010011'],
  ['fmv_x_d',            '111000100000xxxxx000xxxxx1010011'],
  ['fcvt_d_l',           '110100100010xxxxxxxxxxxxx1010011'],
  ['fcvt_d_lu',          '110100100011xxxxxxxxxxxxx1010011'],
  ['fmv_d_x',            '111100100000xxxxx000xxxxx1010011'],

]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_fcvt_l_d( s, inst ):
  s.rf[inst.rd] = sfp.f64_to_i64( s.fp[inst.rs1], inst.rm, True )
  s.fcsr        = sfp.get_flags()
  sfp.set_flags( 0 )
  s.pc += 4

def execute_fcvt_lu_d( s, inst ):
  s.rf[inst.rd] = sfp.f64_to_ui64( s.fp[inst.rs1], inst.rm, True )
  s.fcsr        = sfp.get_flags()
  sfp.set_flags( 0 )
  s.pc += 4

def execute_fmv_x_d( s, inst ):
  s.rf[inst.rd] = s.fp[inst.rs1]
  s.pc += 4

def execute_fcvt_d_l( s, inst ):
  a = signed( s.rf[inst.rs1], 64 )
  s.fp[inst.rd] = sfp.i64_to_f64( a )
  s.fcsr        = sfp.get_flags()
  sfp.set_flags( 0 )
  s.pc += 4

def execute_fcvt_d_lu( s, inst ):
  a = s.rf[inst.rs1]
  s.fp[inst.rd] = sfp.ui64_to_f64( a )
  s.fcsr        = sfp.get_flags()
  sfp.set_flags( 0 )
  s.pc += 4

def execute_fmv_d_x( s, inst ):
  s.fp[inst.rd] = s.rf[inst.rs1]
  s.pc += 4

