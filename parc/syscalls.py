#=======================================================================
# syscalls.py
#=======================================================================
#
# This file defines the syscall numbers and defines the
# architecture-specific calling convention for syscalls.
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

from isa import reg_map
import sys
import os
from pydgin.utils import intmask

#-----------------------------------------------------------------------
# os state and helpers
#-----------------------------------------------------------------------

# short names for registers

v0 = reg_map['v0']  # return value
a0 = reg_map['a0']  # arg0
a1 = reg_map['a1']  # arg1
a2 = reg_map['a2']  # arg2
a3 = reg_map['a3']  # error


#-----------------------------------------------------------------------
# syscall number mapping
#-----------------------------------------------------------------------

import pydgin.syscalls as common

syscall_funcs = {
#   0: syscall,       # unimplemented_func
    1: common.syscall_exit,
    2: common.syscall_read,
    3: common.syscall_write,
    4: common.syscall_open,
    5: common.syscall_close,
    6: common.syscall_link,
    7: common.syscall_unlink,
    8: common.syscall_lseek,
    9: common.syscall_fstat,
   10: common.syscall_stat,
   11: common.syscall_brk,
 4000: common.syscall_numcores,

#4001: sendam,
#4002: bthread_once,
#4003: bthread_create,
#4004: bthread_delete,
#4005: bthread_setspecific,
#4006: bthread_getspecific,
#4007: yield,
}

#-------------------------------------------------------------------------
# do_syscall
#-------------------------------------------------------------------------
# Handle syscall -- use architecture-specific calling convention to
# extract the syscall arguments, get the syscall handling function, do the
# syscall, and return the result back into the architectural state.
def do_syscall( s ):
  syscall_number = s.rf[ v0 ]
  arg0 = intmask( s.rf[ a0 ] )
  arg1 = intmask( s.rf[ a1 ] )
  arg2 = intmask( s.rf[ a2 ] )

  if syscall_number not in syscall_funcs:
    print "WARNING: syscall not implemented: %d" % syscall_number
    # TODO: return an error?
  else:
    syscall_handler = syscall_funcs[ syscall_number ]

    # call the syscall handler and get the return and error values
    retval, errno = syscall_handler( s, arg0, arg1, arg2 )

    if s.debug.enabled( "syscalls" ):
      print " retval=%x errno=%x" % ( retval, errno )

    s.rf[ v0 ] = retval
    s.rf[ a3 ] = errno


