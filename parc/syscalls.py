#=======================================================================
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
# - 2 read
# - 3 write
# - 4 open
# - 5 close
# - 8 lseek

from isa import reg_map
import sys
import os

v0 = reg_map['v0']  # return value
a0 = reg_map['a0']  # arg0
a1 = reg_map['a1']  # arg1
a2 = reg_map['a2']  # arg2
a3 = reg_map['a3']  # error

file_descriptors = [
  sys.stdin,
  sys.stderr,
  sys.stdout,
]

#-----------------------------------------------------------------------
# exit
#-----------------------------------------------------------------------
def syscall_exit( s ):
  exit_code = s.rf[ a0 ]
  sys.exit( exit_code )

#-----------------------------------------------------------------------
# read
#-----------------------------------------------------------------------
def syscall_read( s ):
  raise Exception('read unimplemented!')

#-----------------------------------------------------------------------
# write
#-----------------------------------------------------------------------
def syscall_write( s ):
  file_ptr = s.rf[ a0 ]
  data_ptr = s.rf[ a1 ]
  nbytes   = s.rf[ a2 ]

  fd   = file_descriptors[ file_ptr ]
  data = ''.join( s.mem.data[data_ptr:data_ptr+nbytes] )
  x = os.write( file_ptr, data )

#-----------------------------------------------------------------------
# open
#-----------------------------------------------------------------------
def syscall_open( s ):
  raise Exception('open unimplemented!')

#-----------------------------------------------------------------------
# close
#-----------------------------------------------------------------------
def syscall_close( s ):
  file_ptr = s.rf[ a0 ]
  if file_ptr > 2:
    fd = file_descriptors[ file_ptr ]
    fd.close()

#-----------------------------------------------------------------------
# lseek
#-----------------------------------------------------------------------
def syscall_lseek( s ):
  raise Exception('close unimplemented!')

#-----------------------------------------------------------------------
# brk
#-----------------------------------------------------------------------
# http://stackoverflow.com/questions/6988487/what-does-brk-system-call-do
def syscall_brk( s ):

  # gem5 Implementation

  new_brk = s.rf[ a0 ]

  if new_brk != 0:
    # if new_brk > s.break_point: allocate_memory()
    s.break_point = new_brk

  s.rf[ v0 ] = s.break_point
  #print '>>> breakpoint', hex(s.break_point), hex(s.rf.regs[29]), '<<<',

  # Maven Proxy Kernel Implementation
  #
  #kernel_addr = s.rf[ a0 ]
  #user_addr   = s.rf[ a1 ]

  ## first call to brk initializes the breakk_point address (end of heap)
  ## TODO: initialize in pisa-sim::syscall_init()!
  #if s.break_point == 0:
  #  s.break_point = user_addr

  ## if kernel_addr is not null, set a new break_point
  #if kernel_addr != 0:
  #  s.break_point = kernel_addr

  ## return the break_point value
  #s.rf[ v0 ] = s.break_point

#-----------------------------------------------------------------------
# numcores
#-----------------------------------------------------------------------
def syscall_numcores( s ):
  # always return 1 until multicore is implemented!
  s.rf[ v0 ] = 1

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

