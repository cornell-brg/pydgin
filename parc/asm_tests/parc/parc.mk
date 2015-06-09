#=========================================================================
# parc.mk
#=========================================================================

parc_srcs += \
  parc-addiu.S \
  parc-ori.S \
  parc-lui.S \
  parc-bne.S \
  parc-addu.S \
  parc-lw.S \
  parc-sw.S \
  parc-jal.S \
  parc-jr.S \
  parc-andi.S \
  parc-xori.S \
  parc-slti.S \
  parc-sltiu.S \
  parc-sll.S \
  parc-srl.S \
  parc-sra.S \
  parc-subu.S \
  parc-and.S \
  parc-or.S \
  parc-xor.S \
  parc-nor.S \
  parc-slt.S \
  parc-sltu.S \
  parc-sllv.S \
  parc-srlv.S \
  parc-srav.S \
  parc-lh.S \
  parc-lhu.S \
  parc-lb.S \
  parc-lbu.S \
  parc-sh.S \
  parc-sb.S \
  parc-beq.S \
  parc-blez.S \
  parc-bgez.S \
  parc-bltz.S \
  parc-bgtz.S \
  parc-j.S \
  parc-jalr.S \
  parc-mul.S \
  parc-divu.S \
  parc-remu.S \
  parc-mfc0.S \
  parc-amo-add.S \
  parc-amo-and.S \
  parc-amo-or.S \
  parc-amo-xchg.S \
  parc-amo-min.S \
  parc-movn.S \
  parc-movz.S \
  parc-add-s.S \
  parc-sub-s.S \
  parc-mul-s.S \
  parc-div-s.S \
  parc-c-eq-s.S \
  parc-c-lt-s.S \
  parc-c-le-s.S \
  parc-cvt-w-s.S \
  parc-cvt-s-w.S \
  parc-gcd.S \

# temporarily disable these
#  parc-div.S \
#  parc-rem.S \
#  parc-syscall.S \
#  parc-gcd.S \
#  parc-vecincr.S \
#  parc-scan.S \
#  parc-write.S \
#  parc-fstat.S \
#
