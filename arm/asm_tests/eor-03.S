#include "arm-macros.h"
TEST_BEGIN

mov  r4, #3
eors r5, r4, r4, ROR #1

TEST_END
