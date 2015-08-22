//========================================================================
// switchtest-03.S
//========================================================================
// Test memory dependencies when switching

#include "arm-macros.h"
TEST_BEGIN

mov r0,  #1
mov r1,  #2
mov r2,  #3
mov r3,  #4
mov r4,  #5
mov r5,  #6
mov r6,  #7
mov r7,  #8
mov r8,  #9
mov r9,  #10
mov r10, #11
mov r11, #12
ldr r12, =foo

str r0,  [r12]
str r1,  [r12, #4]
str r2,  [r12, #8]
str r3,  [r12, #12]
str r4,  [r12, #16]
str r5,  [r12, #20]
str r6,  [r12, #24]
str r7,  [r12, #28]
str r8,  [r12, #32]
str r9,  [r12, #36]
str r10, [r12, #40]
str r11, [r12, #44]

ldr r1,  [r12]
ldr r2,  [r12, #4]
ldr r3,  [r12, #8]
ldr r4,  [r12, #12]
ldr r5,  [r12, #16]
ldr r6,  [r12, #20]
ldr r7,  [r12, #24]
ldr r8,  [r12, #28]
ldr r9,  [r12, #32]
ldr r10, [r12, #36]
ldr r11, [r12, #40]
ldr r0,  [r12, #44]

cmp r1, #1
bne fail
cmp r2, #2
add r0, r0, #0
bne fail
cmp r3, #3
bne fail
cmp r4, #4
bne fail
cmp r5, #5
bne fail
cmp r6, #6
bne fail
add r0, r0, #0
cmp r7, #7
bne fail
cmp r8, #8
bne fail
cmp r9, #9
bne fail
cmp r10,#10
bne fail
add r0, r0, #0
cmp r11,#11
bne fail
cmp r0 ,#12
bne fail

success:
mov r0, #1
b   test_end

fail:
mov r0, #0

test_end:
TEST_END

tdata_0:
//.data:
foo:
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
.word 0x00000000
