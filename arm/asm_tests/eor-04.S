#include "arm-macros.h"
TEST_BEGIN

mov  r4, #3
mov  r3, #0x1B
eors r5, r4, r4, ROR #3

TEST_END
