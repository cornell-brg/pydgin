from utils import trim_64

def BRANCH_TARGET( s, inst ):
  return trim_64( s.pc + inst.sb_imm )

def JUMP_TARGET( s, inst ):
  return s.pc + inst.uj_imm

def SHAMT( s, inst ):
  return inst.i_imm & 0x3F

class TRAP_ILLEGAL_INSTRUCTION( Exception ):
  pass
