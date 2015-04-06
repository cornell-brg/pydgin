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

#-----------------------------------------------------------------------
# os state and helpers
#-----------------------------------------------------------------------

# short names for registers

v4 = reg_map['v4']  # syscall number
a1 = reg_map['a1']  # arg0 / return value
a2 = reg_map['a2']  # arg1
a3 = reg_map['a3']  # arg2
                    # error: not used in arm

#-----------------------------------------------------------------------
# syscall number mapping
#-----------------------------------------------------------------------

import pydgin.syscalls as common

syscall_funcs = {
#      NEWLIB
#   0: syscall,       # unimplemented_func
    1: common.syscall_exit,
    3: common.syscall_read,
    4: common.syscall_write,
    5: common.syscall_open,
    6: common.syscall_close,
    9: common.syscall_link,
   10: common.syscall_unlink,

#      UCLIBC/GLIBS
#      see: https://github.com/qemu/qemu/blob/master/linux-user/arm/syscall_nr.h
   19: common.syscall_lseek,
   45: common.syscall_brk,
   54: common.syscall_ioctl,
  106: common.syscall_stat,
  108: common.syscall_fstat,
# 122: common.syscall_uname,
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
    print "WARNING: syscall not implemented: %d" % syscall_number
    # TODO: return an error?
  else:
    syscall_handler = syscall_funcs[ syscall_number ]

    # call the syscall handler and get the return and error values
    retval, errno = syscall_handler( s, arg0, arg1, arg2 )

    if s.debug.enabled( "syscalls" ):
      print " retval=%x errno=%x" % ( retval, errno )

    s.rf[ a1 ] = trim_32( retval )
    # TODO: arm seems to ignore the errno?
    #s.rf[ a3 ] = errno

