#include "arm-macros.h"
TEST_BEGIN

tdata_0: .word 0x0F0F0F0F

ldr r4, =tdata_0
mov r5, #1
cmp r5, #1
ldreqb r5, [r4, #0]

TEST_END
