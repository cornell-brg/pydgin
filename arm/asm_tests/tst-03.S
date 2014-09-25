#include "arm-macros.h"
TEST_BEGIN

mov r2, #0x7f000000
orr r2, #0x00e80000
orr r2, #0x00008600
orr r2, #0x000000c1
tst r2, #3

TEST_END
