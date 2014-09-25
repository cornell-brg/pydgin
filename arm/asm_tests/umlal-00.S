#include "arm-macros.h"
TEST_BEGIN

mov r1, #2
mov r2, #0x80000000
mov r3, #0
mov r4, #0xffffffff
umlals r3, r4, r1, r2 

TEST_END
