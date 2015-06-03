#=========================================================================
# mt.mk
#=========================================================================

# Very simple tests
mt_srcs += \
  mt-simple.S \

# Immediate instructions
mt_srcs += \
  mt-addiu.S \
  mt-andi.S \
  mt-ori.S \
  mt-xori.S \
  mt-lui.S \

# Basic arithmetic and logic instructions
mt_srcs += \
  mt-addu.S \
  mt-subu.S \
  mt-and.S \
  mt-or.S \
  mt-nor.S \
  mt-xor.S \

# Shift instructions
mt_srcs += \
  mt-sll.S \
  mt-sra.S \
  mt-srl.S \
  mt-sllv.S \
  mt-srav.S \
  mt-srlv.S \

# Comparison instructions
mt_srcs += \
  mt-slt.S \
  mt-sltu.S \
  mt-slti.S \
  mt-sltiu.S \

# Branch instructions
mt_srcs += \
  mt-beq.S \
  mt-bne.S \
  mt-bgez.S \
  mt-bgtz.S \
  mt-blez.S \
  mt-bltz.S \

# Jump instructions
mt_srcs += \
  mt-j.S \
  mt-jr.S \
  mt-jal.S \
  mt-jalr.S \

# Load instructions
mt_srcs += \
  mt-lw.S \
  mt-lhu.S \
  mt-lbu.S \
  mt-lh.S \
  mt-lb.S \

# Conditional move instructions
#mt_srcs += \
#  mt-movz.S \
#  mt-movn.S \

# Multiply and divide instructions
mt_srcs += \
  mt-mul.S \
  mt-div.S \
  mt-divu.S \
  mt-rem.S \
  mt-remu.S \

# Atomic ops
mt_srcs += \
  mt-amo-or.S \
  mt-amo-and.S \
  mt-amo-add.S \
  mt-amo-xchg.S \
  mt-amo-min.S \


