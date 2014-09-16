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
  0: sys.stdin .fileno(),
  1: sys.stdout.fileno(),
  2: sys.stderr.fileno(),
}

#-----------------------------------------------------------------------
# exit
#-----------------------------------------------------------------------
def syscall_exit( s ):
  exit_code = s.rf[ a0 ]
  print
  print "NUM  INSTS:", s.ncycles
  print "EXIT CODE: %d (1)" % exit_code
  # TODO: this is an okay way to terminate the simulator?
  #       sys.exit(1) is not valid python

  # TODO: it seems like ARM ignores the exit_code when setting the
  #       return status value.  Is this okay?
  s.status = 1

#-----------------------------------------------------------------------
# read
#-----------------------------------------------------------------------
def syscall_read( s ):
  file_ptr = s.rf[ a0 ]
  data_ptr = s.rf[ a1 ]
  nbytes   = s.rf[ a2 ]

  if file_ptr not in file_descriptors:
    s.rf[ v0 ] = -1   # TODO: return a bad file descriptor error (9)?
    return

  fd = file_descriptors[ file_ptr ]

  try:
    data        = os.read( fd, nbytes )
    nbytes_read = len( data )
    errno       = 0
    # Write data to simulated memory
    for i, char in enumerate( data ):
      s.mem.data[ data_ptr+i ] = char

  except OSError as e:
    print "OSError in syscall_read: errno=%d" % e.errno
    nbytes_read = -1
    errno       = e.errno

  s.rf[ v0 ] = nbytes_read

#-----------------------------------------------------------------------
# write
#-----------------------------------------------------------------------
def syscall_write( s ):
  file_ptr = s.rf[ a0 ]
  data_ptr = s.rf[ a1 ]
  nbytes   = s.rf[ a2 ]

  if file_ptr not in file_descriptors:
    s.rf[ v0 ] = -1   # TODO: return a bad file descriptor error (9)?
    return

  fd = file_descriptors[ file_ptr ]

  # TODO: use mem.read()
  assert data_ptr >= 0 and nbytes >= 0
  data = ''.join( s.mem.data[data_ptr:data_ptr+nbytes] )

  try:
    nbytes_written = os.write( fd, data )
    errno          = 0
    # https://docs.python.org/2/library/os.html#os.fsync
    #os.fsync( fd )  # causes 'Invalid argument' error for some reason...

  except OSError as e:
    print "OSError in syscall_write: errno=%d" % e.errno
    nbytes_written = -1
    errno          = e.errno

  s.rf[ v0 ] = nbytes_written

#-----------------------------------------------------------------------
# open
#-----------------------------------------------------------------------
def syscall_open( s ):
  filename_ptr = s.rf[ a0 ]
  flags        = s.rf[ a1 ]
  mode         = s.rf[ a2 ]

  # convert flags from solaris to linux (necessary?)
  open_flags = 0
  for newlib, linux in flag_table:
    if flags & newlib:
      open_flags |= linux

  # get the filename
  filename = s.mem.data[ filename_ptr ]     # TODO: use mem.read()
  while filename[ -1 ] != '\0':
    filename_ptr += 1
    filename += s.mem.data[ filename_ptr ]  # TODO: use mem.read()

  try:
    # open vs. os.open():  http://stackoverflow.com/a/15039662
    fd    = os.open( filename, open_flags, mode )
    errno = 0

  except OSError as e:
    print "OSError in syscall_open: errno=%d" % e.errno
    fd    = -1
    errno = e.errno

  if fd > 0:
    file_descriptors[ fd ] = fd

  s.rf[ v0 ] = fd

#-----------------------------------------------------------------------
# close
#-----------------------------------------------------------------------
def syscall_close( s ):
  file_ptr = s.rf[ a0 ]

  if file_ptr not in file_descriptors:
    s.rf[ v0 ] = -1   # TODO: return a bad file descriptor error (9)?
    return

  # TODO: hacky don't close the file for 0, 1, 2.
  #       gem5 does this, but is there a better way?
  if file_ptr <= 2:
    s.rf[ v0 ] = 0
    return

  try:
    os.close( file_descriptors[ file_ptr ] )
    del file_descriptors[ file_ptr ]
    errno = 0

  except OSError as e:
    print "OSError in syscall_close: errno=%d" % e.errno
    errno = e.errno

  s.rf[ v0 ] = 0 if errno == 0 else -1

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

  # utsname struct is five fields, each 64 chars + 1 null char
  field_nchars = 64 + 1
  struct = [
    'Linux',                             # sysname
    'm5.eecs.umich.edu',                 # nodename
    '3.10.2',                            # release
    '#1 Mon Aug 18 11:32:15 EDT 2003',   # version
    'armv7l',                            # machine
  ]

  mem_addr = s.rf[ a0 ]

  for field in struct:
    assert len(field) < field_nchars

    # TODO: provide char/string block write interface to memory?
    padding = '\0' * (field_nchars - len(field))
    for char in field + padding:
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

syscall_names = {k: v.func_name for (k,v) in syscall_funcs.items()}

def do_syscall( s, syscall_num ):
  if syscall_num not in syscall_funcs:
    print "WARNING: syscall %d not implemented!" % syscall_num,
    return

  # TODO: make prints debug mode only!
  print syscall_num, syscall_names[ syscall_num ],
  syscall_funcs[ syscall_num ]( s )
  print hex(s.rf[ a0 ]),
