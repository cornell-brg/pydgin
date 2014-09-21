#include "arm-macros.h"
TEST_BEGIN

#immediate rotation
mov r4, #0x3f0
cmp r4, #0x3f, 0x1c

TEST_END
