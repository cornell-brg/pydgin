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

from isa   import reg_map
from utils import trim_32
import sys
import os
import errno

#-----------------------------------------------------------------------
# os state and helpers
#-----------------------------------------------------------------------

# short names for registers

v0 = reg_map['a1']  # return value
a0 = reg_map['a1']  # arg0
a1 = reg_map['a2']  # arg1
a2 = reg_map['a3']  # arg2
                    # error: not used in arm

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
    s.rf[ v0 ] = -1
    return

  fd   = file_descriptors[ file_ptr ]
  data = os.read( fd, nbytes )

  s.rf[ v0 ] = len( data )   # return the number of bytes read

#-----------------------------------------------------------------------
# write
#-----------------------------------------------------------------------
def syscall_write( s ):
  file_ptr = s.rf[ a0 ]
  data_ptr = s.rf[ a1 ]
  nbytes   = s.rf[ a2 ]

  if file_ptr not in file_descriptors:
    s.rf[ v0 ] = -1
    return

  fd   = file_descriptors[ file_ptr ]

  # TODO: use mem.read()
  assert data_ptr >= 0 and nbytes >= 0
  data = ''.join( s.mem.data[data_ptr:data_ptr+nbytes] )

  nbytes_written = os.write( fd, data )
  # https://docs.python.org/2/library/os.html#os.fsync
  #os.fsync( fd )  # this causes Invalid argument error for some reason...

  s.rf[ v0 ] = nbytes_written

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

#-----------------------------------------------------------------------
# close
#-----------------------------------------------------------------------
def syscall_close( s ):
  file_ptr = s.rf[ a0 ]

  if file_ptr not in file_descriptors:
    s.rf[ v0 ] = -1
    return

  os.close( file_descriptors[ file_ptr ] )
  del file_descriptors[ file_ptr ]

  s.rf[ v0 ] = 0

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

#-----------------------------------------------------------------------
# uname
#-----------------------------------------------------------------------
# TODO: Implementation copied directly from gem5 for verification
# purposes. Fix later.
def syscall_uname( s ):

  # utsname struct is five fields, each 65 chars long (1 char for null):
  # sysname, nodename, release, version, machine
  struct = [
    'Linux',
    'm5.eecs.umich.edu',
    '3.10.2',
    '#1 Mon Aug 18 11:32:15 EDT 2003',
    'armv7l',
  ]

  mem_addr = s.rf[ a0 ]

  for field in struct:
    assert len(field) <= 64

    # TODO: provide char/string block write interface to memory?
    for char in field + '\0'*(65 - len(field)):
      s.mem.data[ mem_addr ] = char
      mem_addr += 1

  s.rf[ v0 ] = 0

#-----------------------------------------------------------------------
# ioctl
#-----------------------------------------------------------------------
def syscall_ioctl( s ):
  fd  = s.rf[ a0 ]
  req = s.rf[ a1 ]

  result     = -errno.ENOTTY if fd >= 0 else -errno.EBADF
  s.rf[ v0 ] = trim_32( result )

#-----------------------------------------------------------------------
# syscall number mapping
#-----------------------------------------------------------------------
syscall_funcs = {
#      NEWLIB
#   0: syscall,       # unimplemented_func
    1: syscall_exit,
    3: syscall_read,
    4: syscall_write,
    5: syscall_open,
    6: syscall_close,

#      GLIBC
   45: syscall_brk,
   54: syscall_ioctl,
  122: syscall_uname,
}

def do_syscall( s, num ):
  result = syscall_funcs[ num ]( s )
  print num, syscall_funcs[ num ].func_name, hex(s.rf[ a0 ])
  return result
