#=======================================================================
# instruction.py
#=======================================================================

def rd( inst ):
  return (inst >> 11) & 0x1F

def rt( inst ):
  return (inst >> 16) & 0x1F

def rs( inst ):
  return (inst >> 21) & 0x1F

def fd( inst ):
  return (inst >>  6) & 0x1F

def ft( inst ):
  return (inst >> 16) & 0x1F

def fs( inst ):
  return (inst >> 11) & 0x1F

def imm( inst ):
  return inst & 0xFFFF

def jtarg( inst ):
  return inst & 0x3FFFFFF

def shamt( inst ):
  return (inst >> 6) & 0x1F

