#include "arm-macros.h"
TEST_BEGIN

mov r1, #0xFFFFFFF8
mov r2, #7
cmp r2, #6
orrhis r1, r2

TEST_END
