#include "arm-macros.h"
TEST_BEGIN

mov r4, #1
mov r5, #8
movs r4, r5, LSR #2

TEST_END
