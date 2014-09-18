mov r4, #0xFFFFFFFF
cmp r4, #0

# Terminate the program by calling the exit syscall (1)

mov r7, #1
swi 0x00000000
