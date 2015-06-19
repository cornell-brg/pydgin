#=========================================================================
# syscalls.py
#=========================================================================

from pydgin.utils import intmask
import pydgin.syscalls as cmn_sysc

SYS_exit = 93
SYS_exit_group = 94
SYS_getpid = 172
SYS_kill = 129
SYS_read = 63
SYS_write = 64
SYS_open = 1024
SYS_openat = 56
SYS_close = 57
SYS_lseek = 62
SYS_brk = 214
SYS_link = 1025
SYS_unlink = 1026
SYS_mkdir = 1030
SYS_linkat = 37
SYS_unlinkat = 35
SYS_mkdirat = 34
SYS_chdir = 49
SYS_getcwd = 17
SYS_stat = 1038
SYS_fstat = 80
SYS_lstat = 1039
SYS_fstatat = 79
SYS_access = 1033
SYS_faccessat = 48
SYS_pread = 67
SYS_pwrite = 68
SYS_uname = 160
SYS_getuid = 174
SYS_geteuid = 175
SYS_getgid = 176
SYS_getegid = 177
SYS_mmap = 222
SYS_munmap = 215
SYS_mremap = 216
SYS_mprotect = 226
SYS_time = 1062
SYS_getmainvars = 2011
SYS_rt_sigaction = 134
SYS_writev = 66
SYS_gettimeofday = 169
SYS_times = 153
SYS_fcntl = 25
SYS_getdents = 61
SYS_dup = 23
SYS_readlinkat = 78
SYS_rt_sigprocmask = 135
SYS_ioctl = 29

syscall_funcs = {
  SYS_exit           : cmn_sysc.syscall_exit,
  SYS_exit_group     : cmn_sysc.syscall_exit,
  SYS_read           : cmn_sysc.syscall_read,
 #SYS_pread          : cmn_sysc.syscall_pread,
  SYS_write          : cmn_sysc.syscall_write,
  SYS_open           : cmn_sysc.syscall_open,
 #SYS_openat         : cmn_sysc.syscall_openat,
  SYS_close          : cmn_sysc.syscall_close,
  SYS_fstat          : cmn_sysc.syscall_fstat,
  SYS_lseek          : cmn_sysc.syscall_lseek,
  SYS_stat           : cmn_sysc.syscall_stat,
 #SYS_lstat          : cmn_sysc.syscall_lstat,
 #SYS_fstatat        : cmn_sysc.syscall_fstatat,
  SYS_link           : cmn_sysc.syscall_link,
  SYS_unlink         : cmn_sysc.syscall_unlink,
 #SYS_mkdir          : cmn_sysc.syscall_mkdir,
 #SYS_linkat         : cmn_sysc.syscall_linkat,
 #SYS_unlinkat       : cmn_sysc.syscall_unlinkat,
 #SYS_mkdirat        : cmn_sysc.syscall_mkdirat,
 #SYS_getcwd         : cmn_sysc.syscall_getcwd,
  SYS_brk            : cmn_sysc.syscall_brk,
 #SYS_uname          : cmn_sysc.syscall_uname,
 #SYS_getpid         : cmn_sysc.syscall_getpid,
 #SYS_getuid         : cmn_sysc.syscall_getuid,
 #SYS_geteuid        : cmn_sysc.syscall_getuid,
 #SYS_getgid         : cmn_sysc.syscall_getuid,
 #SYS_getegid        : cmn_sysc.syscall_getuid,
 #SYS_mmap           : cmn_sysc.syscall_mmap,
 #SYS_munmap         : cmn_sysc.syscall_munmap,
 #SYS_mremap         : cmn_sysc.syscall_mremap,
 #SYS_mprotect       : cmn_sysc.syscall_mprotect,
 #SYS_rt_sigaction   : cmn_sysc.syscall_rt_sigaction,
 #SYS_time           : cmn_sysc.syscall_time,
 #SYS_gettimeofday   : cmn_sysc.syscall_gettimeofday,
 #SYS_times          : cmn_sysc.syscall_times,
 #SYS_writev         : cmn_sysc.syscall_writev,
 #SYS_access         : cmn_sysc.syscall_access,
 #SYS_faccessat      : cmn_sysc.syscall_faccessat,
 #SYS_fcntl          : cmn_sysc.syscall_fcntl,
 #SYS_getdents       : cmn_sysc.syscall_getdents,
 #SYS_dup            : cmn_sysc.syscall_dup,
 #SYS_readlinkat     : cmn_sysc.syscall_stub_nosys,
 #SYS_rt_sigprocmask : cmn_sysc.syscall_stub_success,
  SYS_ioctl          : cmn_sysc.syscall_ioctl,
}

# override stat fields.
# XXX: we need a better way to do this
#                             sz off
cmn_sysc.Stat.ST_DEV      = ( 8, 0  )
cmn_sysc.Stat.ST_INO      = ( 8, 8  )
cmn_sysc.Stat.ST_MODE     = ( 4, 16 )
cmn_sysc.Stat.ST_NLINK    = ( 4, 20 )
cmn_sysc.Stat.ST_UID      = ( 4, 24 )
cmn_sysc.Stat.ST_GID      = ( 4, 28 )
cmn_sysc.Stat.ST_RDEV     = ( 8, 32 )
#             pad1 (64b)
cmn_sysc.Stat.ST_SIZE     = ( 8, 48 )
cmn_sysc.Stat.ST_BLKSIZE  = ( 4, 56 )
#             pad2 (32b)
cmn_sysc.Stat.ST_BLOCKS   = ( 8, 64 )
cmn_sysc.Stat.ST_ATIME    = ( 8, 72 )
#             pad3 (64b)
cmn_sysc.Stat.ST_MTIME    = ( 8, 88 )
#             pad4 (64b)
cmn_sysc.Stat.ST_CTIME    = ( 8, 104)
#             pad5 (64b)
#             unused4 (32b)
#             unused5 (32b)

cmn_sysc.Stat.SIZE = 128

#-------------------------------------------------------------------------
# do_syscall
#-------------------------------------------------------------------------

def do_syscall( s ):
  syscall_number = s.rf[17]
  arg0 = intmask( s.rf[10] )
  arg1 = intmask( s.rf[11] )
  arg2 = intmask( s.rf[12] )
  # TODO: riscv supports 6 syscall args, disabling higher args for the time
  # being
  #arg3 = s.rf[13]
  #arg4 = s.rf[14]
  #arg5 = s.rf[15]

  if syscall_number not in syscall_funcs:
    print "WARNING: syscall not implemented: %d" % syscall_number
  else:
    syscall_handler = syscall_funcs[ syscall_number ]

    retval, errno = syscall_handler( s, arg0, arg1, arg2 )

    if s.debug.enabled( "syscalls" ):
      print " retval=%x errno=%x" % ( retval, errno )

    s.rf[ 10 ] = retval
    # TODO: can't return the errno?


