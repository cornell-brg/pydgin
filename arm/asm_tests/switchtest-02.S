//=========================================================================
// switchtest-02.S
//========================================================================
// Tests dependencies through registers when switching

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
mov r0,  r1
mov r1,  r2
mov r2,  r3
mov r3,  r4
mov r4,  r5
mov r5,  r6
mov r6,  r7
mov r7,  r8
mov r8,  r9
mov r9,  r10
mov r10, r11
mov r11, r0
mov r0, r1
mov r1, r2
mov r2, r3
mov r3, r4
mov r4, r5
mov r5, r6
mov r6, r7
mov r7, r8
mov r8, r9
mov r9, r10
mov r10,r11
mov r11,r0
mov r0, r1
mov r1, r2
mov r2, r3
mov r3, r4
mov r4, r5
mov r5, r6
mov r6, r7
mov r7, r8
mov r8, r9
mov r9, r10
mov r10,r11
mov r11,r0

//mov  r0, r1

TEST_END
