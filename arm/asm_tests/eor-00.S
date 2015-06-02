#include "arm-macros.h"
TEST_BEGIN

mov r4, #3
eor r5, r4, #0
eor r6, r4, #3
eor r7, r4, #2

TEST_END
