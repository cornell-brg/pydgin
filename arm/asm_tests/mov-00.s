# The instruction we are testing, result is in r1

mov r4, #1

# Terminate the program by calling the exit syscall (1)

mov r7, #1
swi 0x00000000
