#=======================================================================
# instruction.py
#=======================================================================

class Instruction( object ):
  def __init__( self, bits ):
    self.bits = bits

  def rd( self ):
    return (self.bits >> 11) & 0x1F

  def rt( self ):
    return (self.bits >> 16) & 0x1F

  def rs( self ):
    return (self.bits >> 21) & 0x1F

  def fd( self ):
    return (self.bits >>  6) & 0x1F

  def ft( self ):
    return (self.bits >> 16) & 0x1F

  def fs( self ):
    return (self.bits >> 11) & 0x1F

  def imm( self ):
    return self.bits & 0xFFFF

  def jtarg( self ):
    return self.bits & 0x3FFFFFF

  def shamt( self ):
    return (self.bits >> 6) & 0x1F

