#include "arm-macros.h"
TEST_BEGIN

mov r1, #1
mov r2, #8
cmp r2, #7
subeqs r1, r1, r2

TEST_END
