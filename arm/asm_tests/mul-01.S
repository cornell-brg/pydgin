#include "arm-macros.h"
TEST_BEGIN

mov r1, #0xf0000000
mov r2, #0
muls r3, r1, r2 // V and C bits won't be affected in any case

TEST_END
