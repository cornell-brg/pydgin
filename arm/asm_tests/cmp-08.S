#include "arm-macros.h"
TEST_BEGIN

#logical shift right by register, Rs[7:0] == 0
mov r3, #0x3f0000
mov r4, #0x3f0000
mov r5, #0x200
cmp r4, r3, LSR r5

TEST_END
