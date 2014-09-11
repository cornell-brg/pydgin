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

v0 = reg_map['v0']  # return value
a0 = reg_map['a0']  # arg0
a1 = reg_map['a1']  # arg1
a2 = reg_map['a2']  # arg2
a3 = reg_map['a3']  # error

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

# NOTE: previously, file descriptors was a dict, and the standard io was
# dup'd to new fds. However, this causes issues with translation. So
# instead, we're directly using fds 0, 1, 2. I don't know if this has any
# adverse effects.
# NOTE2: I had changed this to a list, but rpython translation on lists is
# a little funky on lookups and deletions. Using a dict as a set (just for
# doing "fd in file_descriptors", "del file_descriptors[fd]" and
# "file_descriptors[fd] = fd" so we don't really use the values) is more
# reliable. Note that python Set object is not rpython either.
file_descriptors = { 0: 0, 1: 1, 2: 2 }

# TODO: we want verbosity to be set from outside with a command line flag.
# For the time being, we do it here
#verbose = True
verbose = False

#-------------------------------------------------------------------------
# Stat
#-------------------------------------------------------------------------
# We represent the stat structure of the simulated system here and provide
# utility functions to convert Python stat object to this.

class Stat( object ):

  # these are the fields and sizes in maven stat object (from
  # https://github.com/cornell-brg/maven-sim-isa/blob/master/appsvr/sysargs.h#L39,L59)
  # and https://github.com/cornell-brg/maven-sys-xcc/blob/master/src/newlib/libc/include/sys/stat.h#L25-L51)

  #               sz off
  ST_DEV      = ( 2, 0  )
  ST_INO      = ( 2, 2  )
  ST_MODE     = ( 4, 4  )
  ST_NLINK    = ( 2, 8  )
  ST_UID      = ( 2, 10 )
  ST_GID      = ( 2, 12 )
  ST_RDEV     = ( 2, 14 )
  ST_SIZE     = ( 4, 16 )
  #ST_PAD3     = ( 4, 20 )
  ST_ATIME    = ( 4, 20 )
  ST_SPARE1   = ( 4, 24 )
  ST_MTIME    = ( 4, 28 )
  ST_SPARE2   = ( 4, 32 )
  ST_CTIME    = ( 4, 36 )
  ST_SPARE3   = ( 4, 40 )
  ST_BLKSIZE  = ( 4, 44 )
  ST_BLOCKS   = ( 4, 48 )
  ST_SPARE4   = ( 8, 52 )

  SIZE = 64

  def __init__( self ):
    # we represent this stat object as a character array
    self.buffer = [ "\0" ] * Stat.SIZE

  # given the field tuple which contains the size and offset information,
  # we write the value to the buffer
  def set_field( self, field, val ):
    size, offset = field

    # we copy the value byte by byte to the buffer
    for i in xrange( size ):
      self.buffer[ offset + i ] = chr( 0xff & val )
      val = val >> 8

  # converts and copies the python stat object to the simulated memory
  def copy_stat_to_mem( self, py_stat, mem, addr ):

    # we set the buffer fields one by one. Only copying the fields that
    # are os-independent according to
    # https://docs.python.org/2/library/os.html#os.stat

    self.set_field( Stat.ST_MODE,       py_stat.st_mode    )
    self.set_field( Stat.ST_INO,        py_stat.st_ino     )
    self.set_field( Stat.ST_DEV,        py_stat.st_dev     )
    self.set_field( Stat.ST_NLINK,      py_stat.st_nlink   )
    self.set_field( Stat.ST_UID,        py_stat.st_uid     )
    self.set_field( Stat.ST_GID,        py_stat.st_gid     )
    self.set_field( Stat.ST_SIZE,       py_stat.st_size    )
    # atime, mtime, ctime are floats, so we cast them to int
    self.set_field( Stat.ST_ATIME, int( py_stat.st_atime ) )
    self.set_field( Stat.ST_MTIME, int( py_stat.st_mtime ) )
    self.set_field( Stat.ST_CTIME, int( py_stat.st_ctime ) )

    # now we can copy the buffer

    assert addr >= 0
    mem[ addr : addr + Stat.SIZE ] = self.buffer

#-------------------------------------------------------------------------
# get_str
#-------------------------------------------------------------------------
# gets the python string from a pointer to the simulated memory

def get_str( s, ptr ):
  str = s.mem.data[ ptr ]     # TODO: use mem.read()
  while s.mem.data[ ptr + 1 ] != '\0':
    ptr += 1
    str += s.mem.data[ ptr ]  # TODO: use mem.read()
  return str

#-----------------------------------------------------------------------
# exit
#-----------------------------------------------------------------------
def syscall_exit( s ):
  if verbose:
    print "syscall_exit"

  exit_code = s.rf[ a0 ]
  print
  print "NUM  INSTS:", s.ncycles
  print "STAT INSTS:", s.stat_ncycles
  print "EXIT CODE: ", exit_code
  # TODO: this is an okay way to terminate the simulator?
  #       sys.exit(1) is not valid python
  s.status = exit_code
  s.running = False

#-----------------------------------------------------------------------
# read
#-----------------------------------------------------------------------
def syscall_read( s ):
  if verbose:
    print "syscall_read"

  fd       = s.rf[ a0 ]
  data_ptr = s.rf[ a1 ]
  nbytes   = s.rf[ a2 ]

  if fd not in file_descriptors:
    s.rf[ v0 ] = -1
    # we return a bad file descriptor error (9)
    s.rf[ a3 ] = 9
    return

  errno = 0

  try:
    str = os.read( fd, nbytes )
    nbytes_read = len( str )

    # rpython requires us to use a list of characters instead of string
    data = [ "\0" ] * nbytes_read

    for i in xrange( nbytes_read ):
      data[i] = str[i]

    assert data_ptr >= 0
    s.mem.data[data_ptr : data_ptr + nbytes_read ] = data

  except OSError as e:
    if verbose:
      print "OSError in syscall_read. errno=%d" % e.errno
    nbytes_read = -1
    errno = e.errno

  # return the number of bytes read

  s.rf[ v0 ] = nbytes_read
  s.rf[ a3 ] = errno

#-----------------------------------------------------------------------
# write
#-----------------------------------------------------------------------
def syscall_write( s ):
  if verbose:
    print "syscall_write"

  fd       = s.rf[ a0 ]
  data_ptr = s.rf[ a1 ]
  nbytes   = s.rf[ a2 ]

  if fd not in file_descriptors:
    s.rf[ v0 ] = -1
    # we return a bad file descriptor error (9)
    s.rf[ a3 ] = 9
    return

  # TODO: use mem.read()
  assert data_ptr >= 0 and nbytes >= 0
  data = ''.join( s.mem.data[data_ptr:data_ptr+nbytes] )

  errno = 0

  try:
    nbytes_written = os.write( fd, data )

  except OSError as e:
    print "OSError in syscall_write. errno=%d" % e.errno
    nbytes_written = -1
    errno = e.errno

  # https://docs.python.org/2/library/os.html#os.fsync
  #os.fsync( fd )  # this causes Invalid argument error for some reason...

  s.rf[ v0 ] = nbytes_written
  s.rf[ a3 ] = errno

#-----------------------------------------------------------------------
# open
#-----------------------------------------------------------------------
def syscall_open( s ):
  if verbose:
    print "syscall_open"

  filename_ptr = s.rf[ a0 ]
  flags        = s.rf[ a1 ]
  mode         = s.rf[ a2 ]

  # convert flags from solaris to linux (necessary?)
  py_flags = 0

  for newlib, linux in flag_table:
    if flags & newlib:
      py_flags |= linux

  # get the filename

  filename = get_str( s, filename_ptr )

  errno = 0

  # open vs. os.open():  http://stackoverflow.com/a/15039662

  try:
    # NOTE: pypy (not rpython) complains when mode is used directly that
    # only 32-bit integers could be used as the mode. This seems to work
    # fine translated, but interpretation with pypy fails. Seems like only
    # the lower 9 bits of mode matter anyway, so unsetting the most
    # significant bit to keep pypy happy.
    fd = os.open( filename, py_flags, 0x7fffffff & mode )

  except OSError as e:
    if verbose:
      print "OSError in syscall_open. errno=%d" % e.errno
    fd = -1
    errno = e.errno

  if fd > 0:
    file_descriptors[fd] = fd

  s.rf[ v0 ] = fd
  s.rf[ a3 ] = errno

#-----------------------------------------------------------------------
# close
#-----------------------------------------------------------------------
def syscall_close( s ):
  if verbose:
    print "syscall_close"
  fd = s.rf[ a0 ]

  if fd not in file_descriptors:
    s.rf[ v0 ] = -1
    # we return a bad file descriptor error (9)
    s.rf[ a3 ] = 9
    return

  # hacky: we don't close the file for 0, 1, 2 (note gem5 does the same)
  if fd <= 2:
    s.rf[ v0 ] = s.rf[ a3 ] = 0
    return

  errno = 0

  try:
    os.close( fd )
  except OSError as e:
    if verbose:
      print "OSError in syscall_close. errno=%d" % e.errno
    errno = e.errno

  # remove fd only if the previous op succeeded
  if errno == 0:
    del file_descriptors[fd]

  s.rf[ v0 ] = 0 if errno == 0 else -1
  s.rf[ a3 ] = errno

#-------------------------------------------------------------------------
# link
#-------------------------------------------------------------------------

def syscall_link( s ):
  if verbose:
    print "syscall_link"

  src_ptr  = s.rf[ a0 ]
  link_ptr = s.rf[ a1 ]

  src       = get_str( s, src_ptr )
  link_name = get_str( s, link_ptr )

  errno = 0

  try:
    os.link( src, link_name )

  except OSError as e:
    if verbose:
      print "OSError in syscall_link. errno=%d" % e.errno
    errno = e.errno

  s.rf[ v0 ] = 0 if errno == 0 else -1
  s.rf[ a3 ] = errno

#-------------------------------------------------------------------------
# path
#-------------------------------------------------------------------------

def syscall_unlink( s ):
  if verbose:
    print "syscall_unlink"

  path_ptr  = s.rf[ a0 ]

  path = get_str( s, path_ptr )

  errno = 0

  try:
    os.unlink( path )

  except OSError as e:
    if verbose:
      print "OSError in syscall_unlink. errno=%d" % e.errno
    errno = e.errno

  s.rf[ v0 ] = 0 if errno == 0 else -1
  s.rf[ a3 ] = errno

#-----------------------------------------------------------------------
# lseek
#-----------------------------------------------------------------------
def syscall_lseek( s ):
  if verbose:
    print "syscall_lseek"

  fd  = s.rf[ a0 ]
  pos = s.rf[ a1 ]
  how = s.rf[ a2 ]

  if fd not in file_descriptors:
    s.rf[ v0 ] = -1
    # we return a bad file descriptor error (9)
    s.rf[ a3 ] = 9
    return

  errno = 0

  try:
    os.lseek( fd, pos, how )

  except OSError as e:
    if verbose:
      print "OSError in syscall_lseek. errno=%d" % e.errno
    errno = e.errno

  s.rf[ v0 ] = 0 if errno == 0 else -1
  s.rf[ a3 ] = errno

#-------------------------------------------------------------------------
# fstat
#-------------------------------------------------------------------------

def syscall_fstat( s ):
  if verbose:
    print "syscall_fstat"

  fd       = s.rf[ a0 ]
  buf_ptr  = s.rf[ a1 ]

  if fd not in file_descriptors:
    s.rf[ v0 ] = -1
    # we return a bad file descriptor error (9)
    s.rf[ a3 ] = 9
    return

  errno = 0

  try:
    # we get a python stat object
    py_stat = os.fstat( fd )

    # we construct a new simulated Stat object
    stat = Stat()

    # we convert this and copy it to the memory
    stat.copy_stat_to_mem( py_stat, s.mem.data, buf_ptr )

  except OSError as e:
    if verbose:
      print "OSError in syscall_fstat. errno=%d" % e.errno
    errno = e.errno

  s.rf[ v0 ] = 0 if errno == 0 else -1
  s.rf[ a3 ] = errno


#-------------------------------------------------------------------------
# stat
#-------------------------------------------------------------------------

def syscall_stat( s ):
  if verbose:
    print "syscall_stat"

  path_ptr = s.rf[ a0 ]
  buf_ptr  = s.rf[ a1 ]

  path = get_str( s, path_ptr )

  errno = 0

  try:
    # we get a python stat object
    py_stat = os.stat( path )

    # we construct a new simulated Stat object
    stat = Stat()

    # we convert this and copy it to the memory
    stat.copy_stat_to_mem( py_stat, s.mem.data, buf_ptr )

  except OSError as e:
    if verbose:
      print "OSError in syscall_stat. errno=%d" % e.errno
    errno = e.errno

  s.rf[ v0 ] = 0 if errno == 0 else -1
  s.rf[ a3 ] = errno

#-----------------------------------------------------------------------
# brk
#-----------------------------------------------------------------------
# http://stackoverflow.com/questions/6988487/what-does-brk-system-call-do
def syscall_brk( s ):
  if verbose:
    print "syscall_brk"

  # TODO: this syscall shouldn't be necessary? As far as I know, ctorng
  # added this to add DVFS stuff to multicore

  new_brk = s.rf[ a0 ]

  if new_brk != 0:
    s.breakpoint = new_brk

  s.rf[ v0 ] = s.breakpoint
  s.rf[ a3 ] = 0

#-----------------------------------------------------------------------
# numcores
#-----------------------------------------------------------------------
def syscall_numcores( s ):
  if verbose:
    print "syscall_numcores"
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
    6: syscall_link,
    7: syscall_unlink,
    8: syscall_lseek,
    9: syscall_fstat,
   10: syscall_stat,
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

