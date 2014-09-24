#include "arm-macros.h"
TEST_BEGIN

mov r4, #0x80000000
cmp r4, #0x80000000
tstne r4, #0x80000000

TEST_END
