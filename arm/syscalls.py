#=======================================================================
# syscalls.py
#=======================================================================
#
# Syscall numbers and syscall interface.
#
#  Example ARM syscall:
#
#   // Note that some operating systems use the immediate field of the swi
#   // instruction rather than $r7 to set the syscall number
#
#   move    $r0, #<arg0>
#   move    $r1, #<arg1>
#   move    $r2, #<arg2>
#   move    $r7, #<syscall_num>
#   swi     0x00000000
#
#   // result of syscall stored in $r0
#

from pydgin.misc import FatalError
from isa         import reg_map
from utils       import trim_32
import os
import pydgin.syscalls as cmn_sysc
#import fcntl

#-----------------------------------------------------------------------
# os state and helpers
#-----------------------------------------------------------------------

# short names for registers

v4 = reg_map['v4']  # syscall number
a1 = reg_map['a1']  # arg0 / return value
a2 = reg_map['a2']  # arg1
a3 = reg_map['a3']  # arg2
                    # error: not used in arm

#-------------------------------------------------------------------------
# fstat
#-------------------------------------------------------------------------
def syscall_fstat( s, arg0, arg1, arg2 ):

  fd       = arg0
  buf_ptr  = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_fstat( fd=%x, buf=%x )" % ( fd, buf_ptr ),

  if not cmn_sysc.is_fd_open( s, fd ):
    return -1, cmn_sysc.BAD_FD_ERRNO

  errno = 0

  try:
    # we get a python stat object
    py_stat = os.fstat( fd )

    # we construct a new simulated Stat object
    stat = Stat()

    # we convert this and copy it to the memory
    stat.copy_stat_to_mem( py_stat, s.mem, buf_ptr )

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_fstat. errno=%d" % e.errno
    errno = e.errno

  return 0 if errno == 0 else -1, errno

#-------------------------------------------------------------------------
# fstat64
#-------------------------------------------------------------------------
def syscall_fstat64( s, arg0, arg1, arg2 ):

  fd       = arg0
  buf_ptr  = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_fstat64( fd=%x, buf=%x )" % ( fd, buf_ptr ),

  if not cmn_sysc.is_fd_open( s, fd ):
    return -1, cmn_sysc.BAD_FD_ERRNO

  errno = 0

  try:
    # we get a python stat object
    py_stat = os.fstat( fd )

    # we construct a new simulated Stat object
    stat64 = Stat64()

    # we convert this and copy it to the memory
    stat64.copy_stat_to_mem( py_stat, s.mem, buf_ptr )

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

  path = cmn_sysc.get_str( s, path_ptr )

  if s.debug.enabled( "syscalls" ):
    print "path=%s" % path,

  errno = 0

  try:
    # we get a python stat object
    py_stat = os.stat( path )

    # we construct a new simulated Stat object
    stat = Stat()

    # we convert this and copy it to the memory
    stat.copy_stat_to_mem( py_stat, s.mem, buf_ptr )

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_stat. errno=%d" % e.errno
    errno = e.errno

  return 0 if errno == 0 else -1, errno

#-------------------------------------------------------------------------
# stat64
#-------------------------------------------------------------------------
def syscall_stat64( s, arg0, arg1, arg2 ):

  path_ptr = arg0
  buf_ptr  = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_stat( path=%x, buf=%x )" % ( path_ptr, buf_ptr ),

  path = cmn_sysc.get_str( s, path_ptr )

  if s.debug.enabled( "syscalls" ):
    print "path=%s" % path,

  errno = 0

  try:
    # we get a python stat object
    py_stat = os.stat( path )

    # we construct a new simulated Stat object
    stat64 = Stat64()

    # we convert this and copy it to the memory
    stat64.copy_stat_to_mem( py_stat, s.mem, buf_ptr )

  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_stat. errno=%d" % e.errno
    errno = e.errno

  return 0 if errno == 0 else -1, errno

#-------------------------------------------------------------------------
# fcntl64
#-------------------------------------------------------------------------
def syscall_fcntl64( s, arg0, arg1, arg2 ):

  fd   = arg0
  cmd  = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_fcntl64( fd=%x, cmd=%x )" % ( fd, cmd ),

  errno = 0
  ret = -1

  #try:
  #  ret = fcntl.fcntl( fd, cmd )

  #except IOError as e:
  #  if s.debug.enabled( "syscalls" ):
  #    print "IOError in syscall_fcntl64. errno=%d" % e.errno
  #  errno = e.errno

  # TODO: this is fake!!!
  ret = 0x8001

  return ret, errno

#-----------------------------------------------------------------------
# mmap
#-----------------------------------------------------------------------
def syscall_mmap( s, arg0, arg1, arg2 ):
  # TODO: we currently use first two args only
  req_addr = arg0
  req_len  = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_mmap( addr=%x, len=%x )" % ( req_addr, req_len ),

  # assign a new address using the mmap_boundary. TODO: we iginore the
  # requested address

  addr = s.mmap_boundary - req_len
  s.mmap_boundary = addr

  return trim_32( addr ), 0

#-------------------------------------------------------------------------
# getcwd
#-------------------------------------------------------------------------
def syscall_getcwd( s, arg0, arg1, arg2 ):
  ptr = arg0
  len = arg1

  if s.debug.enabled( "syscalls" ):
    print "syscall_getcwd( ptr=%x, len=%x )" % ( ptr, len ),

  errno = 0

  try:
    cwd = os.getcwd()
    # append a null character
    cwd = cwd + "\0"
    #cwd = "/work/bits0/bi45/vc/hg-misc/pypy-cross/pypy/goal/\0"
    cmn_sysc.put_str( s, ptr, cwd )
  except OSError as e:
    if s.debug.enabled( "syscalls" ):
      print "OSError in syscall_stat. errno=%d" % e.errno
    errno = e.errno

  return ptr if errno == 0 else 0, errno

#-----------------------------------------------------------------------
# ignore
#-----------------------------------------------------------------------
# ignore the syscall without warning
def syscall_ignore( s, arg0, arg1, arg2 ):

  if s.debug.enabled( "syscalls" ):
    syscall_number = s.rf[ v4 ]
    print "syscall_ignore( syscall=%d, arg0=%x, arg1=%x, arg2=%x )" % \
          ( syscall_number, arg0, arg1, arg2 ),

  # return success

  return 0, 0

#-------------------------------------------------------------------------
# Stat
#-------------------------------------------------------------------------
# We represent the stat structure of the simulated system here and provide
# utility functions to convert Python stat object to this.
class Stat( object ):

  # assuming the newlib style stat datastructure
  # https://github.com/cornell-brg/maven-sim-isa/blob/master/appsvr/sysargs.h#L39,L59)
  # and https://github.com/cornell-brg/maven-sys-xcc/blob/master/src/newlib/libc/include/sys/stat.h#L25-L51)

  #               sz off
  ST_DEV      = ( 4, 0  )
  ST_INO      = ( 4, 4  )
  ST_MODE     = ( 2, 8  )
  ST_NLINK    = ( 2, 10 )
  ST_UID      = ( 2, 12 )
  ST_GID      = ( 2, 14 )
  ST_SIZE     = ( 4, 20 )
  ST_ATIME    = ( 4, 32 )
  ST_MTIME    = ( 4, 40 )
  ST_CTIME    = ( 4, 48 )

  ST_RDEV     = ( 4, 16 )
  ST_BLKSIZE  = ( 4, 24 )
  ST_BLOCKS   = ( 4, 28 )

  # Alternatively:
  # gem5 ARM:
  # https://github.com/cornell-brg/gem5-mcpat/blob/master/src/arch/arm/linux/linux.hh#L118-L135
  # gem5 Linux:
  # https://github.com/cornell-brg/gem5-mcpat/blob/master/src/kern/linux/linux.hh#L72-L89

  SIZE = 64

  def __init__( self ):
    # we represent this stat object as a character array
    self.buffer = [ "\0" ] * self.SIZE

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

    #print "st_mode    %s" % hex( py_stat.st_mode  )
    #print "st_ino     %s" % hex( py_stat.st_ino   )
    #print "st_dev     %s" % hex( py_stat.st_dev   )
    #print "st_nlink   %s" % hex( py_stat.st_nlink )
    #print "st_uid     %s" % hex( py_stat.st_uid   )
    #print "st_gid     %s" % hex( py_stat.st_gid   )
    #print "st_size    %s" % hex( py_stat.st_size  )
    #print "st_rdev    %s" % hex( py_stat.st_rdev  )
    #print "st_blksize %s" % hex( py_stat.st_blksize )
    #print "st_blocks  %s" % hex( py_stat.st_blocks  )
    #print "st_atime   %s" % hex( int( py_stat.st_atime ) )
    #print "st_mtime   %s" % hex( int( py_stat.st_mtime ) )
    #print "st_ctime   %s" % hex( int( py_stat.st_ctime ) )

    self.set_field( self.ST_MODE,       py_stat.st_mode    )
    self.set_field( self.ST_INO,        py_stat.st_ino     )
    self.set_field( self.ST_DEV,        py_stat.st_dev     )
    self.set_field( self.ST_NLINK,      py_stat.st_nlink   )
    self.set_field( self.ST_UID,        py_stat.st_uid     )
    self.set_field( self.ST_GID,        py_stat.st_gid     )
    self.set_field( self.ST_SIZE,       py_stat.st_size    )

    self.set_field( self.ST_RDEV,       py_stat.st_rdev    )
    self.set_field( self.ST_BLKSIZE,    py_stat.st_blksize )
    self.set_field( self.ST_BLOCKS,     py_stat.st_blocks  )

    # atime, mtime, ctime are floats, so we cast them to int
    self.set_field( self.ST_ATIME, int( py_stat.st_atime ) )
    self.set_field( self.ST_MTIME, int( py_stat.st_mtime ) )
    self.set_field( self.ST_CTIME, int( py_stat.st_ctime ) )

    # now we can copy the buffer

    # TODO: this could be more efficient
    assert addr >= 0
    for i in xrange( self.SIZE ):
      mem.write( addr + i, 1, ord( self.buffer[i] ) )

class Stat64( Stat ):

  ST_DEV      = ( 8, 0x0  )
  ST_INO      = ( 4, 0xc  )
  #ST_INO      = ( 8, 0x50  )
  ST_MODE     = ( 4, 0x10 )
  ST_NLINK    = ( 4, 0x14 )
  ST_UID      = ( 4, 0x18 )
  ST_GID      = ( 4, 0x1c )

  ST_RDEV     = ( 8, 0x20 )

  ST_SIZE     = ( 8, 0x30 )
  ST_BLKSIZE  = ( 4, 0x38 )
  ST_BLOCKS   = ( 4, 0x40 )
  ST_ATIME    = ( 4, 0x48 )
  ST_MTIME    = ( 4, 0x50 )
  ST_CTIME    = ( 4, 0x58 )

  SIZE = 0x68

#-----------------------------------------------------------------------
# syscall number mapping
#-----------------------------------------------------------------------

syscall_funcs = {
#      NEWLIB
#   0: syscall,       # unimplemented_func
    1: cmn_sysc.syscall_exit,
    3: cmn_sysc.syscall_read,
    4: cmn_sysc.syscall_write,
    5: cmn_sysc.syscall_open,
    6: cmn_sysc.syscall_close,
    9: cmn_sysc.syscall_link,
   10: cmn_sysc.syscall_unlink,

#      UCLIBC/GLIBS
#      see: https://github.com/qemu/qemu/blob/master/linux-user/arm/syscall_nr.h
   19: cmn_sysc.syscall_lseek,
   45: cmn_sysc.syscall_brk,
   54: cmn_sysc.syscall_ioctl,
# using local defs for stat and fstat
  106: syscall_stat,
  108: syscall_fstat,
# 106: cmn_sysc.syscall_stat,
# 108: cmn_sysc.syscall_fstat,
# 122: cmn_sysc.syscall_uname,

#  mmap stuff: note that 192 is in reality mmap2, but we map both mmap and
#  mmap2 to the same implementation
   90: syscall_mmap,
  192: syscall_mmap,

  195: syscall_stat64,
  196: syscall_stat64,
  197: syscall_fstat64,

  183: syscall_getcwd,

  221: syscall_fcntl64,


# the remaining should be ignored for now -- used by pypy
   33:  syscall_ignore,
   55:  syscall_ignore,
   78:  syscall_ignore,
   91:  syscall_ignore,
  122:  syscall_ignore,
  140:  syscall_ignore,
  174:  syscall_ignore,
  175:  syscall_ignore,
  191:  syscall_ignore,
  199:  syscall_ignore,
  200:  syscall_ignore,
  201:  syscall_ignore,
  202:  syscall_ignore,
  217:  syscall_ignore,
  263:  syscall_ignore,
  472:  syscall_ignore,
983042: syscall_ignore,
}

#-------------------------------------------------------------------------
# do_syscall
#-------------------------------------------------------------------------
# Handle syscall -- use architecture-specific calling convention to
# extract the syscall arguments, get the syscall handling function, do the
# syscall, and return the result back into the architectural state.
def do_syscall( s ):
  syscall_number = s.rf[ v4 ]
  arg0 = s.rf[ a1 ]
  arg1 = s.rf[ a2 ]
  arg2 = s.rf[ a3 ]

  if syscall_number not in syscall_funcs:
    if syscall_number == 20:
      # fake getpid impl
      print "Warning: getpid = 3000"
      s.rf[ a1 ] = 3000
    else:
      print ( "Warning: syscall %d not implemented! (cyc: %d pc: %s)\n" + \
              "(%s %s %s %s)" ) % \
            ( syscall_number, s.ncycles, hex( s.pc ), hex(s.rf[0]), hex(s.rf[1]),
              hex(s.rf[2]), hex(s.rf[3]) )

      if syscall_number == 195 or syscall_number == 183 or syscall_number == 196:
        filename = cmn_sysc.get_str( s, s.rf[0] )
        print "ignored syscall %d filename %s" % (syscall_number, filename)

      # returning success
      s.rf[ a1 ] = 0

  else:
    syscall_handler = syscall_funcs[ syscall_number ]

    # call the syscall handler and get the return and error values
    retval, errno = syscall_handler( s, arg0, arg1, arg2 )

    if s.debug.enabled( "syscalls" ):
      print " retval=%x errno=%x" % ( retval, errno )

    s.rf[ a1 ] = trim_32( retval )
    # TODO: arm seems to ignore the errno?
    #s.rf[ a3 ] = errno

