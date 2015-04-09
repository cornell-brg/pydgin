#=======================================================================
# instruction.py
#=======================================================================

class Instruction( object ):
  _immutable_fields_ = ["bits", "str"]
  def __init__( self, bits, str ):
    self.bits = bits
    self.str  = str

  @property
  def rd( self ):
    return (self.bits >> 11) & 0x1F

  @property
  def rt( self ):
    return (self.bits >> 16) & 0x1F

  @property
  def rs( self ):
    return (self.bits >> 21) & 0x1F

  @property
  def fd( self ):
    return (self.bits >>  6) & 0x1F

  @property
  def ft( self ):
    return (self.bits >> 16) & 0x1F

  @property
  def fs( self ):
    return (self.bits >> 11) & 0x1F

  @property
  def imm( self ):
    return self.bits & 0xFFFF

  @property
  def jtarg( self ):
    return self.bits & 0x3FFFFFF

  @property
  def shamt( self ):
    return (self.bits >> 6) & 0x1F

