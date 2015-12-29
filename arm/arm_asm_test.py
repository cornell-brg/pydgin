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
transl_dbg  = '../arm/pydgin-arm-nojit-debug {}'.format( dbg_opts )

#=======================================================================
# assembly file tests
#=======================================================================

#-----------------------------------------------------------------------
# arm assembly files
#-----------------------------------------------------------------------

N, Z, C, V = ('N','Z','C','V')

file_tests = [

  #  Filename,  Expected Register File State

  [ 'adc-00',   {4:2,          N:0, Z:0, C:0, V:0} ],
  [ 'adc-01',   {4:3,          N:0, Z:0, C:1, V:0} ],
  [ 'adc-02',   {1:0x180000,   N:0, Z:0, C:0, V:0} ],
  [ 'adc-03',   {1:0x180001,   N:0, Z:0, C:0, V:0} ],
  [ 'add-00',   {1:0,          N:0, Z:1, C:0, V:0} ],
  [ 'add-01',   {1:0x80000000, N:1, Z:0, C:0, V:1} ],
  [ 'add-02',   {1:0x00000000, N:0, Z:1, C:0, V:0} ],
  [ 'cmp-00',   {4:0xFFFFFFFF, N:1, Z:0, C:1, V:0} ],
  [ 'cmp-01',   {4:0x3F0     , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-02',   {4:0x3F0     , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-03',   {4:0x3F0     , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-04',   {4:0x3F0     , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-05',   {4:0x0       , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-06',   {4:0x3F0     , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-07',   {4:0x3F0     , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-08',   {4:0x3f0000  , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-09',   {4:0x3F0000  , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-10',   {4:0x3F0000  , N:0, Z:1, C:1, V:0} ],
  [ 'cmp-11',   {4:0x9C000000, N:1, Z:0, C:0, V:0} ],
  [ 'cmp-12',   {4:0x9C000000, N:1, Z:0, C:0, V:0} ],
  [ 'cmp-13',   {4:0xf1000000, N:0, Z:0, C:0, V:0} ],
  [ 'cmp-14',   {4:0xf1000000, N:0, Z:0, C:0, V:0} ],
  [ 'ldm-00',   {5:1, 6:2,     N:0, Z:0, C:0, V:0} ],
  [ 'ldm-01',   {5:1, 6:2,     N:0, Z:0, C:0, V:0} ],
  [ 'ldm-02',   {5:2, 6:3,     N:0, Z:0, C:0, V:0} ],
  [ 'ldm-03',   {5:1, 6:2,     N:0, Z:0, C:0, V:0} ],
  [ 'ldr-00',   {5:0xFF,       N:0, Z:0, C:0, V:0} ],
  [ 'ldr-01',   {5:0xFF,       N:0, Z:0, C:0, V:0} ],
  [ 'ldr-02',   {5:0xFF00,     N:0, Z:0, C:0, V:0} ],
  [ 'ldr-03',   {4:0, 5:0,
                 6:0x8094++28++24,
                               N:0, Z:0, C:0, V:0} ],
  [ 'ldrb-00',  {5:0xF,        N:0, Z:0, C:0, V:0} ],
  [ 'ldrbcs-00',{5:0xF,        N:0, Z:0, C:1, V:0} ],
  [ 'ldrbcs-01',{5:1,          N:1, Z:0, C:0, V:0} ],
  [ 'ldrbeq-00',{5:0xF,        N:0, Z:1, C:1, V:0} ],
  [ 'ldrbne-00',{5:0xF,        N:0, Z:0, C:1, V:0} ],
  [ 'ldrh-00',  {5:0x101,      N:0, Z:0, C:0, V:0} ],
  [ 'ldrhi-00', {5:0xFF,       N:0, Z:0, C:1, V:0} ],
  [ 'ldrls-00', {5:0xFF,       N:0, Z:1, C:1, V:0} ],
  [ 'ldrne-00', {5:0xFF,       N:0, Z:0, C:1, V:0} ],
  [ 'mla-00',   {9:0x90000000, N:1, Z:0, C:0, V:0} ],
  [ 'mov-00',   {4:0,          N:0, Z:0, C:0, V:0} ],
  [ 'mov-01',   {4:1,          N:0, Z:0, C:0, V:0} ],
  [ 'mov-02',   {4:0x8094 + 8, N:0, Z:0, C:0, V:0} ],
  [ 'mov-03',   {4:0,
                 5:0x8094+20+8,
                 6:0x8094+24+8,
                               N:0, Z:0, C:0, V:0} ],
  [ 'mov-04',   {4:2,          N:0, Z:0, C:0, V:0} ],
  [ 'mov-05',   {4:0x10,       N:0, Z:0, C:0, V:0} ],
  [ 'mov-06',   {3:0x50000005, N:0, Z:0, C:1, V:0} ],
  [ 'mov-07',   {3:0xD0000005, N:1, Z:0, C:1, V:0} ],
  [ 'movcc-00', {4:1,          N:0, Z:0, C:0, V:0} ],
  [ 'movcc-01', {4:0,          N:0, Z:1, C:1, V:0} ],
  [ 'movcs-00', {4:1,          N:0, Z:1, C:1, V:0} ],
  [ 'movcs-01', {4:0,          N:0, Z:0, C:0, V:0} ],
  [ 'moveq-00', {4:0,          N:0, Z:0, C:0, V:0} ],
  [ 'moveq-01', {4:1,          N:0, Z:1, C:1, V:0} ],
  [ 'movgt-00', {4:1,          N:0, Z:0, C:0, V:0} ],
  [ 'movgt-01', {4:0,          N:1, Z:0, C:0, V:0} ],
  [ 'movhi-00', {4:1,          N:0, Z:0, C:1, V:0} ],
  [ 'movls-00', {4:0,          N:0, Z:0, C:1, V:0} ],
  [ 'movls-01', {4:1,          N:0, Z:1, C:1, V:0} ],
  [ 'movne-00', {4:1,          N:0, Z:0, C:1, V:0} ],
  [ 'movne-01', {4:0,          N:0, Z:1, C:1, V:0} ],
  [ 'mul-00',   {3:0xe0000000, N:1, Z:0, C:0, V:0} ],
  [ 'mul-01',   {3:0,          N:0, Z:1, C:0, V:0} ],
  [ 'mvn-00',   {1:0xfffffff8, N:1, Z:0, C:0, V:0} ],
  [ 'mvn-01',   {1:0,          N:0, Z:1, C:0, V:0} ],
  [ 'mvneq-00', {1:0xfffffff8, N:0, Z:1, C:1, V:0} ],
  [ 'mvnne-00', {1:0xfffffff8, N:0, Z:0, C:1, V:0} ],
  [ 'orr-00',   {1:0xffffffff, N:1, Z:0, C:0, V:0} ],
  [ 'orr-01',   {1:0xff,       N:0, Z:0, C:0, V:0} ],
  [ 'orr-02',   {4:0,
                 5:0x8094+12+16,
                 6:0x8094+12+20,
                               N:0, Z:0, C:0, V:0} ],
  [ 'orreq-00', {1:0xfffffff8, N:0, Z:0, C:1, V:0} ],
  [ 'orreq-01', {1:0xffffffff, N:1, Z:0, C:1, V:0} ],
  [ 'orrgt-00', {1:1,          N:0, Z:0, C:0, V:0} ],
  [ 'orrgt-01', {1:0xf0000001, N:1, Z:0, C:0, V:1} ],
  [ 'orrhi-00', {1:0xffffffff, N:1, Z:0, C:1, V:0} ],
  [ 'orrhi-01', {1:0xfffffff8, N:0, Z:1, C:1, V:0} ],
  [ 'orrne-00', {1:0xfffffff8, N:0, Z:1, C:1, V:0} ],
  [ 'orrne-01', {1:0xffffffff, N:1, Z:0, C:0, V:0} ],
  [ 'rsb-00',   {1:0xfffffff9, N:1, Z:0, C:0, V:0} ],
  [ 'rsb-01',   {1:0,          N:0, Z:1, C:1, V:0} ],
  [ 'rsb-02',   {6:0x28,       N:0, Z:0, C:0, V:0} ],
  [ 'rsbeq-00', {1:0xfffffff9, N:0, Z:1, C:1, V:0} ],
  [ 'rsbne-00', {1:0xfffffff9, N:0, Z:0, C:1, V:0} ],
  [ 'rsble-00', {1:0xfffffff9, N:0, Z:1, C:1, V:0} ],
  [ 'rsble-01', {1:0xfffffff9, N:1, Z:0, C:0, V:0} ],
  [ 'smull-00', {1:0x85d093ea,
                 2:0x834e0b5f,
                 14:0x00007e56,
                 3:0xffffc276, N:0, Z:0, C:0, V:0} ],
  [ 'smull-01', {3:0, 4:0,     N:0, Z:1, C:0, V:0} ],
  [ 'smull-02', {3:0x80000001, 
		   4:0xffffffff, N:1, Z:0, C:0, V:0} ],
  [ 'smull-03', {3:0, 
		   4:0x40000000, N:0, Z:0, C:0, V:0} ],
  [ 'smull-04', {3:0x80000000, 
		   4:0xc0000000, N:1, Z:0, C:0, V:0} ],
  [ 'stm-00',   {8:1, 9:2,     N:0, Z:0, C:0, V:0} ],
  [ 'stm-01',   {8:0xff,
                 9:1,
                 10:2,         N:0, Z:0, C:0, V:0} ],
  [ 'str-00',   {6:1,          N:0, Z:0, C:0, V:0} ],
  [ 'strb-00',  {6:0,          N:0, Z:0, C:0, V:0} ],
  [ 'strb-01',  {6:0x1f,       N:0, Z:0, C:0, V:0} ],
  [ 'strbcc-00',{6:0x100000ff, N:0, Z:0, C:0, V:0} ],
  [ 'strbcs-00',{6:0x100000ff, N:0, Z:1, C:1, V:0} ],
  [ 'strbne-00',{6:0x100000ff, N:0, Z:0, C:1, V:0} ],
  [ 'strcc-00', {6:1,          N:0, Z:0, C:0, V:0} ],
  [ 'streq-00', {6:1,          N:0, Z:1, C:1, V:0} ],
  [ 'strhi-00', {6:1,          N:0, Z:0, C:1, V:0} ],
  [ 'strls-00', {6:1,          N:0, Z:1, C:1, V:0} ],
  [ 'strne-00', {6:1,          N:0, Z:0, C:1, V:0} ],
  [ 'sub-00',   {1:0xfffffff9, N:1, Z:0, C:0, V:0} ],
  [ 'sub-01',   {1:0,          N:0, Z:1, C:1, V:0} ],
  [ 'sub-02',   {4:0, 5:0,
                 6:0x8094++16++16,
                               N:0, Z:0, C:0, V:0} ],
  [ 'subeq-00', {1:1,          N:0, Z:0, C:1, V:0} ],
  [ 'subeq-01', {1:0xfffffff9, N:1, Z:0, C:0, V:0} ],
  [ 'sublt-00', {1:1,          N:0, Z:0, C:0, V:0} ],
  [ 'sublt-01', {1:0x80000001, N:1, Z:0, C:0, V:1} ],
  [ 'teq-00',   {4:3,          N:0, Z:1, C:0, V:0} ],
  [ 'teq-01',   {4:1,          N:0, Z:0, C:0, V:0} ],
  [ 'teq-02',   {4:0x80000000, N:1, Z:0, C:0, V:0} ],
  [ 'tst-00',   {4:0,          N:0, Z:1, C:0, V:0} ],
  [ 'tst-01',   {4:1,          N:0, Z:1, C:0, V:0} ],
  [ 'tst-02',   {4:0x80000000, N:1, Z:0, C:1, V:0} ],
  [ 'tst-03',   {2:0x7fe886c1, N:0, Z:0, C:0, V:0} ],
  [ 'tst-04',   {2:0xbfe8b860, N:0, Z:1, C:0, V:0} ],
  [ 'tstne-00', {4:0x80000000, N:1, Z:0, C:1, V:0} ],
  [ 'tstne-01', {4:0x80000000, N:0, Z:1, C:1, V:0} ],
  [ 'umlal-00', {3:0, 4:0,     N:0, Z:1, C:0, V:0} ],
  [ 'umlal-01', {3:0x80000000,
                 4:0,          N:0, Z:0, C:0, V:0} ],
  [ 'umlal-02', {3:0x40000000,
                 4:0xffffffff, N:1, Z:0, C:0, V:0} ],
  [ 'umlal-03', {3:0, 4:1,     N:0, Z:0, C:0, V:0} ],
  [ 'umull-00', {3:0, 4:0,     N:0, Z:1, C:0, V:0} ],
  [ 'umull-01', {3:0, 4:1,     N:0, Z:0, C:0, V:0} ],
  [ 'umull-02', {3:0x40000000,
                 4:0xbfffffff, N:1, Z:0, C:0, V:0} ],
  [ 'eor-00',   {4:3,  5:3,
                 6:0,  7:1,    N:0, Z:0, C:0, V:0} ],
  [ 'eor-01',   {4:3,  5:3,    N:0, Z:0, C:0, V:0} ],
  [ 'eor-02',   {4:3,  5:0,    N:0, Z:1, C:0, V:0} ],
  [ 'eor-03',   {4:3,
                 5:0x80000002, N:1, Z:0, C:1, V:0} ],
  [ 'eor-04',   {4:3,
                 3:0b11011,
                 5:0x60000003, N:0, Z:0, C:0, V:0} ],
  [ 'eor-05',   {4:0x0cb00000, N:0, Z:0, C:0, V:0} ],

]

#-----------------------------------------------------------------------
# test_asm_file_py
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'test_file,expected_out', file_tests )
@pytest.mark.parametrize( 'sim', [ python_dbg, transl_dbg ] )
def test_asm_file_py( tmpdir, test_file, expected_out, sim ):

  # disabled compiling here in the interest of providing pre-compiled test
  # files for travis ci

  #elf_file    = tmpdir.join('a.out')
  #asm_file    = os.path.join( test_dir, asm_file )
  #compile_cmd = '{assembler} {asm_file} -o {elf_file}'
  #cmd = compile_cmd.format( assembler = assembler,
  #                          asm_file  = asm_file,
  #                          elf_file  = elf_file )
  #print cmd
  #subprocess.check_call( cmd, shell=True )

  elf_file = "asm_tests/build/{}".format( test_file )

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

    if not line or 'retval' in line:
      continue

    elif 0 < collect_regs <= 5:
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
