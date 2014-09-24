#include "arm-macros.h"
TEST_BEGIN

#rotate right by immediate
mov r3, #0x1000000f
mov r4, #0xf1000000
cmp r3, r3, ROR #4

TEST_END
