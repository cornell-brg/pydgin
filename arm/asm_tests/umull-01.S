#include "arm-macros.h"
TEST_BEGIN

mov r1, #0x80000000
mov r2, #2
umulls r3, r4, r1, r2 

TEST_END
