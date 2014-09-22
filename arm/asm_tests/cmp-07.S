#include "arm-macros.h"
TEST_BEGIN

#logical shift right by immediate > 0
mov r3, #0x3f0000
mov r4, #0x3f0
cmp r4, r3, LSR #0xC

TEST_END
