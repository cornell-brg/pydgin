#include "arm-macros.h"
TEST_BEGIN

mov r5, #0
cmp r5, #0
movccs r4, #1

TEST_END
