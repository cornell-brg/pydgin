import sys
import subprocess
sys.path.append('/Users/dmlockhart/vc/git-brg/parc/pymtl')

from pisa.pisa_inst_addiu_test import gen_basic_test
from pisa.pisa_inst_addiu_test import gen_dest_byp_test
from pisa.pisa_inst_addiu_test import gen_src_byp_test
from pisa.pisa_inst_addiu_test import gen_srcs_dest_test
from pisa.pisa_inst_addiu_test import gen_value_test
from pisa.pisa_inst_addiu_test import gen_random_test

cmd = './interp_asm_jit-c'
#cmd = 'python interp_asm_jit.py'
asm = 'test.s'

#-----------------------------------------------------------------------
# collect tests
#-----------------------------------------------------------------------
tests = []
test_names = []
for name, obj in vars().items():
  if not name.startswith('gen_'):
    continue
  test = obj()
  if isinstance( test, str ):
    test_names.append( name )
    tests.append( test )
  else:
    names = [ '{}_{}'.format( name, x ) for x, _ in enumerate(test) ]
    test_names.extend( names )
    tests.extend( test )


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

