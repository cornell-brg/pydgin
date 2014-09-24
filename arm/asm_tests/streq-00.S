#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x000000ff

ldr r4, =tdata_0
mov r5, #1
cmp r5, #1
str r5, [r4]
ldr r6, [r4]

TEST_END
