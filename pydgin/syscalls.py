#=======================================================================
# syscalls.py
#=======================================================================
#
# Implementations of emulated syscalls. NOTE: the following note is mostly
# PARC-specific. Might not be applicable to architectures.
#
# Call numbers were borrowed from the following files:
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

import sys
import os

try:
  from rpython.rtyper.lltypesystem import lltype
  from rpython.rtyper.lltypesystem import rffi
  use_rpython = True
except ImportError:
  use_rpython = False

#-----------------------------------------------------------------------
# os state and helpers
#-----------------------------------------------------------------------

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

# some common error values
BAD_FD_ERRNO = 9

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

    # TODO: this could be more efficient
    assert addr >= 0
    for i in xrange( Stat.SIZE ):
      mem.write( addr + i, 1, ord( self.buffer[i] ) )

#-------------------------------------------------------------------------
# get_str
#-------------------------------------------------------------------------
# gets the python string from a pointer to the simulated memory. If nchars
# is not provided, reads until a null character.

def get_str( s, ptr, nchars=0 ):
  # more efficient string building for large strings
  if use_rpython and nchars > 1000:
    char_arr = lltype.malloc( rffi.CArray( lltype.Char ),
                              nchars, flavor="raw" )

    for i in xrange( nchars ):
      char_arr[i] = chr( s.mem.read( ptr + i, 1 ) )

    # convert to string, free the char array and return the string
    str = rffi.charpsize2str( char_arr, nchars )
    lltype.free( char_arr, flavor="raw" )
    return str

  # the following is the naive and slow implementation
  str = ""
  if nchars > 0:
    for i in xrange( nchars ):
      str += chr( s.mem.read( ptr + i, 1 ) )
  else:
    while s.mem.read( ptr, 1 ) != 0:
      str += chr( s.mem.read( ptr, 1 ) )
      ptr += 1
  return str

#-------------------------------------------------------------------------
# put_str
#-------------------------------------------------------------------------
# puts python string to simulated memory -- note that no null character is
# added to the end

def put_str( s, ptr, str ):
  for c in str:
    s.mem.write( ptr, 1, ord( c ) )
    ptr += 1

#-------------------------------------------------------------------------
# is_fd_open
#-------------------------------------------------------------------------
# checks if the fd is in the open file descriptors, returns True on
# failure

def is_fd_open( s, fd ):
  if fd not in file_descriptors:
    if s.debug.enabled( "syscalls" ):
      print ( "Could not find fd=%d in open file_descriptors, " % fd ) + \
            "returning errno=9"
    return False

  return True

#-----------------------------------------------------------------------
# exit
#-----------------------------------------------------------------------
def syscall_exit( s, arg0, arg1, arg2 ):

  exit_code = arg0

  if s.debug.enabled( "syscalls" ):
    print "syscall_exit( status=%x )" % exit_code

  s.status = exit_code
  s.running = False

  #      ret_val    errno
  return exit_code, 0

#-----------------------------------------------------------------------
# read
#-----------------------------------------------------------------------
def syscall_read( s, arg0, arg1, arg2 ):

  fd       = arg0
  data_ptr = arg1
  nbytes   = arg2

  if s.debug.enabled( "syscalls" ):
    print "syscall_read( fd=%x, buf=%x, count=%x )" % \
          ( fd, data_ptr, nbytes ),

  if not is_fd_open( s, fd ):
    return -1, BAD_FD_ERRNO

  try:
    str = os.read( fd, nbytes )
    nbytes_read = len( str )

    put_str( s, data_ptr, str )

    errno = 0

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_read. errno=%d" % e.errno
    nbytes_read = -1
    errno = e.errno

  # return the number of bytes read
  return nbytes_read, errno

#-----------------------------------------------------------------------
# write
#-----------------------------------------------------------------------
def syscall_write( s, arg0, arg1, arg2 ):

  fd       = arg0
  data_ptr = arg1
  nbytes   = arg2

  if s.debug.enabled( "syscalls" ):
    print "syscall_write( fd=%x, buf=%x, count=%x )" % \
          ( fd, data_ptr, nbytes ),

  if not is_fd_open( s, fd ):
    return -1, BAD_FD_ERRNO

  data = get_str( s, data_ptr, nbytes )

  try:
    nbytes_written = os.write( fd, data )
    errno = 0

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_write. errno=%d" % e.errno
    nbytes_written = -1
    errno = e.errno

  # https://docs.python.org/2/library/os.html#os.fsync
  #os.fsync( fd )  # this causes Invalid argument error for some reason...

  return nbytes_written, errno

#-----------------------------------------------------------------------
# open
#-----------------------------------------------------------------------
def syscall_open( s, arg0, arg1, arg2 ):
  if s.debug.enabled( "syscalls" ):
    print "syscall_open"

  filename_ptr = arg0
  flags        = arg1
  mode         = arg2

  if s.debug.enabled( "syscalls" ):
    print "syscall_open( filename=%x, flags=%x, mode=%x )" % \
          ( filename_ptr, flags, mode ),

  # convert flags from solaris to linux (necessary?)
  open_flags = 0

  for newlib, linux in flag_table:
    if flags & newlib:
      open_flags |= linux

  # get the filename

  filename = get_str( s, filename_ptr )

  # open vs. os.open():  http://stackoverflow.com/a/15039662

  try:
    # NOTE: pypy (not rpython) complains when mode is used directly that
    # only 32-bit integers could be used as the mode. This seems to work
    # fine translated, but interpretation with pypy fails. Seems like only
    # the lower 9 bits of mode matter anyway, so unsetting the most
    # significant bit to keep pypy happy.
    fd = os.open( filename, open_flags, 0x7fffffff & mode )
    errno = 0

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_open. errno=%d" % e.errno
    fd = -1
    errno = e.errno

  if fd > 0:
    file_descriptors[fd] = fd

  return fd, errno

#-----------------------------------------------------------------------
# close
#-----------------------------------------------------------------------
def syscall_close( s, arg0, arg1, arg2 ):
  fd = arg0

  if s.debug.enabled( "syscalls" ):
    print "syscall_close( fd=%x )" % fd,

  if not is_fd_open( s, fd ):
    return -1, BAD_FD_ERRNO

  # hacky: we don't close the file for 0, 1, 2 (note gem5 does the same)

  if fd <= 2:
    return 0, 0

  try:
    os.close( fd )
    errno = 0
  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_close. errno=%d" % e.errno
    errno = e.errno

  # remove fd only if the previous op succeeded
  if errno == 0:
    del file_descriptors[fd]

  return 0 if errno == 0 else -1, errno

#-------------------------------------------------------------------------
# link
#-------------------------------------------------------------------------

def syscall_link( s, arg0, arg1, arg2 ):

  src_ptr  = arg0
  link_ptr = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_link( src=%x, link=%x )" % \
          ( src_ptr, link_ptr ),

  src       = get_str( s, src_ptr )
  link_name = get_str( s, link_ptr )

  try:
    os.link( src, link_name )
    errno = 0

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_link. errno=%d" % e.errno
    errno = e.errno

  return 0 if errno == 0 else -1, errno

#-------------------------------------------------------------------------
# path
#-------------------------------------------------------------------------

def syscall_unlink( s, arg0, arg1, arg2 ):

  path_ptr  = arg0

  if s.debug.enabled( "syscalls" ):
    print "syscall_unlink( path=%x )" % path_ptr,

  path = get_str( s, path_ptr )


  try:
    os.unlink( path )
    errno = 0

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_unlink. errno=%d" % e.errno
    errno = e.errno

  return 0 if errno == 0 else -1, errno

#-----------------------------------------------------------------------
# lseek
#-----------------------------------------------------------------------

def syscall_lseek( s, arg0, arg1, arg2 ):

  fd  = arg0
  pos = arg1
  how = arg2

  if s.debug.enabled( "syscalls" ):
    print "syscall_lseek( fd=%x, pos=%x, how=%x )" % ( fd, pos, how ),

  if not is_fd_open( s, fd ):
    return -1, BAD_FD_ERRNO

  try:
    # NOTE: rpython gives some weird errors in rtyping stage if we don't
    # explicitly cast the return value of os.lseek to int

    new_pos = int( os.lseek( fd, pos, how ) )
    errno = 0

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_lseek. errno=%d" % e.errno
    errno = e.errno
    new_pos = -1

  return new_pos, errno

#-------------------------------------------------------------------------
# fstat
#-------------------------------------------------------------------------

def syscall_fstat( s, arg0, arg1, arg2 ):

  fd       = arg0
  buf_ptr  = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_fstat( fd=%x, buf=%x )" % ( fd, buf_ptr ),

  if not is_fd_open( s, fd ):
    return -1, BAD_FD_ERRNO

  try:
    # we get a python stat object
    py_stat = os.fstat( fd )

    # we construct a new simulated Stat object
    stat = Stat()

    # we convert this and copy it to the memory
    stat.copy_stat_to_mem( py_stat, s.mem, buf_ptr )

    errno = 0

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_fstat. errno=%d" % e.errno
    errno = e.errno

  return 0 if errno == 0 else -1, errno

#-------------------------------------------------------------------------
# stat
#-------------------------------------------------------------------------

def syscall_stat( s, arg0, arg1, arg2 ):

  path_ptr = arg0
  buf_ptr  = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_stat( path=%x, buf=%x )" % ( path_ptr, buf_ptr ),

  path = get_str( s, path_ptr )

  try:
    # we get a python stat object
    py_stat = os.stat( path )

    # we construct a new simulated Stat object
    stat = Stat()

    # we convert this and copy it to the memory
    stat.copy_stat_to_mem( py_stat, s.mem, buf_ptr )

    errno = 0

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_stat. errno=%d" % e.errno
    errno = e.errno

  return 0 if errno == 0 else -1, errno

#-----------------------------------------------------------------------
# brk
#-----------------------------------------------------------------------
# http://stackoverflow.com/questions/6988487/what-does-brk-system-call-do
def syscall_brk( s, arg0, arg1, arg2 ):

  new_brk = arg0

  if s.debug.enabled( "syscalls" ):
    print "syscall_brk( addr=%x )" % new_brk,

  if new_brk != 0:
    s.breakpoint = new_brk

  return s.breakpoint, 0

#-----------------------------------------------------------------------
# numcores
#-----------------------------------------------------------------------
def syscall_numcores( s, arg0, arg1, arg2 ):
  if s.debug.enabled( "syscalls" ):
    print "syscall_numcores()",
  # always return 1 until multicore is implemented!
  return 1, 0

#-----------------------------------------------------------------------
# uname
#-----------------------------------------------------------------------
# TODO: Implementation copied directly from gem5 for verification
# purposes. Fix later.
def syscall_uname( s, arg0, arg1, arg2 ):

  if s.debug.enabled( "syscalls" ):
    print "syscall_uname()",

  # utsname struct is five fields, each 64 chars + 1 null char
  field_nchars = 64 + 1
  struct = [
    'Linux',                             # sysname
    'm5.eecs.umich.edu',                 # nodename
    '3.12.2',                            # release
    '#1 Mon Aug 18 11:32:15 EDT 2003',   # version
    'armv7l',                            # machine
  ]

  mem_addr = arg0

  for field in struct:
    assert len(field) < field_nchars

    # TODO: provide char/string block write interface to memory?
    padding = '\0' * (field_nchars - len(field))
    put_str( s, mem_addr, field + padding )
    mem_addr += field_nchars

  return 0, 0

#-----------------------------------------------------------------------
# ioctl
#-----------------------------------------------------------------------

import errno

def syscall_ioctl( s, arg0, arg1, arg2 ):
  fd  = arg0
  req = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_ioctl( fd=%x, req=%x )" % ( fd, req ),

  # TODO: not sure what this does... return errno 0
  result     = -errno.ENOTTY if fd >= 0 else -errno.EBADF
  return result, 0

