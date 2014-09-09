#=======================================================================
# syscalls.py
#=======================================================================
#
# Implementations of emulated syscalls. Call numbers were borrowed from
# the following files:
#
# - https://github.com/cornell-brg/maven-sim-isa/blob/master/common/syscfg.h
# - https://github.com/cornell-brg/pyparc/blob/master/pkernel/pkernel/syscfg.h
# - https://github.com/cornell-brg/maven-sys-xcc/blob/master/src/libgloss/maven/machine/syscfg.h
# - https://github.com/cornell-brg/gem5-mcpat/blob/master/src/arch/mips/linux/process.cc
#
# Implementation details from the Maven proxy kernel:
#
# - https://github.com/cornell-brg/pyparc/blob/master/pkernel/pkernel/pkernel.c#L463-L544
# - https://github.com/cornell-brg/pyparc/blob/master/pkernel/pkernel/pkernel-xcpthandler.S#L78-L89
#
#   // Jump to C function to handle syscalls
#
#   move    $a3, $a2 // arg2
#   move    $a2, $a1 // arg1
#   move    $a1, $a0 // arg0
#   move    $a0, $v0 // syscall number
#   la      $t0, handle_syscall
#   jalr    $t0
#
#   // Restore user context
#
#   move    $k0, $sp
#
# Details for newlib syscalls from the Maven cross compiler:
#
# - https://github.com/cornell-brg/maven-sys-xcc/blob/master/src/libgloss/maven/syscalls.c
#
# According to Berkin, only the following syscalls are needed by pbbs:
#
# - read (2), write (3), open (4), close (5), lseek (8)
#
# Other syscall emulation resources:
#
# - http://brg.csl.cornell.edu/wiki/Proxy%20Kernel%20vs%20Syscall%20Emulation
# - http://wiki.osdev.org/Porting_Newlib
# - http://wiki.osdev.org/OS_Specific_Toolchain
# - http://www.embecosm.com/appnotes/ean9/ean9-howto-newlib-1.0.html
#

from isa import reg_map
import sys
import os

#-----------------------------------------------------------------------
# os state and helpers
#-----------------------------------------------------------------------

# short names for registers

v0 = reg_map['a1']  # return value
a0 = reg_map['a1']  # arg0
a1 = reg_map['a2']  # arg1
a2 = reg_map['a3']  # arg2
a3 = reg_map['a4']  # error

# solaris to linux open flag conversion
# https://docs.python.org/2/library/os.html#open-constants

flag_table = [
  [ 0x0000, os.O_RDONLY   ], # NEWLIB_O_RDONLY
  [ 0x0001, os.O_WRONLY   ], # NEWLIB_O_WRONLY
  [ 0x0002, os.O_RDWR     ], # NEWLIB_O_RDWR
  [ 0x0008, os.O_APPEND   ], # NEWLIB_O_APPEND
  [ 0x0200, os.O_CREAT    ], # NEWLIB_O_CREAT
  [ 0x0400, os.O_TRUNC    ], # NEWLIB_O_TRUNC
  [ 0x0800, os.O_EXCL     ], # NEWLIB_O_EXCL
  [ 0x2000, os.O_SYNC     ], # NEWLIB_O_SYNC
  [ 0x4000, os.O_NDELAY   ], # NEWLIB_O_NDELAY
  [ 0x4000, os.O_NONBLOCK ], # NEWLIB_O_NONBLOCK
  [ 0x8000, os.O_NOCTTY   ], # NEWLIB_O_NOCTTY
 #[ 0x????, os.O_DIRECTORY],
 #[ 0x????, os.O_ASYNC    ],
 #[ 0x????, os.O_DSYNC    ],
 #[ 0x????, os.O_NOATIME  ],
 #[ 0x????, os.O_DIRECT   ],
 #[ 0x????, os.O_LARGEFILE],
 #[ 0x????, os.O_NOFOLLOW ],
 #[ 0x????, os.O_RSYNC    ],
]

file_descriptors = {
  0: os.dup( sys.stdin .fileno() ),
  1: os.dup( sys.stdout.fileno() ),
  2: os.dup( sys.stderr.fileno() ),
}

#-----------------------------------------------------------------------
# exit
#-----------------------------------------------------------------------
def syscall_exit( s ):
  exit_code = s.rf[ a0 ]
  print
  print "NUM  INSTS:", s.ncycles
  print "STAT INSTS:", s.stat_ncycles
  print "EXIT CODE: ", exit_code
  # TODO: this is an okay way to terminate the simulator?
  #       sys.exit(1) is not valid python
  s.status = exit_code

#-----------------------------------------------------------------------
# read
#-----------------------------------------------------------------------
def syscall_read( s ):
  file_ptr = s.rf[ a0 ]
  data_ptr = s.rf[ a1 ]
  nbytes   = s.rf[ a2 ]

  if file_ptr not in file_descriptors:
    s.rf[ v0 ] = s.rf[ a3 ] = -1
    return

  fd   = file_descriptors[ file_ptr ]
  data = os.read( fd, nbytes )

  s.rf[ v0 ] = len( data )   # return the number of bytes read
  s.rf[ a3 ] = 0

#-----------------------------------------------------------------------
# write
#-----------------------------------------------------------------------
def syscall_write( s ):
  file_ptr = s.rf[ a0 ]
  data_ptr = s.rf[ a1 ]
  nbytes   = s.rf[ a2 ]

  if file_ptr not in file_descriptors:
    s.rf[ v0 ] = s.rf[ a3 ] = -1
    return

  fd   = file_descriptors[ file_ptr ]

  # TODO: use mem.read()
  assert data_ptr >= 0 and nbytes >= 0
  data = ''.join( s.mem.data[data_ptr:data_ptr+nbytes] )

  nbytes_written = os.write( fd, data )
  # https://docs.python.org/2/library/os.html#os.fsync
  #os.fsync( fd )  # this causes Invalid argument error for some reason...

  s.rf[ v0 ] = nbytes_written
  s.rf[ a3 ] = 0

#-----------------------------------------------------------------------
# open
#-----------------------------------------------------------------------
def syscall_open( s ):
  filename_ptr = s.rf[ a0 ]
  flags        = s.rf[ a1 ]
  mode         = s.rf[ a2 ]

  # convert flags from solaris to linux (necessary?)
  for newlib, linux in flag_table:
    if flags & newlib:
      flags |= linux

  # get the filename
  filename = s.mem.data[ filename_ptr ]     # TODO: use mem.read()
  while filename[ -1 ] != '\0':
    filename_ptr += 1
    filename += s.mem.data[ filename_ptr ]  # TODO: use mem.read()

  # open vs. os.open():  http://stackoverflow.com/a/15039662
  fd = os.open( filename, flags, mode )

  if fd > 0:
    file_descriptors[ fd ] = fd

  s.rf[ v0 ] = fd
  s.rf[ a3 ] = 0 if fd > 0 else -1

#-----------------------------------------------------------------------
# close
#-----------------------------------------------------------------------
def syscall_close( s ):
  file_ptr = s.rf[ a0 ]

  if file_ptr not in file_descriptors:
    s.rf[ v0 ] = s.rf[ a3 ] = -1
    return

  os.close( file_descriptors[ file_ptr ] )
  del file_descriptors[ file_ptr ]

  s.rf[ v0 ] = s.rf[ a3 ] = 0

#-----------------------------------------------------------------------
# lseek
#-----------------------------------------------------------------------
def syscall_lseek( s ):
  raise Exception('lseek unimplemented!')

#-----------------------------------------------------------------------
# brk
#-----------------------------------------------------------------------
# http://stackoverflow.com/questions/6988487/what-does-brk-system-call-do
def syscall_brk( s ):
  new_brk = s.rf[ a0 ]

  if new_brk != 0:
    s.breakpoint = new_brk

  s.rf[ v0 ] = s.breakpoint
  s.rf[ a3 ] = 0

#-----------------------------------------------------------------------
# numcores
#-----------------------------------------------------------------------
def syscall_numcores( s ):
  # always return 1 until multicore is implemented!
  s.rf[ v0 ] = 1
  s.rf[ a3 ] = 0

#-----------------------------------------------------------------------
# syscall number mapping
#-----------------------------------------------------------------------
syscall_funcs = {
#   0: syscall,       # unimplemented_func
    1: syscall_exit,
    2: syscall_read,
    3: syscall_write,
    4: syscall_open,
    5: syscall_close,
#   6: link,
#   7: unlink,
    8: syscall_lseek,
#   9: fstat,
#  10: stat,
   11: syscall_brk,
 4000: syscall_numcores,

#4001: sendam,
#4002: bthread_once,
#4003: bthread_create,
#4004: bthread_delete,
#4005: bthread_setspecific,
#4006: bthread_getspecific,
#4007: yield,
}

