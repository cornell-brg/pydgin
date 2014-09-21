#include "arm-macros.h"
TEST_BEGIN

#logical shift left by immediate
mov r4, #0x3f0
mov r3, #0x7e
cmp r4, r3, LSL #0x3

TEST_END
