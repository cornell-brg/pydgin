#=========================================================================
# jit.py
#=========================================================================
# Thin wrapper for RPython jitting API. Mostly for turning jit-related
# calls into no-ops when not translated and when RPython not in path.

try:
  import rpython.rlib.jit as jit

  JitDriver      = jit.JitDriver
  unroll_safe    = jit.unroll_safe
  elidable       = jit.elidable
  elidable_promote       = jit.elidable_promote
  set_param      = jit.set_param
  set_user_param = jit.set_user_param
  hint           = jit.hint

except ImportError:
  # rpython not in path, use dummy functions

  class JitDriver( object ):
    def __init__( self, **kwargs ):
      pass
    def jit_merge_point( self, **kwargs ):
      pass
    def can_enter_jit( self, **kwargs ):
      pass

  def dummy_decorator( func ):
    return func

  unroll_safe = dummy_decorator
  elidable    = dummy_decorator
  elidable_promote    = dummy_decorator

  def set_param( driver, name, value ):
    pass

  def set_user_param( driver, text ):
    pass

  def hint( x, **kwargs ):
    return x
