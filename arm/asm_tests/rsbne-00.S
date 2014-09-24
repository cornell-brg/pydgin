#include "arm-macros.h"
TEST_BEGIN

mov r1, #1
mov r2, #8
cmp r2, #7
rsbne r1, r2, r1

TEST_END
