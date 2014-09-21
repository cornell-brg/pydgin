#include "arm-macros.h"
TEST_BEGIN

mov r1, #0xFFFFFFF8
mov r2, #7
orrs r1, r2

TEST_END
