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

arch       = 'parc'
dbg_opts   = '--max-insts 1000 --test --debug insts,mem,rf,regdump'
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
  "parcv1-addiu",
  "parcv1-addu",
  "parcv1-bne",
  "parcv1-jal",
  "parcv1-jr",
  "parcv1-lui",
  "parcv1-lw",
  "parcv1-ori",
  "parcv1-sw",
  "parcv2-and",
  "parcv2-andi",
  "parcv2-beq",
  "parcv2-bgez",
  "parcv2-bgtz",
  "parcv2-blez",
  "parcv2-bltz",
  "parcv2-div",
  "parcv2-divu",
  "parcv2-j",
  "parcv2-jalr",
  "parcv2-lb",
  "parcv2-lbu",
  "parcv2-lh",
  "parcv2-lhu",
  "parcv2-mfc0",
  "parcv2-mul",
  "parcv2-nor",
  "parcv2-or",
  "parcv2-rem",
  "parcv2-remu",
  "parcv2-sb",
  "parcv2-sh",
  "parcv2-sll",
  "parcv2-sllv",
  "parcv2-slt",
  "parcv2-slti",
  "parcv2-sltiu",
  "parcv2-sltu",
  "parcv2-sra",
  "parcv2-srav",
  "parcv2-srl",
  "parcv2-srlv",
  "parcv2-subu",
  "parcv2-xor",
  "parcv2-xori",
  "parcv3-add-s",
  "parcv3-amo-add",
  "parcv3-amo-and",
  "parcv3-amo-min",
  "parcv3-amo-or",
  "parcv3-amo-xchg",
  "parcv3-c-eq-s",
  "parcv3-c-le-s",
  "parcv3-c-lt-s",
  "parcv3-cvt-s-w",
  "parcv3-cvt-w-s",
  "parcv3-div-s",
  "parcv3-movn",
  "parcv3-movz",
  "parcv3-mul-s",
  "parcv3-sub-s",
  #"parcv3-syscall"
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

