#include "arm-macros.h"
TEST_BEGIN

#logical shift right by register, Rs[7:0] < 32
mov r3, #0x3f
mov r4, #0x3f0000
mov r5, #0x210
cmp r3, r4, LSR r5

TEST_END
