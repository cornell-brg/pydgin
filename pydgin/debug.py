#=======================================================================
# Debug
#=======================================================================

from pydgin.jit import elidable

#-----------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------
# a class that contains different debug flags
class Debug( object ):
  _immutable_fields_ = [ 'enabled_flags?', 'start_after', ]

  # NOTE: it doesn't seem possible to have conditional debug prints
  # without incurring performance losses. So, instead we are
  # specializing the binary in translation time. This class variable
  # will be set true in translation time only if debugging is enabled.
  # Otherwise, the translator can optimize away the enabled call below

  global_enabled = False

  def __init__( self, flags = [], start_after = 0 ):
    self.start_after = start_after
    # enable this only if start_after is 0 (start from the beginning)
    self._enabled = ( start_after == 0 )
    self._enabled_flags = flags
    if self._enabled:
      self.enabled_flags = flags
    else:
      self.enabled_flags = []

  #---------------------------------------------------------------------
  # enabled
  #---------------------------------------------------------------------
  # Returns true if debugging is turned on in translation and the
  # particular flag is turned on in command line.
  def enabled( self, flag ):
    return self._enabled_impl( flag, self.enabled_flags )

  #---------------------------------------------------------------------
  # _enabled_impl
  #---------------------------------------------------------------------
  # we separate the impl from the enabled so that we can elide this with
  # the enabled_flags as an arg
  @elidable
  def _enabled_impl( self, flag, enabled_flags ):
    return Debug.global_enabled and ( flag in enabled_flags )

  #---------------------------------------------------------------------
  # check_start_after
  #---------------------------------------------------------------------
  # if start after specified, and if ncycles has reached this, we enable
  # debug by setting enabled_flags. Note that enabled_flags is a quasi-
  # immutable
  def check_start_after( self, ncycles ):
    # if globally disabled or already locally enabled, skip
    if not Debug.global_enabled or self._enabled:
      return
    elif ncycles >= self.start_after:
      # enable the debug
      print "Reached %s cycles, enabling debug" % ncycles
      self._enabled = True
      self.enabled_flags = self._enabled_flags

#-------------------------------------------------------------------------
# pad
#-------------------------------------------------------------------------
# add padding to string
def pad( str, nchars, pad_char=" ", pad_end=True ):
  pad_str = ( nchars - len( str ) ) * pad_char
  out_str = str + pad_str if pad_end else pad_str + str
  return out_str

#-------------------------------------------------------------------------
# pad_hex
#-------------------------------------------------------------------------
# easier-to-use padding function for hex values
def pad_hex( hex_val, len=8 ):
  return pad( "%x" % hex_val, len, "0", False )

