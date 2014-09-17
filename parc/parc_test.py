#=======================================================================
# parc_test.py
#=======================================================================

import os
import itertools
import pytest
import subprocess

#-----------------------------------------------------------------------
# test configuration
#-----------------------------------------------------------------------

python     = 'python ../parc/pisa-sim.py'
translated = '../parc/pydgin-parc-jit'

ub_path  = '../ubmark-nosyscalls/build-parc'

ubmarks = [ os.path.join( ub_path, x ) for x in [
  'ubmark-vvadd',
  'ubmark-cmplx-mult',
  'ubmark-bin-search',
  'ubmark-masked-filter',
]]

# test binary with and without command line arguments

iterations = ('', '3')
configs    = list( itertools.product( ubmarks, iterations ) )

# verify binaries exist
if not os.path.exists( ub_path ):
  raise Exception('Please build ubmark binaries in {}!'.format( ub_path ))
for filename in ubmarks:
  if not os.path.isfile( filename ):
    raise Exception('Please build ubmark binary: {}'.format( filename ))

#-----------------------------------------------------------------------
# test_python
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'ubmark,iterations', configs )
def test_python( ubmark, iterations, sim=python ):
  cmd = '{sim} {ubmark} {iterations}'.format( **locals() )

  subprocess.check_call( cmd, shell=True )

#-----------------------------------------------------------------------
# test_translated
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'ubmark,iterations', configs )
def test_translated( ubmark, iterations, sim=translated ):
  cmd = '{sim} {ubmark} {iterations}'.format( **locals() )

  subprocess.check_call( cmd, shell=True )
