import sys
import subprocess
sys.path.append('/Users/dmlockhart/vc/git-brg/parc/pymtl')

from inspect import getmembers, ismodule, isfunction

import pisa.pisa_inst_addu_test
import pisa.pisa_inst_subu_test
import pisa.pisa_inst_and_test
import pisa.pisa_inst_or_test
import pisa.pisa_inst_xor_test
import pisa.pisa_inst_nor_test
import pisa.pisa_inst_slt_test
import pisa.pisa_inst_sltu_test

import pisa.pisa_inst_addiu_test
import pisa.pisa_inst_andi_test
import pisa.pisa_inst_ori_test
import pisa.pisa_inst_xori_test
import pisa.pisa_inst_slti_test
import pisa.pisa_inst_sltiu_test

import pisa.pisa_inst_sll_test
import pisa.pisa_inst_srl_test
import pisa.pisa_inst_sra_test
import pisa.pisa_inst_sllv_test
import pisa.pisa_inst_srlv_test
import pisa.pisa_inst_srav_test

import pisa.pisa_inst_lui_test
import pisa.pisa_inst_j_test
import pisa.pisa_inst_jal_test
import pisa.pisa_inst_jr_test
import pisa.pisa_inst_jalr_test

import pisa.pisa_inst_beq_test
import pisa.pisa_inst_bne_test
import pisa.pisa_inst_blez_test
import pisa.pisa_inst_bltz_test
import pisa.pisa_inst_bgez_test
import pisa.pisa_inst_bgtz_test

cmd = './interp_asm_jit-c'
#cmd = 'python interp_asm_jit.py'
asm = 'test.s'

#-----------------------------------------------------------------------
# collect tests
#-----------------------------------------------------------------------
tests = []
test_names = []

for mname, module in getmembers( pisa, ismodule ):
  if not (mname.startswith('pisa_inst') and mname.endswith('test')):
    continue
  for func_name, func in getmembers( module, isfunction ):
    if not (func_name.startswith('gen') and func.__module__.endswith( mname )):
      continue
    test = func()

    name = '{}.{}'.format( mname, func_name )
    test_names.append( name )

    if isinstance( test, str ):
      tests.append( test )
    else:
      tests.append( ''.join( test ) )


#-----------------------------------------------------------------------
# test_asm
#-----------------------------------------------------------------------
import pytest
@pytest.mark.parametrize( 'test_str', tests, ids=test_names )
def test_asm( test_str ):

  with open(asm, 'w') as asm_file:
    lines = test_str.split('\n')
    for line in lines:
      asm_file.write( line.lstrip()+'\n' )

  try:
    subprocess.check_call(
        (cmd+' '+asm).split(),
        env={'PYTHONPATH': '/Users/dmlockhart/vc/hg-opensource/pypy'}
    )
  except subprocess.CalledProcessError as e:
    print test_str
    raise e

  print "DONE"

