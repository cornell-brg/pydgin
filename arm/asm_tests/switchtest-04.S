//========================================================================
// switchtest-04.S
//========================================================================
// This test tests for control flags (cpsr) by using comparison and branch
// operations

#include "arm-macros.h"
TEST_BEGIN

// initial values
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

cmp r0, #1
bne fail

cmp r1, #2
bne fail

// add a nop here so that we test the other direction
//add r0, r0, #0

cmp r2, #3
bne fail

cmp r3, #4
bne fail

// add a nop here so that we test the other direction
//add r0, r0, #0

cmp r4, #5
bne fail

cmp r5, #6
bne fail

// add a nop here so that we test the other direction
add r0, r0, #0

cmp r6, #7
bne fail

cmp r7, #8
bne fail

cmp r8, #9
bne fail

cmp r9, #10
bne fail

cmp r10,#11
// add a nop here so that we test the other direction
add r0, r0, #0
bne fail

cmp r11,#12
bne fail

cmp r2, r3
beq fail
bge fail

cmp r4, r3
beq fail
blt fail

adds r4, r4, #0x7ffffffe
bvc fail
bpl fail

adds r3, r3, #0x7fffffff
bvc fail
blt fail

success:
mov r0, #1
b   test_end

fail:
mov r0, #0

test_end:
TEST_END

