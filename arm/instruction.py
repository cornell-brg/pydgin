#=======================================================================
# instruction.py
#=======================================================================

def cond( inst ):
  return (inst >> 28) & 0xF

def rn( inst ):
  return (inst >> 16) & 0xF

def rd( inst ):
  return (inst >> 12) & 0xF

def rm( inst ):
  return inst & 0xF

def rs( inst ):
  return (inst >> 8) & 0xF

def shift( inst ):
  return (inst >> 5) & 0b11

def shift_amt( inst ):
  return (inst >> 7) & 0x1F

def rotate( inst ):
  return (inst >> 8) & 0xF

def imm_8( inst ):
  return inst & 0xFF

def imm_12( inst ):
  return inst & 0xFFF

def imm_24( inst ):
  return inst & 0xFFFFFF

def register_list( inst ):
  return inst & 0xFFFF

def cp_num( inst ):
  return (inst >> 8) & 0xF

def opcode( inst ):
  return (inst >> 21) & 0xF

def opcode_1( inst ):
  return (inst >> 20) & 0x1F

def opcode_2( inst ):
  return (inst >> 5) & 0b111

def I( inst ):
  return (inst >> 25) & 0b1

def P( inst ):
  return (inst >> 24) & 0b1

def U( inst ):
  return (inst >> 23) & 0b1

def B( inst ):
  return (inst >> 22) & 0b1

def W( inst ):
  return (inst >> 21) & 0b1

#def L( inst ):
#  return (inst >> 20) & 0b1

def S( inst ):
  return (inst >> 20) & 0b1

