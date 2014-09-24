#include "arm-macros.h"
TEST_BEGIN

#Rotate right with extend, carry = 1
mov r4, #0xFFFFFFFF
cmp r4, #0
mov r3, #0xa000000b
movs r3, r3, RRX

TEST_END
