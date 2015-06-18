#=========================================================================
# instruction.py
#=========================================================================

from pydgin.utils import r_ulonglong
from utils import signed, sext_32, sext, trim_64

class Instruction( object ):
  def __init__( self, bits, str ):
    self.bits = bits
    self.str  = str

#  int64_t i_imm() { return int64_t(b) >> 20; }
#  int64_t s_imm() { return x(7, 5) + (xs(25, 7) << 5); }
#  int64_t sb_imm(){ return (x(8, 4) << 1) + (x(25,6) << 5) + (x(7,1) << 11) + (imm_sign() << 12); }
#  int64_t u_imm() { return int64_t(b) >> 12 << 12; }
#  int64_t uj_imm(){ return (x(21, 10) << 1) + (x(20, 1) << 11) + (x(12, 8) << 12) + (imm_sign() << 20)
#  uint64_t rd()  { return x(7, 5)
#  uint64_t rs1() { return x(15, 5)
#  uint64_t rs2() { return x(20, 5)
#  uint64_t rs3() { return x(27, 5)
#  uint64_t rm()  { return x(12, 3)
#  uint64_t csr() { return x(20, 12)

  def x( self, lo, len ):
    mask = r_ulonglong( 0xffffffffffffffff ) >> (64-len)
    return (self.bits >> lo) & mask

  def xs( self, lo, len ):
    return sext(self.bits >> lo, len)

  def imm_sign( self ):
    return self.xs( 31, 1 )

  @property
  def i_imm(self):
    return self.xs( 20, 12 )

  @property
  def s_imm(self):
    return self.x(7, 5) + (self.xs(25, 7) << 5)

  @property
  def sb_imm(self):
    return (self.x(8, 4) << 1) + \
           (self.x(25,6) << 5) + \
           (self.x(7,1) << 11) + \
           (self.imm_sign() << 12)

  @property
  def u_imm(self):
    return sext_32( self.bits ) >> 12 << 12

  @property
  def uj_imm(self):
    return (self.x(21, 10) << 1) + \
           (self.x(20, 1) << 11) + \
           (self.x(12, 8) << 12) + \
           (self.imm_sign() << 20)

  @property
  def rd(self):
    return self.x(7, 5)

  @property
  def rs1(self):
    return self.x(15, 5)

  @property
  def rs2(self):
    return self.x(20, 5)

  @property
  def rs3(self):
    return self.x(27, 5)

  @property
  def rm(self):
    return self.x(12, 3)

  @property
  def csr(self):
    return self.x(20, 12)
