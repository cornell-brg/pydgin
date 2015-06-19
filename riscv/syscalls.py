#=========================================================================
# syscalls.py
#=========================================================================

from pydgin.utils import intmask
import pydgin.syscalls as common

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
  SYS_exit           : common.syscall_exit,
  SYS_exit_group     : common.syscall_exit,
  SYS_read           : common.syscall_read,
 #SYS_pread          : common.syscall_pread,
  SYS_write          : common.syscall_write,
  SYS_open           : common.syscall_open,
 #SYS_openat         : common.syscall_openat,
  SYS_close          : common.syscall_close,
  SYS_fstat          : common.syscall_fstat,
  SYS_lseek          : common.syscall_lseek,
  SYS_stat           : common.syscall_stat,
 #SYS_lstat          : common.syscall_lstat,
 #SYS_fstatat        : common.syscall_fstatat,
  SYS_link           : common.syscall_link,
  SYS_unlink         : common.syscall_unlink,
 #SYS_mkdir          : common.syscall_mkdir,
 #SYS_linkat         : common.syscall_linkat,
 #SYS_unlinkat       : common.syscall_unlinkat,
 #SYS_mkdirat        : common.syscall_mkdirat,
 #SYS_getcwd         : common.syscall_getcwd,
  SYS_brk            : common.syscall_brk,
 #SYS_uname          : common.syscall_uname,
 #SYS_getpid         : common.syscall_getpid,
 #SYS_getuid         : common.syscall_getuid,
 #SYS_geteuid        : common.syscall_getuid,
 #SYS_getgid         : common.syscall_getuid,
 #SYS_getegid        : common.syscall_getuid,
 #SYS_mmap           : common.syscall_mmap,
 #SYS_munmap         : common.syscall_munmap,
 #SYS_mremap         : common.syscall_mremap,
 #SYS_mprotect       : common.syscall_mprotect,
 #SYS_rt_sigaction   : common.syscall_rt_sigaction,
 #SYS_time           : common.syscall_time,
 #SYS_gettimeofday   : common.syscall_gettimeofday,
 #SYS_times          : common.syscall_times,
 #SYS_writev         : common.syscall_writev,
 #SYS_access         : common.syscall_access,
 #SYS_faccessat      : common.syscall_faccessat,
 #SYS_fcntl          : common.syscall_fcntl,
 #SYS_getdents       : common.syscall_getdents,
 #SYS_dup            : common.syscall_dup,
 #SYS_readlinkat     : common.syscall_stub_nosys,
 #SYS_rt_sigprocmask : common.syscall_stub_success,
  SYS_ioctl          : common.syscall_ioctl,
}

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


