#=======================================================================
# syscalls.py
#=======================================================================
# Implementations of emulated syscalls. Call numbers were borrowed from
# the following files:
#
# - https://github.com/cornell-brg/maven-sim-isa/blob/master/common/syscfg.h
# - https://github.com/cornell-brg/pyparc/blob/master/pkernel/pkernel/syscfg.h
# - https://github.com/cornell-brg/maven-sys-xcc/blob/master/src/libgloss/maven/machine/syscfg.h
# - https://github.com/cornell-brg/gem5-mcpat/blob/master/src/arch/mips/linux/process.cc
#
# According to Berkin, only the following syscalls are needed by pbbs:
#
# - 2 read
# - 3 write
# - 4 open
# - 5 close
# - 8 lseek


def syscall_read():
  raise Exception('read unimplemented!')
def syscall_write():
  raise Exception('write unimplemented!')
def syscall_open():
  raise Exception('open unimplemented!')
def syscall_close():
  raise Exception('close unimplemented!')
def syscall_lseek():
  raise Exception('close unimplemented!')
def syscall_numcores():
  return 1

syscall_funcs = {
    2: syscall_read,
    3: syscall_write,
    4: syscall_open,
    5: syscall_close,
    8: syscall_lseek,
 4000: syscall_numcores,
}


# -  0  syscall # unimplementedFunc
# -  1  exit    # exitFunc
# -  2  read    # readFunc
# -  3  write   # writeFunc
# -  4  open    # openFunc<MipsLinux>
# -  5  close   # closeFunc
# -  6  link    #", unimplementedFunc),
# -  7  unlink  #", unlinkFunc),
# -  8  lseek   #", lseekFunc),
# -  9  fstat   #", fstatFunc<MipsLinux>),
# - 10  stat    #",  statFunc<MipsLinux>),
# - 11  break   #", brkFunc),
