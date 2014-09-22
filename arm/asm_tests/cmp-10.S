#include "arm-macros.h"
TEST_BEGIN

#logical shift right by register, Rs[7:0] >= 32 (shifter_operand == 0)
mov r3, #0x0
mov r4, #0x3f0000
mov r5, #0x220
cmp r3, r3, LSR r5

TEST_END
