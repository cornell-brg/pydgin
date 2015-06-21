#=======================================================================
# isa_RV32D.py
#=======================================================================
'RISC-V instructions for the double-precision floating point extension.'

from utils        import sext_xlen, sext_32, sext, signed, trim
from pydgin.utils import trim_32
from helpers      import *

from isa_RV32F    import ffi, lib

#=======================================================================
# Instruction Encodings
#=======================================================================

encodings = [

  ['fld',                'xxxxxxxxxxxxxxxxx011xxxxx0000111'],
  ['fsd',                'xxxxxxxxxxxxxxxxx011xxxxx0100111'],
  ['fmadd_d',            'xxxxx01xxxxxxxxxxxxxxxxxx1000011'],
  ['fmsub_d',            'xxxxx01xxxxxxxxxxxxxxxxxx1000111'],
  ['fnmsub_d',           'xxxxx01xxxxxxxxxxxxxxxxxx1001011'],
  ['fnmadd_d',           'xxxxx01xxxxxxxxxxxxxxxxxx1001111'],
  ['fadd_d',             '0000001xxxxxxxxxxxxxxxxxx1010011'],
  ['fsub_d',             '0000101xxxxxxxxxxxxxxxxxx1010011'],
  ['fmul_d',             '0001001xxxxxxxxxxxxxxxxxx1010011'],
  ['fdiv_d',             '0001101xxxxxxxxxxxxxxxxxx1010011'],
  ['fsqrt_d',            '010110100000xxxxxxxxxxxxx1010011'],
  ['fsgnj_d',            '0010001xxxxxxxxxx000xxxxx1010011'],
  ['fsgnjn_d',           '0010001xxxxxxxxxx001xxxxx1010011'],
  ['fsgnjx_d',           '0010001xxxxxxxxxx010xxxxx1010011'],
  ['fmin_d',             '0010101xxxxxxxxxx000xxxxx1010011'],
  ['fmax_d',             '0010101xxxxxxxxxx001xxxxx1010011'],
  ['fcvt_s_d',           '010000000001xxxxxxxxxxxxx1010011'],
  ['fcvt_d_s',           '010000100000xxxxxxxxxxxxx1010011'],
  ['feq_d',              '1010001xxxxxxxxxx010xxxxx1010011'],
  ['flt_d',              '1010001xxxxxxxxxx001xxxxx1010011'],
  ['fle_d',              '1010001xxxxxxxxxx000xxxxx1010011'],
  ['fclass_d',           '111000100000xxxxx001xxxxx1010011'],
  ['fcvt_w_d',           '110000100000xxxxxxxxxxxxx1010011'],
  ['fcvt_wu_d',          '110000100001xxxxxxxxxxxxx1010011'],
  ['fcvt_d_w',           '110100100000xxxxxxxxxxxxx1010011'],
  ['fcvt_d_wu',          '110100100001xxxxxxxxxxxxx1010011'],

]

#=======================================================================
# Instruction Definitions
#=======================================================================

def execute_fld( s, inst ):
  # TODO: make memory support 64-bit ops
  addr          = s.rf[inst.rs1] + inst.i_imm
  s.fp[inst.rd] = ( s.mem.read( addr+4, 4 ) << 32 ) \
                  | s.mem.read( addr, 4 )
  s.pc += 4

def execute_fsd( s, inst ):
  # XXX: ignoring fsd for the time being
  #raise NotImplementedError()
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

def execute_fadd_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.fp[ inst.rd ] = lib.f64_add( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
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

def execute_fsqrt_d( s, inst ):
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
  s.fp[inst.rd] = lib.f64_to_f32( s.fp[inst.rs1] )
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fcvt_d_s( s, inst ):
  s.fp[inst.rd] = lib.f32_to_f64( trim_32(s.fp[inst.rs1]) )
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_feq_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.rf[ inst.rd ] = lib.f64_eq( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_flt_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.rf[ inst.rd ] = lib.f64_lt( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fle_d( s, inst ):
  a, b = s.fp[inst.rs1], s.fp[inst.rs2]
  s.rf[ inst.rd ] = lib.f64_le( a, b )
  s.fcsr          = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fclass_d( s, inst ):
  s.rf[inst.rd] = lib.f64_classify( s.fp[inst.rs1] )
  s.pc += 4

def execute_fcvt_w_d( s, inst ):
  s.rf[inst.rd] = sext_32(lib.f64_to_i32( s.fp[inst.rs1], inst.rm, True ))
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fcvt_wu_d( s, inst ):
  s.rf[inst.rd] = sext_32(lib.f64_to_ui32( s.fp[inst.rs1], inst.rm, True ))
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fcvt_d_w( s, inst ):
  a = signed( s.rf[inst.rs1], 32 )
  s.fp[inst.rd] = lib.i32_to_f64( a )
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

def execute_fcvt_d_wu( s, inst ):
  a = trim_32(s.rf[inst.rs1])
  s.fp[inst.rd] = lib.ui32_to_f64( a )
  s.fcsr        = lib.softfloat_exceptionFlags
  lib.softfloat_exceptionFlags = 0
  s.pc += 4

