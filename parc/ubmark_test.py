#=======================================================================
# ubmark_test.py
#=======================================================================

import os
import itertools
import pytest
import subprocess

#-----------------------------------------------------------------------
# test configuration
#-----------------------------------------------------------------------

arch       = 'parc'
dbg_opts   = '--debug insts,mem,rf,regdump'
opts       = '--max-insts 10000'
dir        = '../{}'.format( arch )

python     = 'python {dir}/{arch}-sim.py {opts}'.format( **locals() )
python_dbg = 'python {dir}/{arch}-sim.py {opts} {dbg_opts}'.format( **locals() )

# discover translated binaries

transl_bins     = filter( lambda b : b.startswith("pydgin-{}-".format(arch)),
                          os.listdir( dir ) )
transl_dbg_bins = filter( lambda b : "-debug" in b, transl_bins )
transl     = map( lambda b : "{}/{} {}".format( dir, b, opts ), transl_bins )
transl_dbg = map( lambda b : "{}/{} {} {}".format( dir, b, opts, dbg_opts ),
                  transl_dbg_bins )

ub_path  = '../ubmark-nosyscalls/build-{}'.format( arch )

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
# test_ubmark
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'ubmark,iterations', configs )
@pytest.mark.parametrize( 'sim', [python, python_dbg] + transl + transl_dbg )
def test_ubmark( ubmark, iterations, sim ):
  cmd = '{sim} {ubmark} {iterations}'.format( **locals() )

  output = subprocess.check_output( cmd, shell=True )

  # make sure we got a passed message

  assert "Reached the max_insts" not in output
  assert "failed" not in output
  assert "passed" in output

