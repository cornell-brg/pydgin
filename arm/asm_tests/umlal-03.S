#include "arm-macros.h"
TEST_BEGIN

mov r1, #0xc0000000
mov r2, #0xffffffff
mov r3, #0xc0000000
mov r4, #0x40000001
umlals r3, r4, r1, r2 

TEST_END
