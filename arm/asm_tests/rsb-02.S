#include "arm-macros.h"
TEST_BEGIN

mov r6, #0x28
mov r7, #0x00
rsbne r6, r7, r6

TEST_END
