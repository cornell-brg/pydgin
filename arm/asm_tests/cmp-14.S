#include "arm-macros.h"
TEST_BEGIN

#rotate right by register
mov r3, #0x1000000f
mov r4, #0xf1000000
mov r5, #0x4
cmp r3, r3, ROR r5

TEST_END
