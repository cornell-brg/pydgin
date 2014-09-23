#include "arm-macros.h"
TEST_BEGIN

mov r4, #0
mov r5, #0
mov r6, #0
mov pc, pc
mov r4, pc
mov r5, pc
mov r6, pc

TEST_END
