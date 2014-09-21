#include "arm-macros.h"
TEST_BEGIN

mov r1, #0xc0000000
mov r2, #0xffffffff
umulls r3, r4, r1, r2 

TEST_END
