#=======================================================================
# instruction.py
#=======================================================================


class Instruction( object ):

  def __init__( self, bits ):
    self.bits = bits

  def cond( self ):
    return (self.bits >> 28) & 0xF

  def rn( self ):
    return (self.bits >> 16) & 0xF

  def rd( self ):
    return (self.bits >> 12) & 0xF

  def rm( self ):
    return self.bits & 0xF

  def rs( self ):
    return (self.bits >> 8) & 0xF

  def shift( self ):
    return (self.bits >> 5) & 0b11

  def shift_amt( self ):
    return (self.bits >> 7) & 0x1F

  def rotate( self ):
    return (self.bits >> 8) & 0xF

  def imm_8( self ):
    return self.bits & 0xFF

  def imm_12( self ):
    return self.bits & 0xFFF

  def imm_24( self ):
    return self.bits & 0xFFFFFF

  def imm_H( self ):
    return (self.bits >> 8) & 0xF

  def imm_L( self ):
    return self.bits & 0xF

  def register_list( self ):
    return self.bits & 0xFFFF

  def cp_num( self ):
    return (self.bits >> 8) & 0xF

  def opcode( self ):
    return (self.bits >> 21) & 0xF

  def opcode_1( self ):
    return (self.bits >> 20) & 0x1F

  def opcode_2( self ):
    return (self.bits >> 5) & 0b111

  def I( self ):
    return (self.bits >> 25) & 0b1

  def P( self ):
    return (self.bits >> 24) & 0b1

  def U( self ):
    return (self.bits >> 23) & 0b1

  def B( self ):
    return (self.bits >> 22) & 0b1

  def W( self ):
    return (self.bits >> 21) & 0b1

  #def L( self ):
  #  return (self.bits >> 20) & 0b1

  def S( self ):
    return (self.bits >> 20) & 0b1

  def SH( self ):
    return (self.bits >> 5) & 0b11

