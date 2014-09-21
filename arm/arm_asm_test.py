#=======================================================================
# arm_asm_test.py
#=======================================================================

import os.path
import itertools
import pytest
import subprocess
import collections
import pprint

#-----------------------------------------------------------------------
# test configuration
#-----------------------------------------------------------------------

assembler   = 'arm-unknown-linux-uclibcgnueabi-gcc -nostdlib'
test_dir    = '../arm/asm_tests'

# arm instruction set simulator

dbg_opts    = '--debug insts,mem,regdump,syscalls'

python_dbg  = 'python ../arm/arm-sim.py {}'   .format( dbg_opts )
transl_dbg  = '../arm/pydgin-arm-jit-debug {}'.format( dbg_opts )

#=======================================================================
# assembly file tests
#=======================================================================

#-----------------------------------------------------------------------
# arm assembly files
#-----------------------------------------------------------------------

N, Z, C, V = ('N','Z','C','V')

file_tests = [

  #  Filename,  Expected Register File State
  
  [ 'add-00.S',   {1:0,          N:0, Z:1, C:0, V:0} ],
  [ 'add-01.S',   {1:0x80000000, N:1, Z:0, C:0, V:1} ],
  [ 'cmp-00.S',   {4:0xFFFFFFFF, N:1, Z:0, C:1, V:0} ],
  [ 'ldm-00.S',   {5:1, 6:2,     N:0, Z:0, C:0, V:0} ],
  [ 'ldm-01.S',   {5:1, 6:2,     N:0, Z:0, C:0, V:0} ],
  [ 'ldm-02.S',   {5:2, 6:3,     N:0, Z:0, C:0, V:0} ],
  [ 'ldm-03.S',   {5:1, 6:2,     N:0, Z:0, C:0, V:0} ],
  [ 'ldr-00.S',   {5:0xFF, 	 N:0, Z:0, C:0, V:0} ],
  [ 'ldr-01.S',   {5:0xFF, 	 N:0, Z:0, C:0, V:0} ],
  [ 'ldr-02.S',   {5:0xFF00, 	 N:0, Z:0, C:0, V:0} ],
  [ 'ldrb-00.S',  {5:0xF, 	 N:0, Z:0, C:0, V:0} ],
  [ 'ldrh-00.S',  {5:0x101, 	 N:0, Z:0, C:0, V:0} ],
  [ 'mla-00.S',   {9:0x90000000, N:1, Z:0, C:0, V:0} ],
  [ 'mov-00.S',   {4:0,          N:0, Z:0, C:0, V:0} ],
  [ 'mov-01.S',   {4:1,          N:0, Z:0, C:0, V:0} ],
  [ 'mul-00.S',   {3:0xe0000000, N:1, Z:0, C:0, V:0} ],
  [ 'mul-01.S',   {3:0,  	 N:0, Z:1, C:0, V:0} ],
  [ 'mvn-00.S',   {1:0xfffffff8, N:1, Z:0, C:0, V:0} ],
  [ 'mvn-01.S',   {1:0, 	 N:0, Z:1, C:0, V:0} ],
  [ 'orr-00.S',   {1:0xffffffff, N:1, Z:0, C:0, V:0} ],
  [ 'orr-01.S',   {1:0xff, 	 N:0, Z:0, C:0, V:0} ],
  [ 'rsb-00.S',   {1:0xfffffff9, N:1, Z:0, C:0, V:0} ],
  [ 'rsb-01.S',   {1:0, 	 N:0, Z:1, C:1, V:0} ],
  [ 'stm-00.S',   {8:1, 9:2, 	 N:0, Z:0, C:0, V:0} ],
  [ 'stm-01.S',   {8:0xff, 
		   9:1, 10:2, 	 N:0, Z:0, C:0, V:0} ],
  [ 'str-00.S',   {6:1, 	 N:0, Z:0, C:0, V:0} ],
  [ 'sub-00.S',   {1:0xfffffff9, N:1, Z:0, C:0, V:0} ],
  [ 'sub-01.S',   {1:0, 	 N:0, Z:1, C:1, V:0} ],
  [ 'teq-00.S',   {4:3, 	 N:0, Z:1, C:0, V:0} ],
  [ 'teq-01.S',   {4:1, 	 N:0, Z:0, C:0, V:0} ],
  [ 'teq-02.S',   {4:0x80000000, N:1, Z:0, C:0, V:0} ],
  [ 'tst-00.S',   {4:0, 	 N:0, Z:1, C:0, V:0} ],
  [ 'tst-01.S',   {4:1, 	 N:0, Z:1, C:0, V:0} ],
  [ 'tst-02.S',   {4:0x80000000, N:1, Z:0, C:1, V:0} ],
  [ 'umull-00.S', {3:0, 4:0, 	 N:0, Z:1, C:0, V:0} ],
  [ 'umull-01.S', {3:0, 4:1, 	 N:0, Z:0, C:0, V:0} ],
  [ 'umull-02.S', {3:0x40000000, 
		   4:0xbfffffff, N:1, Z:0, C:0, V:0} ],

]

#-----------------------------------------------------------------------
# test_asm_file_py
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'asm_file,expected_out', file_tests )
def test_asm_file_py( tmpdir, asm_file, expected_out, sim=python_dbg ):

  # compile the assembly file

  elf_file    = tmpdir.join('a.out')
  asm_file    = os.path.join( test_dir, asm_file )
  compile_cmd = '{assembler} {asm_file} -o {elf_file}'
  cmd = compile_cmd.format( assembler = assembler,
                            asm_file  = asm_file,
                            elf_file  = elf_file )
  print cmd
  subprocess.check_call( cmd, shell=True )

  simulate_and_verify( sim, elf_file, expected_out )


#-----------------------------------------------------------------------
# simulate_and_verify
#-----------------------------------------------------------------------
def simulate_and_verify( sim, elf_file, expected_out ):

  # simulate the elf file

  simulate_cmd = '{sim} {elf_file}'.format( sim      = sim,
                                            elf_file = elf_file )
  print simulate_cmd
  output = subprocess.check_output( simulate_cmd, shell=True )

  # parse the final register file state of the simulation

  rf = get_regs_from_output( output )
  for k, v in rf.items():
    print '{:>2} {:8x}'.format( k, v )

  # verify the output

  for key in expected_out:
    print 'VERIFY {:1s}: {:8x} == {:8x}'.format( str(key), rf[ key ], expected_out[ key ] )
    assert rf[ key ] == expected_out[ key ]


#-----------------------------------------------------------------------
# get_regs_from_output
#-----------------------------------------------------------------------
def get_regs_from_output( output_str ):

  collect_regs = 0
  counter      = range(16)[::-1]
  rf           = collections.OrderedDict()

  # Utility function to parse one line of register file output
  def parse_regs( line ):
    tmp = line.split(':')[1:]     # split on the colon
    for i in range(3):
      tmp[i] = tmp[i].split()[0]  # first 3 have extra cruft, remove

    for x in tmp:
      reg_id     = counter.pop()  # HACKY global state!
      rf[reg_id] = int( x, 16 )   # convert strings to integers

  # Utility function to parse condition flags output.
  def parse_flags( line ):
    idx = ['N','Z','C','V']
    for i, char in enumerate( line ):
      rf[idx[i]] = 1 if char != '-' else 0

  # Parse the output of the simulator ignoring all lines until we reach
  # the exit syscall. We then parse four lines of information: the first
  # four contain the register file (4 lines of 4 regs each), the last
  # line contains the condition code flags.

  for line in output_str.split('\n'):
    if 0 < collect_regs <= 5:
      print line
      if collect_regs == 5: parse_flags( line )
      else:                 parse_regs ( line )
      collect_regs += 1

    elif 'syscall_exit' in line:
      collect_regs += 1

  # Return a dictionary containing the values of the register file and
  # condition flags. Registers are keyed by their register number (int),
  # condition flags are keyed by their letter identifier (N, Z, C, V).

  return rf
