
try:

  import os
  from rpython.rtyper.lltypesystem    import rffi
  from rpython.rlib.rarithmetic       import r_ulonglong
  from rpython.translator.tool.cbuild import ExternalCompilationInfo
  from os.path                        import dirname, realpath, join

  CUR_DIR  = dirname( realpath( __file__ ) )
  INCL_DIR = join( CUR_DIR, 'softfloat-c' )
  LIB_DIR  = join( dirname(CUR_DIR), 'build' )

  print INCL_DIR
  print LIB_DIR

  eci = ExternalCompilationInfo(
    includes     = ['softfloat.h'],
    include_dirs = [ INCL_DIR ],
    library_dirs = [ LIB_DIR ],
    libraries    = ['softfloat'],
  )

  bool          = rffi.UINT
  int_fast8_t   = rffi.INT_FAST8_T
  uint_fast16_t = rffi.UINT_FAST16_T
  uint_fast32_t = rffi.UINT_FAST32_T
  uint_fast64_t = rffi.UINT_FAST64_T
  int_fast32_t  = rffi.INT_FAST32_T
  int_fast64_t  = rffi.INT_FAST64_T
  float32_t     = rffi.ULONG
  float64_t     = rffi.ULONGLONG

  _get_flags, set_flags = \
    rffi.CExternVariable( int_fast8_t, 'softfloat_exceptionFlags', eci )

  def get_flags():
    return r_ulonglong( _get_flags() )

  def rffi_fn( name, arg_types, return_type ):
    return rffi.llexternal( name, arg_types, return_type, compilation_info=eci )

  f32_add       = rffi_fn('f32_add',      [float32_t,float32_t], float32_t )
  f32_sub       = rffi_fn('f32_sub',      [float32_t,float32_t], float32_t )
  f32_mul       = rffi_fn('f32_mul',      [float32_t,float32_t], float32_t )
  f32_div       = rffi_fn('f32_div',      [float32_t,float32_t], float32_t )
  f32_rem       = rffi_fn('f32_rem',      [float32_t,float32_t], float32_t )
  f32_sqrt      = rffi_fn('f32_sqrt',     [float32_t], float32_t )
  f32_mulAdd    = rffi_fn('f32_mulAdd',   [float32_t,float32_t,float32_t], float32_t )
  f32_classify  = rffi_fn('f32_classify', [float32_t], uint_fast16_t )
  f32_eq        = rffi_fn('f32_eq',       [float32_t,float32_t], bool )
  f32_lt        = rffi_fn('f32_lt',       [float32_t,float32_t], bool )
  f32_le        = rffi_fn('f32_le',       [float32_t,float32_t], bool )
  f32_lt_quiet  = rffi_fn('f32_lt_quiet', [float32_t,float32_t], bool )
  f32_le_quiet  = rffi_fn('f32_le_quiet', [float32_t,float32_t], bool )

  f64_add       = rffi_fn('f64_add',      [float64_t,float64_t], float64_t )
  f64_sub       = rffi_fn('f64_sub',      [float64_t,float64_t], float64_t )
  f64_mul       = rffi_fn('f64_mul',      [float64_t,float64_t], float64_t )
  f64_div       = rffi_fn('f64_div',      [float64_t,float64_t], float64_t )
  f64_rem       = rffi_fn('f64_rem',      [float64_t,float64_t], float64_t )
  f64_sqrt      = rffi_fn('f64_sqrt',     [float64_t], float64_t )
  f64_mulAdd    = rffi_fn('f64_mulAdd',   [float64_t,float64_t,float64_t], float64_t )
  f64_classify  = rffi_fn('f64_classify', [float64_t], uint_fast16_t )
  f64_eq        = rffi_fn('f64_eq',       [float64_t,float64_t], bool )
  f64_lt        = rffi_fn('f64_lt',       [float64_t,float64_t], bool )
  f64_le        = rffi_fn('f64_le',       [float64_t,float64_t], bool )
  f64_lt_quiet  = rffi_fn('f64_lt_quiet', [float64_t,float64_t], bool )
  f64_le_quiet  = rffi_fn('f64_le_quiet', [float64_t,float64_t], bool )

  i32_to_f32  = rffi_fn('i32_to_f32', [int_fast32_t], float32_t )
  i64_to_f32  = rffi_fn('i64_to_f32', [int_fast64_t], float32_t )
  ui32_to_f32 = rffi_fn('ui32_to_f32', [uint_fast32_t], float32_t )
  ui64_to_f32 = rffi_fn('ui64_to_f32', [uint_fast64_t], float32_t )

  i32_to_f64  = rffi_fn('i32_to_f64',  [int_fast32_t], float64_t )
  i64_to_f64  = rffi_fn('i64_to_f64',  [int_fast64_t], float64_t )
  ui32_to_f64 = rffi_fn('ui32_to_f64', [uint_fast32_t], float64_t )
  ui64_to_f64 = rffi_fn('ui64_to_f64', [uint_fast64_t], float64_t )

  f64_to_f32  = rffi_fn('f64_to_f32',  [float64_t], float32_t )
  f32_to_f64  = rffi_fn('f32_to_f64',  [float32_t], float64_t )

  f32_to_ui32 = rffi_fn('f32_to_ui32', [float32_t,int_fast8_t,bool], uint_fast32_t )
  f32_to_ui64 = rffi_fn('f32_to_ui64', [float32_t,int_fast8_t,bool], uint_fast64_t )
  f32_to_i32  = rffi_fn('f32_to_i32',  [float32_t,int_fast8_t,bool], int_fast32_t )
  f32_to_i64  = rffi_fn('f32_to_i64',  [float32_t,int_fast8_t,bool], int_fast64_t )

  f64_to_ui32 = rffi_fn('f64_to_ui32', [float64_t,int_fast8_t,bool], uint_fast32_t )
  f64_to_ui64 = rffi_fn('f64_to_ui64', [float64_t,int_fast8_t,bool], uint_fast64_t )
  f64_to_i32  = rffi_fn('f64_to_i32',  [float64_t,int_fast8_t,bool], int_fast32_t )
  f64_to_i64  = rffi_fn('f64_to_i64',  [float64_t,int_fast8_t,bool], int_fast64_t )

except ImportError:

  from softfloat._abi import ffi
  lib = ffi.dlopen('../build/libsoftfloat.so')

  def get_flags():
    return lib.softfloat_exceptionFlags

  def set_flags( value ):
    lib.softfloat_exceptionFlags = value

  f32_add       = lib.f32_add
  f32_sub       = lib.f32_sub
  f32_mul       = lib.f32_mul
  f32_div       = lib.f32_div
  f32_rem       = lib.f32_rem
  f32_sqrt      = lib.f32_sqrt
  f32_mulAdd    = lib.f32_mulAdd
  f32_classify  = lib.f32_classify
  f32_eq        = lib.f32_eq
  f32_lt        = lib.f32_lt
  f32_le        = lib.f32_le
  f32_lt_quiet  = lib.f32_lt_quiet
  f32_le_quiet  = lib.f32_le_quiet

  f64_add       = lib.f64_add
  f64_sub       = lib.f64_sub
  f64_mul       = lib.f64_mul
  f64_div       = lib.f64_div
  f64_rem       = lib.f64_rem
  f64_sqrt      = lib.f64_sqrt
  f64_mulAdd    = lib.f64_mulAdd
  f64_classify  = lib.f64_classify
  f64_eq        = lib.f64_eq
  f64_lt        = lib.f64_lt
  f64_le        = lib.f64_le
  f64_lt_quiet  = lib.f64_lt_quiet
  f64_le_quiet  = lib.f64_le_quiet

  i32_to_f32  = lib.i32_to_f32
  i64_to_f32  = lib.i64_to_f32
  ui32_to_f32 = lib.ui32_to_f32
  ui64_to_f32 = lib.ui64_to_f32

  i32_to_f64  = lib.i32_to_f64
  i64_to_f64  = lib.i64_to_f64
  ui32_to_f64 = lib.ui32_to_f64
  ui64_to_f64 = lib.ui64_to_f64

  f64_to_f32  = lib.f64_to_f32
  f32_to_f64  = lib.f32_to_f64

  f32_to_ui32 = lib.f32_to_ui32
  f32_to_ui64 = lib.f32_to_ui64
  f32_to_i32  = lib.f32_to_i32
  f32_to_i64  = lib.f32_to_i64

  f64_to_ui32 = lib.f64_to_ui32
  f64_to_ui64 = lib.f64_to_ui64
  f64_to_i32  = lib.f64_to_i32
  f64_to_i64  = lib.f64_to_i64

