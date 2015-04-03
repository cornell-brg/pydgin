#=======================================================================
# instruction.py
#=======================================================================


class Instruction( object ):

  def __init__( self, bits, str ):
    self.bits = bits
    self.str  = str

  @property
  def cond( self ):
    return (self.bits >> 28) & 0xF

  @property
  def rn( self ):
    return (self.bits >> 16) & 0xF

  @property
  def rd( self ):
    return (self.bits >> 12) & 0xF

  @property
  def rm( self ):
    return self.bits & 0xF

  @property
  def rs( self ):
    return (self.bits >> 8) & 0xF

  @property
  def shift( self ):
    return (self.bits >> 5) & 0b11

  @property
  def shift_amt( self ):
    return (self.bits >> 7) & 0x1F

  @property
  def rotate( self ):
    return (self.bits >> 8) & 0xF

  @property
  def imm_8( self ):
    return self.bits & 0xFF

  @property
  def imm_12( self ):
    return self.bits & 0xFFF

  @property
  def imm_24( self ):
    return self.bits & 0xFFFFFF

  @property
  def imm_H( self ):
    return (self.bits >> 8) & 0xF

  @property
  def imm_L( self ):
    return self.bits & 0xF

  @property
  def register_list( self ):
    return self.bits & 0xFFFF

  @property
  def cp_num( self ):
    return (self.bits >> 8) & 0xF

  @property
  def opcode( self ):
    return (self.bits >> 21) & 0xF

  @property
  def opcode_1( self ):
    return (self.bits >> 20) & 0x1F

  @property
  def opcode_2( self ):
    return (self.bits >> 5) & 0b111

  @property
  def I( self ):
    return (self.bits >> 25) & 0b1

  @property
  def P( self ):
    return (self.bits >> 24) & 0b1

  @property
  def U( self ):
    return (self.bits >> 23) & 0b1

  @property
  def B( self ):
    return (self.bits >> 22) & 0b1

  @property
  def W( self ):
    return (self.bits >> 21) & 0b1

  #def L( self ):
  #  return (self.bits >> 20) & 0b1

  @property
  def S( self ):
    return (self.bits >> 20) & 0b1

  @property
  def SH( self ):
    return (self.bits >> 5) & 0b11

  @property
  def R( self ):
    return (self.bits >> 22) & 0b1
