#!/usr/bin/env python
#=========================================================================
# build.py
#=========================================================================
# Builds pydgin.

import os
import shutil
import sys
import subprocess

all_targets = [ "pydgin-parc-jit", "pydgin-parc-nojit-debug",
                "pydgin-arm-jit", "pydgin-arm-nojit-debug" ]

def build_target( name, pypy_dir, build_dir ):
  # use the name to determine the arch, jit and debug
  arch = None
  if "parc" in name:
    arch = "parc"
  if "arm" in name:
    assert arch is None, "conflicting arch definitions {} and {}" \
                         .format( arch, "arm" )
    arch = "arm"
  assert arch is not None, "could not determine arch from name"

  if "jit" in name and "nojit" not in name:
    jit = True
  elif "nojit" in name:
    jit = False
  else:
    # default behavior if neither jit or nojit in name
    jit = True

  if "debug" in name and "nodebug" not in name:
    debug = True
  elif "nodebug" in name:
    debug = False
  else:
    # default behavior if neither debug or nodebug in name
    debug = False

  print "Building {}\n  arch: {}\n  jit: {}\n  debug: {}\n" \
        .format( name, arch, jit, debug )

  os.chdir('../{}'.format( arch ) )
  cmd = ( 'pypy {1}/rpython/bin/rpython {2} {0}-sim.py {3}'
          .format( arch, pypy_dir,
                   "--opt=jit" if jit   else "",
                   "--debug"   if debug else "", ) )

  #print cmd
  #ret = subprocess.call( cmd, shell=True )

  #if ret != 0:
  #  print "{} failed building, aborting!".format( name )
  #  sys.exit( ret )

  #shutil.copy( name, '../scripts/{}'.format( build_dir ) )
  os.symlink( '../{}/{}'.format( build_dir, name ),
              '../scripts/builds/{}'.format( name ) )

def main():
  if sys.argv[1] == '--help':
    print "Usage:\n  ./build.py [targets]"
    return 1

  # ensure we know where the pypy source code is
  try:
    pypy_dir = os.environ['PYDGIN_PYPY_SRC_DIR']
  except KeyError as e:
    raise ImportError( 'Please define the PYDGIN_PYPY_SRC_DIR '
                       'environment variable!')

  targets = sys.argv[1:]

  # all includes all_targets
  if "all" in targets:
    targets += all_targets
    targets.remove( "all" )

  # unique-ify
  targets = list( set( targets ) )

  # if there are no targets, we add all
  if len( targets ) == 0:
    targets = all_targets

  # get the version number
  pydgin_ver = subprocess.check_output(
                               "./vcs-version.sh", shell=True ).rstrip()

  print "Building Pydgin..."
  print "Version: {}".format( pydgin_ver )
  print "PyPy source: {}".format( pypy_dir )
  print "Targets: {}".format( targets )

  # create build dir
  build_dir = "builds/pydgin-{}/bin".format( pydgin_ver )
  subprocess.call( "mkdir -p {}".format( build_dir ), shell=True )

  for target in targets:
    build_target( target, pypy_dir, build_dir )

if __name__ == "__main__":
  main()

