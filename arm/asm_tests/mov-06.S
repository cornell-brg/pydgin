#include "arm-macros.h"
TEST_BEGIN

#Rotate right with extend, carry = 0
mov r3, #0xa000000b
movs r3, r3, RRX

TEST_END
