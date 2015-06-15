def sext_xlen( value ):
  return value

def BRANCH_TARGET( s, inst ):
  return s.pc + inst.sb_imm

def SHAMT( s, inst ):
  return insn.i_imm & 0x3F

raise TRAP_ILLEGAL_INSTRUCTION( Exception ):
  pass
