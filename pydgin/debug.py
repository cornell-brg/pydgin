#=======================================================================
# Debug
#=======================================================================

#-----------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------
# a class that contains different debug flags
class Debug( object ):
  _immutable_fields_ = [ 'enabled_flags', 'start_after', 'state' ]

  # NOTE: it doesn't seem possible to have conditional debug prints
  # without incurring performance losses. So, instead we are
  # specializing the binary in translation time. This class variable
  # will be set true in translation time only if debugging is enabled.
  # Otherwise, the translator can optimize away the enabled call below

  global_enabled = False

  def __init__( self, flags = [], start_after = 0 ):
    self.enabled_flags = flags
    self.start_after = start_after
    # we need the state to check the number of cycles
    self.state = None

  #---------------------------------------------------------------------
  # enabled
  #---------------------------------------------------------------------
  # Returns true if debugging is turned on in translation and the
  # particular flag is turned on in command line.
  def enabled( self, flag ):
    return Debug.global_enabled and ( flag in self.enabled_flags ) and \
        ( self.state is None or self.start_after <= self.state.stat_num_insts )

  #---------------------------------------------------------------------
  # set_state
  #---------------------------------------------------------------------
  # set the state so that we can get the stat_num_insts
  def set_state( self, state ):
    self.state = state

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

