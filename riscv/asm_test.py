#=======================================================================
# asm_test.py
#=======================================================================

import os
import itertools
import pytest
import subprocess

#-----------------------------------------------------------------------
# test configuration
#-----------------------------------------------------------------------

arch       = 'riscv'
dbg_opts   = '--max-insts 10000 --test --debug insts,mem,rf,regdump'
dir        = '../{}'.format( arch )
transl_bin = 'pydgin-{arch}-nojit-debug'.format( **locals() )
build_dir  = '{dir}/asm_tests/build'.format( **locals() )

python_dbg = 'python {dir}/{arch}-sim.py {dbg_opts}'.format( **locals() )
transl_dbg = '{dir}/{transl_bin} {dbg_opts}'.format( **locals() )

sims = [ python_dbg ]

# add translated dbg only if it exists
if transl_bin in os.listdir( dir ):
  sims.append( transl_dbg )

tests = [
  "rv64ui-p-add",
  "rv64ui-p-addi",
  "rv64ui-p-addiw",
  "rv64ui-p-addw",
  "rv64ui-p-amoadd_d",
  "rv64ui-p-amoadd_w",
  "rv64ui-p-amoand_d",
  "rv64ui-p-amoand_w",
  "rv64ui-p-amomax_d",
  "rv64ui-p-amomax_w",
  "rv64ui-p-amomaxu_d",
  "rv64ui-p-amomaxu_w",
  "rv64ui-p-amomin_d",
  "rv64ui-p-amomin_w",
  "rv64ui-p-amominu_d",
  "rv64ui-p-amominu_w",
  "rv64ui-p-amoor_d",
  "rv64ui-p-amoor_w",
  "rv64ui-p-amoswap_d",
  "rv64ui-p-amoswap_w",
  "rv64ui-p-amoxor_d",
  "rv64ui-p-amoxor_w",
  "rv64ui-p-and",
  "rv64ui-p-andi",
  "rv64ui-p-auipc",
  "rv64ui-p-beq",
  "rv64ui-p-bge",
  "rv64ui-p-bgeu",
  "rv64ui-p-blt",
  "rv64ui-p-bltu",
  "rv64ui-p-bne",
  "rv64ui-p-div",
  "rv64ui-p-divu",
  "rv64ui-p-divuw",
  "rv64ui-p-divw",
  "rv64ui-p-example",
  "rv64ui-p-fence_i",
  "rv64ui-p-j",
  "rv64ui-p-jal",
  "rv64ui-p-jalr",
  "rv64ui-p-lb",
  "rv64ui-p-lbu",
  "rv64ui-p-ld",
  "rv64ui-p-lh",
  "rv64ui-p-lhu",
  "rv64ui-p-lui",
  "rv64ui-p-lw",
  "rv64ui-p-lwu",
  "rv64ui-p-mul",
  "rv64ui-p-mulh",
  "rv64ui-p-mulhsu",
  "rv64ui-p-mulhu",
  "rv64ui-p-mulw",
  "rv64ui-p-or",
  "rv64ui-p-ori",
  "rv64ui-p-rem",
  "rv64ui-p-remu",
  "rv64ui-p-remuw",
  "rv64ui-p-remw",
  "rv64ui-p-sb",
  "rv64ui-p-sd",
  "rv64ui-p-sh",
  "rv64ui-p-simple",
  "rv64ui-p-sll",
  "rv64ui-p-slli",
  "rv64ui-p-slliw",
  "rv64ui-p-sllw",
  "rv64ui-p-slt",
  "rv64ui-p-slti",
  "rv64ui-p-sltiu",
  "rv64ui-p-sltu",
  "rv64ui-p-sra",
  "rv64ui-p-srai",
  "rv64ui-p-sraiw",
  "rv64ui-p-sraw",
  "rv64ui-p-srl",
  "rv64ui-p-srli",
  "rv64ui-p-srliw",
  "rv64ui-p-srlw",
  "rv64ui-p-sub",
  "rv64ui-p-subw",
  "rv64ui-p-sw",
  "rv64ui-p-xor",
  "rv64ui-p-xori",
  "rv64ui-pm-lrsc",

  "rv64uf-p-fadd",
  "rv64uf-p-fclass",
  "rv64uf-p-fcmp",
  "rv64uf-p-fcvt",
  "rv64uf-p-fcvt_w",
  "rv64uf-p-fdiv",
  "rv64uf-p-fmadd",
  "rv64uf-p-fmin",
  "rv64uf-p-fsgnj",
  "rv64uf-p-ldst",
  "rv64uf-p-move",
  "rv64uf-p-structural",
]

# verify binaries exist
if not os.path.exists( build_dir ):
  raise Exception('Please build test binaries in {}!'.format( build_dir ))
for filename in tests:
  if not os.path.isfile( "{}/{}".format( build_dir, filename ) ):
    raise Exception('Please build test binary: {}'.format( filename ))

#-----------------------------------------------------------------------
# test_asm
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'test', tests )
@pytest.mark.parametrize( 'sim', sims )
def test_asm( test, sim ):

  test_bin = "{}/{}".format( build_dir, test )
  cmd = '{sim} {test_bin}'.format( **locals() )

  output = subprocess.check_output( cmd, shell=True )

  # make sure we got a passed message

  assert "Reached the max_insts" not in output
  assert "FAILED" not in output
  assert "passed" in output

