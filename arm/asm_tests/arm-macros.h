.macro TEST_BEGIN

  # gcc needs this to create a valid elf
  .global main
  main:

.endm

.macro TEST_END

  # Terminate the program by calling the exit syscall (1)
  mov r7, #1
  swi 0x00000000

  # the pydgin elf loader needs this to find the breakpoint
  .bss
  xxx: .word 0

.endm

