#=======================================================================
# isa_RV32F.py
#=======================================================================
'RISC-V instructions for the single-precision floating point extension.'

from utils        import sext_xlen, sext_32, sext, signed, trim, fp_neg
from pydgin.utils import trim_32
from helpers      import *

from softfloat._abi import ffi
lib = ffi.dlopen('../build/libsoftfloat.so')

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [

  ['flw',                'xxxxxxxxxxxxxxxxx010xxxxx0000111'],
  ['fsw',                'xxxxxxxxxxxxxxxxx010xxxxx0100111'],
  ['fmadd_s',            'xxxxx00xxxxxxxxxxxxxxxxxx1000011'],
  ['fmsub_s',            'xxxxx00xxxxxxxxxxxxxxxxxx1000111'],
  ['fnmsub_s',           'xxxxx00xxxxxxxxxxxxxxxxxx1001011'],
  ['fnmadd_s',           'xxxxx00xxxxxxxxxxxxxxxxxx1001111'],
  ['fadd_s',             '0000000xxxxxxxxxxxxxxxxxx1010011'],
  ['fsub_s',             '0000100xxxxxxxxxxxxxxxxxx1010011'],
  ['fmul_s',             '0001000xxxxxxxxxxxxxxxxxx1010011'],
  ['fdiv_s',             '0001100xxxxxxxxxxxxxxxxxx1010011'],
  ['fsqrt_s',            '010110000000xxxxxxxxxxxxx1010011'],
  ['fsgnj_s',            '0010000xxxxxxxxxx000xxxxx1010011'],
  ['fsgnjn_s',           '0010000xxxxxxxxxx001xxxxx1010011'],
  ['fsgnjx_s',           '0010000xxxxxxxxxx010xxxxx1010011'],
  ['fmin_s',             '0010100xxxxxxxxxx000xxxxx1010011'],
  ['fmax_s',             '0010100xxxxxxxxxx001xxxxx1010011'],
  ['fcvt_w_s',           '110000000000xxxxxxxxxxxxx1010011'],
  ['fcvt_wu_s',          '110000000001xxxxxxxxxxxxx1010011'],
  ['fmv_x_s',            '111000000000xxxxx000xxxxx1010011'],
  ['feq_s',              '1010000xxxxxxxxxx010xxxxx1010011'],
  ['flt_s',              '1010000xxxxxxxxxx001xxxxx1010011'],
  ['fle_s',              '1010000xxxxxxxxxx000xxxxx1010011'],
  ['fclass_s',           '111000000000xxxxx001xxxxx1010011'],
  ['fcvt_s_w',           '110100000000xxxxxxxxxxxxx1010011'],
  ['fcvt_s_wu',          '110100000001xxxxxxxxxxxxx1010011'],
  ['fmv_s_x',            '111100000000xxxxx000xxxxx1010011'],
  ['fsflags',            '000000000001xxxxx001xxxxx1110011'],

]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_flw( s, inst ):
  addr          = s.rf[inst.rs1] + inst.i_imm
  s.fp[inst.rd] = s.mem.read( addr, 4 )
  s.pc += 4

def execute_fsw( s, inst ):
  addr = s.rf[inst.rs1] + inst.s_imm
  s.mem.write( addr, 4, s.fp[inst.rs2] )
  s.pc += 4

def execute_fmadd_s( s, inst ):
  a, b, c = s.fp[inst.rs1], s.fp[inst.rs2], s.fp[inst.rs3]
  s.fp[ inst.rd ] = lib.f32_mulAdd( a, b, c )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fmsub_s( s, inst ):
  a, b, c = s.fp[inst.rs1], s.fp[inst.rs2], s.fp[inst.rs3]
  s.fp[ inst.rd ] = lib.f32_mulAdd( a, b, fp_neg(c,32) )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fnmsub_s( s, inst ):
  a, b, c = s.fp[inst.rs1], s.fp[inst.rs2], s.fp[inst.rs3]
  s.fp[ inst.rd ] = lib.f32_mulAdd( fp_neg(a,32), b, c )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fnmadd_s( s, inst ):
  a, b, c = s.fp[inst.rs1], s.fp[inst.rs2], s.fp[inst.rs3]
  s.fp[ inst.rd ] = lib.f32_mulAdd( fp_neg(a,32), b, fp_neg(c,32) )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fadd_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.fp[ inst.rd ] = sext_32( lib.f32_add( a, b ) )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
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
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.fp[ inst.rd ] = sext_32( lib.f32_div( a, b ) )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fsqrt_s( s, inst ):
  a = trim_32( s.fp[inst.rs1] )
  s.fp[ inst.rd ] = sext_32( lib.f32_sqrt( a ) )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fsgnj_s( s, inst ):
  sign_mask = 1 << 31
  body_mask = sign_mask - 1
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.fp[inst.rd] = (b & sign_mask) | (a & body_mask)
  s.pc += 4

def execute_fsgnjn_s( s, inst ):
  sign_mask = 1 << 31
  body_mask = sign_mask - 1
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.fp[inst.rd] = (~b & sign_mask) | (a & body_mask)
  s.pc += 4

def execute_fsgnjx_s( s, inst ):
  sign_mask = 1 << 31
  body_mask = sign_mask - 1
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.fp[inst.rd] = (b & sign_mask) ^ a
  s.pc += 4

def execute_fmin_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  # TODO: s.fp[ inst.rd ] = lib.isNaNF32UI(b) || ...
  s.fp[ inst.rd ] = a if lib.f32_lt_quiet(a,b) else b
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fmax_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  # TODO: s.fp[ inst.rd ] = lib.isNaNF32UI(b) || ...
  s.fp[ inst.rd ] = a if lib.f32_le_quiet(b,a) else b
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fcvt_w_s( s, inst ):
  s.rf[inst.rd] = sext_32(lib.f32_to_i32( s.fp[inst.rs1], inst.rm, True ))
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fcvt_wu_s( s, inst ):
  s.rf[inst.rd] = sext_32(lib.f32_to_ui32( s.fp[inst.rs1], inst.rm, True ))
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fmv_x_s( s, inst ):
  s.rf[inst.rd] = sext_32( s.fp[inst.rs1] )
  s.pc += 4

def execute_feq_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.rf[ inst.rd ] = lib.f32_eq( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_flt_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.rf[ inst.rd ] = lib.f32_lt( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fle_s( s, inst ):
  a, b = trim_32( s.fp[inst.rs1] ), trim_32( s.fp[inst.rs2] )
  s.rf[ inst.rd ] = lib.f32_le( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fclass_s( s, inst ):
  s.rf[inst.rd] = lib.f32_classify( trim_32( s.fp[inst.rs1] ) )
  s.pc += 4

def execute_fcvt_s_w( s, inst ):
  a = signed( s.rf[inst.rs1], 32 )
  s.fp[inst.rd] = lib.i32_to_f32( a )
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fcvt_s_wu( s, inst ):
  a = trim_32(s.rf[inst.rs1])
  s.fp[inst.rd] = lib.ui32_to_f32( a )
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fmv_s_x( s, inst ):
  s.fp[inst.rd] = s.rf[inst.rs1]
  s.pc += 4

def execute_fsflags( s, inst ):
  old = s.fcsr & 0x1F
  new = s.rf[inst.rs1] & 0x1F
  s.fcsr = ((s.fcsr >> 5) << 5) | new
  s.rf[inst.rd] = old
  s.pc += 4


