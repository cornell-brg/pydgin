#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x000000ff

ldr r8, =tdata_0
mov r4, #0
mov r5, #0
mov r6, #0
mov r9, #12
add r9, r9, pc
str r9, [r8]
ldr pc, [r8]
mov r4, pc
mov r5, pc
mov r6, pc

TEST_END
