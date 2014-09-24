#include "arm-macros.h"
TEST_BEGIN

mov r1, #1
mov r2, #0x80000000
mov r3, #0x70000000
subs r1, r1, r2
orrgts r1, r3

TEST_END
