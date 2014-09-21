#include "arm-macros.h"
TEST_BEGIN

#logical shift left by register, Rs[7:0] >= 32 (shifter_operand = 0)
mov r4, #0x0
mov r3, #0x3f0
mov r2, #0xff
cmp r4, r3, LSL r2

TEST_END
